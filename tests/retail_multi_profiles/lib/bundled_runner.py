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
    tickets = ticket_leg(
        q.question,
        ticket_source,
        model=pf.oem_model or q.model_id or None,
        brand=pf.brand,
        k=ctx.k_tickets,
    )
    ticket_hits = tickets.get("hits") or []

    lanes = load_lanes(ctx.repo)
    lane = lanes["B"]
    resolved = resolve_effective_profile(
        ctx.cfg,
        profile_id=ctx.manual_profile_id,
        lane_ids=["B"],
        retrieval_mode="raw_rag",
    )
    template = str(ctx.cfg.get("query_template") or "{model_id} {question}")
    query = template.format(model_id=q.model_id, question=q.question)
    top_k = ctx.k_manuals
    page_prefix = int(ctx.cfg.get("page_prefix_chars") or 8000)
    chunk_max = int(ctx.cfg.get("context_max_chars_per_chunk") or 2000)
    embed_cfg = (ctx.cfg.get("retail_raw_rag") or {}).get("embedding") or {}
    raw_cfg = ctx.cfg.get("retail_raw_rag") or {}

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
    _emit_progress(
        ctx,
        step="manual_retrieve_done",
        question_id=q.question_id,
        index=index,
        retrieval_ms=pkg.latency_ms,
    )

    context = build_bundled_context(
        ticket_hits,
        manual_hits,
        page_prefix_chars=page_prefix,
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
            page_prefix_chars=page_prefix,
            max_chars_per_chunk=chunk_max,
        ),
        "candidate_answer": candidate,
        "gold_answer": q.gold_answer,
        "answer_ms": answer_ms,
        "judge_ms": judge_ms,
        "manual_retrieval_ms": pkg.latency_ms,
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
