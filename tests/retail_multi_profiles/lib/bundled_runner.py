"""Run B20 bundled Q&A: Postgres tickets (mode C) + PG manual hybrid, judged like M90."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
RETAIL_PKG = REPO / "scripts" / "retail"
for p in (str(REPO), str(RETAIL_PKG)):
    if p not in sys.path:
        sys.path.insert(0, p)

from logging_utils.run_progress import (  # noqa: E402
    completed_row_keys,
    progress_row_key,
    write_jsonl_line,
)
from retail_brain.answer_tickets import PgTicketSource, load_issue_keys, ticket_leg  # noqa: E402
from retail_brain.bundle_context import (  # noqa: E402
    build_bundled_context,
    bundled_answer_prompt,
    format_manual_hits_for_context,
    format_ticket_hits_for_context,
)
from retail_brain.product_scope import resolve_product_scope  # noqa: E402
from retail_brain.query_unit_orchestrator import (  # noqa: E402
    DecomposedRetrievalTrace,
    UnitManualTrace,
    UnitTicketTrace,
    merge_ticket_hits_gated,
    select_manual_packet,
    pfda_pick_tickets,
    plan_query_units,
    should_run_decomposed,
)
from retail_brain.rerank import (  # noqa: E402
    MANUAL_RERANK_CANDIDATE_N,
    MANUAL_RERANK_CONTEXT_CHARS,
    MANUAL_RERANK_KEEP,
    rerank_manual_candidates,
)
from retail_brain.rerank_registry import build_rank_fn  # noqa: E402
from tests.retail_multi_profiles.lib.raw_policy import d7_query_mode  # noqa: E402
from retail_brain.sim_data_profile import resolve_sim_data_profile  # noqa: E402
from utils.neat_logger.neat_logger_instance import NeatLoggerFactory  # noqa: E402

from .eval_models import resolve_eval_llms  # noqa: E402
from .lanes import load_lanes  # noqa: E402
from .load_bundled_suite import BundledQuestion, iter_bundled_questions, load_bundled_suite  # noqa: E402
from .manual_raw_pipeline import build_manual_raw_pipeline  # noqa: E402
from .resolved_run_profile import resolve_effective_profile  # noqa: E402
from .run_config import load_merged_run_config  # noqa: E402
from .scoring import score_judged  # noqa: E402
from .llm_generate import llm_generate  # noqa: E402


def _git_head(repo: Path) -> str:
    """Best-effort commit hash for run metadata."""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except Exception:
        return ""


def _bundled_logger(run_id: str):
    """Operator tee for bundled harness."""
    safe = run_id.replace("/", "_")
    return NeatLoggerFactory.create(
        "OPS",
        "RETAIL_BUNDLED_QA",
        log_file_name=f"retail-bundled-qa-{safe}.log",
        log_output="both",
    )


@dataclass
class BundledRunContext:
    """Shared state for one bundled benchmark run."""

    repo: Path
    run_id: str
    cfg: dict[str, Any]
    results_path: Path
    progress_path: Path
    log: Any
    k_tickets: int
    k_manuals: int
    manual_profile_id: str


def _emit_progress(ctx: BundledRunContext, **fields: Any) -> None:
    """Append one JSONL progress line."""
    row = {"ts": datetime.now(timezone.utc).isoformat(), "run_id": ctx.run_id, **fields}
    write_jsonl_line(ctx.progress_path, row)


def _ticket_in_packet(hits: list[dict[str, Any]], expected_id: str) -> bool:
    """True when the gold ticket id appears in the top-k ticket hits."""
    if not expected_id:
        return False
    return any(str(h.get("ticket_id")) == expected_id for h in hits)


def run_one_bundled_row(ctx: BundledRunContext, q: BundledQuestion, *, index: int) -> dict[str, Any]:
    """Retrieve both legs, answer, judge, and return one results.jsonl row."""
    dsn = os.environ.get("RETAIL_DATABASE_URL")
    if not dsn:
        raise RuntimeError("RETAIL_DATABASE_URL required for bundled Q&A")

    os.environ.setdefault("RETAIL_TICKET_SEARCH_MODE", "rrf_term_boosted")

    sim = resolve_sim_data_profile()
    issue_keys = (
        load_issue_keys(sim.ticket_manifest_jsonl)
        if sim.ticket_manifest_jsonl.is_file()
        else {}
    )
    ticket_source = PgTicketSource(dsn, issue_keys)
    product = resolve_product_scope(
        q.question,
        suite_model=q.model_id,
        manual_anchor_question_id=q.manual_anchor_question_id,
    )
    pf = product.ticket_filter
    lanes = load_lanes(ctx.repo)
    lane = lanes["B"]
    resolved = resolve_effective_profile(
        ctx.cfg,
        profile_id=ctx.manual_profile_id,
        lane_ids=["B"],
        retrieval_mode="raw_rag",
    )
    template = str(ctx.cfg.get("query_template") or "{model_id} {question}")
    top_k = ctx.k_manuals
    page_prefix = int(ctx.cfg.get("page_prefix_chars") or 8000)
    chunk_max = int(ctx.cfg.get("context_max_chars_per_chunk") or 2000)
    embed_cfg = (ctx.cfg.get("retail_raw_rag") or {}).get("embedding") or {}
    raw_cfg = ctx.cfg.get("retail_raw_rag") or {}

    d7_trace: DecomposedRetrievalTrace | None = None
    units = plan_query_units(q.question)
    use_d7 = d7_query_mode() == "decompose" and should_run_decomposed(units)
    manual_rerank = (q.manual_rerank or "").strip().lower()
    probe_rank_fn = None
    probe_model = ""
    if manual_rerank == "llm_listwise":
        answer_llm_probe, _ = resolve_eval_llms(ctx.cfg)
        probe_model = answer_llm_probe.model
        probe_rank_fn = build_rank_fn(
            "llm_listwise",
            llm_cfg={
                "provider": answer_llm_probe.provider,
                "model": answer_llm_probe.model,
                "temperature": answer_llm_probe.temperature,
            },
        )
    elif manual_rerank == "cross_encoder":
        from retail_brain.rerank import CROSS_ENCODER_MODEL

        probe_model = CROSS_ENCODER_MODEL
    rerank_ms_total = 0

    _emit_progress(ctx, step="manual_retrieve_start", question_id=q.question_id, index=index)
    pipeline = build_manual_raw_pipeline(
        lane,
        resolved,
        embed_cfg=embed_cfg,
        top_k=top_k,
        page_prefix_chars=page_prefix,
        max_chars_per_chunk=chunk_max,
        raw_rag_cfg=raw_cfg,
        answer_llm_cfg=ctx.cfg.get("answer") or {},
    )

    if use_d7:
        from retail_brain.query_unit_orchestrator import d7_min_ticket_cosine

        d7_trace = DecomposedRetrievalTrace(
            enabled=True,
            units=units,
            min_ticket_cosine=d7_min_ticket_cosine(),
        )
        ticket_unit_hits: list[list[dict[str, Any]]] = []
        manual_unit_rows: list[list[dict[str, Any]]] = []
        manual_ms_total = 0
        ticket_mode = "rrf_term_boosted"

        for ui, unit in enumerate(units):
            tickets = ticket_leg(
                unit,
                ticket_source,
                model=pf.oem_model or q.model_id or None,
                brand=pf.brand,
                k=ctx.k_tickets,
            )
            ticket_mode = str(tickets.get("search_mode") or ticket_mode)
            thits = list(tickets.get("hits") or [])
            floor = d7_min_ticket_cosine()
            kept_ids: list[str] = []
            for h in thits:
                if float(h.get("cosine_similarity") or 0.0) < floor:
                    continue
                tid = str(h.get("ticket_id") or "")
                if tid and tid not in kept_ids:
                    kept_ids.append(tid)
                if len(kept_ids) >= ctx.k_tickets:
                    break
            d7_trace.ticket_units.append(
                UnitTicketTrace(unit_index=ui, query=unit, hits=thits, kept_ticket_ids=kept_ids)
            )
            ticket_unit_hits.append(thits)

            retrieve_q = template.format(model_id=q.model_id, question=unit)
            saved_top_k = pipeline.retriever.top_k
            if manual_rerank:
                pipeline.retriever.top_k = MANUAL_RERANK_CANDIDATE_N
            try:
                pkg = pipeline.retriever.retrieve(
                    retrieve_q,
                    model_id=q.model_id,
                    product_filter=product.manual_filter,
                    skip_index_check=True,
                )
            finally:
                pipeline.retriever.top_k = saved_top_k
            manual_ms_total += int(pkg.latency_ms or 0)
            rows = [
                {
                    "source_relpath": c.source_relpath,
                    "text": c.text,
                    "chunk_id": c.chunk_id,
                }
                for c in pkg.chunks
            ]
            rerank_meta: dict[str, Any] = {}
            if manual_rerank:
                rows, rerank_meta = rerank_manual_candidates(
                    retrieve_q,
                    rows,
                    backend=manual_rerank,
                    keep=MANUAL_RERANK_KEEP,
                    rank_fn=probe_rank_fn,
                    model_id=probe_model,
                )
                rerank_ms_total += int(rerank_meta["rerank_ms"])
                ctx.log.info(
                    f"manual_rerank {q.question_id} unit {ui} "
                    f"backend={manual_rerank} candidates={rerank_meta['candidate_count']} "
                    f"rerank_ms={rerank_meta['rerank_ms']}"
                )
            manual_unit_rows.append(rows)
            d7_trace.manual_units.append(
                UnitManualTrace(
                    unit_index=ui,
                    customer_unit=unit,
                    retrieve_query=retrieve_q,
                    chunk_ids=[str(r["chunk_id"]) for r in rows],
                    latency_ms=int(pkg.latency_ms or 0),
                    rerank_backend=str(rerank_meta.get("rerank_backend") or ""),
                    rerank_model=str(rerank_meta.get("rerank_model") or ""),
                    candidate_count=int(rerank_meta.get("candidate_count") or 0),
                    rerank_ms=int(rerank_meta.get("rerank_ms") or 0),
                    pre_rerank_chunk_ids=list(rerank_meta.get("pre_rerank_chunk_ids") or []),
                    post_rerank_chunk_ids=list(rerank_meta.get("post_rerank_chunk_ids") or []),
                )
            )

        decomposed_ticket_hits = merge_ticket_hits_gated(
            ticket_unit_hits, k_per_unit=ctx.k_tickets
        )
        anchor_pkg = ticket_leg(
            q.question,
            ticket_source,
            model=pf.oem_model or q.model_id or None,
            brand=pf.brand,
            k=ctx.k_tickets,
        )
        anchor_hits = list(anchor_pkg.get("hits") or [])
        answer_llm, _ = resolve_eval_llms(ctx.cfg)
        pfda_llm_cfg = {
            "provider": answer_llm.provider,
            "model": answer_llm.model,
            "temperature": answer_llm.temperature,
        }
        pfda_rank_fn = build_rank_fn("llm_listwise", llm_cfg=pfda_llm_cfg)
        ticket_hits, pfda_trace = pfda_pick_tickets(
            q.question,
            decomposed_hits=decomposed_ticket_hits,
            anchor_hits=anchor_hits,
            k=ctx.k_tickets,
            rank_fn=pfda_rank_fn,
        )
        d7_trace.d7_version = "v3"
        d7_trace.pfda = pfda_trace
        tickets = {"search_mode": ticket_mode, "hits": ticket_hits}
        merged_manual = select_manual_packet(
            manual_unit_rows, manual_rerank=manual_rerank, top_k=top_k
        )
        manual_hits = [
            {
                "source_relpath": r.get("source_relpath"),
                "text": r.get("text"),
                "chunk_id": r.get("chunk_id"),
            }
            for r in merged_manual
        ]
        d7_trace.merged_ticket_ids = [
            str(h.get("ticket_id") or "") for h in decomposed_ticket_hits
        ]
        d7_trace.merged_manual_chunk_ids = [str(h.get("chunk_id") or "") for h in manual_hits]
        manual_retrieval_ms = manual_ms_total
    else:
        query = template.format(model_id=q.model_id, question=q.question)
        tickets = ticket_leg(
            q.question,
            ticket_source,
            model=pf.oem_model or q.model_id or None,
            brand=pf.brand,
            k=ctx.k_tickets,
        )
        ticket_hits = tickets.get("hits") or []
        pkg = pipeline.retriever.retrieve(
            query,
            model_id=q.model_id,
            product_filter=product.manual_filter,
            skip_index_check=True,
        )
        manual_hits = [
            {
                "source_relpath": c.source_relpath,
                "text": c.text,
                "chunk_id": c.chunk_id,
            }
            for c in pkg.chunks
        ]
        manual_retrieval_ms = int(pkg.latency_ms or 0)

    _emit_progress(
        ctx,
        step="manual_retrieve_done",
        question_id=q.question_id,
        index=index,
        retrieval_ms=manual_retrieval_ms,
        rerank_backend=manual_rerank or None,
        rerank_ms=rerank_ms_total,
        candidate_count=MANUAL_RERANK_CANDIDATE_N if manual_rerank else top_k,
    )

    manual_budget = MANUAL_RERANK_CONTEXT_CHARS if manual_rerank else page_prefix
    context = build_bundled_context(
        ticket_hits,
        manual_hits,
        page_prefix_chars=manual_budget,
        max_chars_per_chunk=chunk_max,
    )
    literal = str(ctx.cfg.get("insufficient_literal") or "Insufficient_Information_Based_On_Given_PDF")
    prompt = bundled_answer_prompt(q.question, context, insufficient_literal=literal)

    answer_llm, judge_llm = resolve_eval_llms(ctx.cfg)
    _emit_progress(ctx, step="answer_start", question_id=q.question_id, index=index)
    t0 = time.perf_counter()
    candidate = llm_generate(
        prompt,
        provider=answer_llm.provider,
        model=answer_llm.model,
        temperature=answer_llm.temperature,
    ).strip()
    answer_ms = int((time.perf_counter() - t0) * 1000)
    _emit_progress(ctx, step="answer_done", question_id=q.question_id, index=index, answer_ms=answer_ms)

    _emit_progress(ctx, step="judge_start", question_id=q.question_id, index=index)
    t_j = time.perf_counter()
    passed, rationale = score_judged(
        q.question,
        q.gold_answer,
        candidate,
        provider=judge_llm.provider,
        model=judge_llm.model,
        temperature=judge_llm.temperature,
    )
    judge_ms = int((time.perf_counter() - t_j) * 1000)
    _emit_progress(ctx, step="judge_done", question_id=q.question_id, index=index, judge_ms=judge_ms)

    expected = q.expected_ticket_ids[0] if q.expected_ticket_ids else ""
    ticket_hit = _ticket_in_packet(ticket_hits, expected)

    return {
        "question_id": q.question_id,
        "difficulty": q.difficulty,
        "model_id": q.model_id,
        "pass": passed,
        "judge_rationale": rationale,
        "ticket_search_mode": tickets.get("search_mode"),
        "ticket_hit_in_packet": ticket_hit,
        "expected_ticket_id": expected,
        # Narrative source row (may be open); retrieval scored against expected_ticket_id only.
        "provenance_ticket_ids": list(q.provenance_ticket_ids)
        if q.provenance_ticket_ids
        else None,
        "ticket_ids_returned": [h.get("ticket_id") for h in ticket_hits],
        "manual_profile_id": ctx.manual_profile_id,
        "manual_lane_id": "B",
        "manual_lane_path": str(lane.project_path),
        "product_scope": product.to_metadata(),
        "manual_filter_brand": pf.brand,
        "manual_filter_oem_model": pf.oem_model,
        "manual_chunk_count": len(manual_hits),
        "ticket_leg_context": format_ticket_hits_for_context(ticket_hits),
        "manual_leg_context": format_manual_hits_for_context(
            manual_hits,
            page_prefix_chars=manual_budget,
            max_chars_per_chunk=chunk_max,
        ),
        "candidate_answer": candidate,
        "gold_answer": q.gold_answer,
        "answer_ms": answer_ms,
        "judge_ms": judge_ms,
        "manual_retrieval_ms": manual_retrieval_ms,
        **({"d7_trace": d7_trace.to_dict()} if d7_trace is not None else {}),
    }


def run_bundled_benchmark(
    repo: Path,
    *,
    questions: list[BundledQuestion],
    run_id: str | None = None,
    resume: bool = False,
    manual_profile_id: str = "MANUAL_B_RAW_PG_HYBRID",
) -> Path:
    """Execute bundled rows and write ops/runs/retail-bundled-qa/<run_id>/results.jsonl."""
    from utils.retail_fru.env import load_repo_env

    load_repo_env(repo)
    rid = run_id or datetime.now(timezone.utc).strftime("bundled-%Y%m%d-%H%M%S")
    out_dir = repo / "ops" / "runs" / "retail-bundled-qa" / rid
    out_dir.mkdir(parents=True, exist_ok=True)
    results_path = out_dir / "results.jsonl"
    progress_path = out_dir / "progress.jsonl"
    log = _bundled_logger(rid)
    cfg = load_merged_run_config(repo)
    k_tickets = int(cfg.get("k_tickets") or 2)
    k_manuals = int(cfg.get("k_manuals") or cfg.get("search_top_k") or 5)

    ctx = BundledRunContext(
        repo=repo,
        run_id=rid,
        cfg=cfg,
        results_path=results_path,
        progress_path=progress_path,
        log=log,
        k_tickets=k_tickets,
        k_manuals=k_manuals,
        manual_profile_id=manual_profile_id,
    )

    meta = {
        "run_id": rid,
        "git_head": _git_head(repo),
        "k_tickets": k_tickets,
        "k_manuals": k_manuals,
        "manual_profile_id": manual_profile_id,
        "ticket_search_mode": "rrf_term_boosted",
        "question_count": len(questions),
    }
    (out_dir / "run_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    done = completed_row_keys(results_path) if resume and results_path.is_file() else set()

    for index, q in enumerate(questions):
        key = progress_row_key("bundled", q.question_id)
        if key in done:
            continue
        log.info(f"row {index + 1}/{len(questions)} {q.question_id}")
        _emit_progress(ctx, step="row_start", question_id=q.question_id, index=index)
        try:
            row = run_one_bundled_row(ctx, q, index=index)
            row["run_id"] = rid
            row["lane"] = "bundled"
            write_jsonl_line(results_path, {"type": "result", "row": row})
            _emit_progress(
                ctx,
                step="row_done",
                question_id=q.question_id,
                index=index,
                judge_pass=row.get("pass"),
                ticket_hit_in_packet=row.get("ticket_hit_in_packet"),
            )
        except Exception as exc:  # noqa: BLE001
            log.error(f"row_error {q.question_id}: {exc}\n{traceback.format_exc()}")
            _emit_progress(
                ctx,
                step="row_error",
                question_id=q.question_id,
                index=index,
                error=f"{type(exc).__name__}: {exc}",
            )
            raise

    return results_path


def load_default_suite(repo: Path) -> dict[str, Any]:
    """Load B20 JSON from the standard data path."""
    path = repo / "tests" / "retail_multi_profiles" / "data" / "retail-bundled-qa-b20.json"
    return load_bundled_suite(path)
