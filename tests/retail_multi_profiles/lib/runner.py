"""Run benchmark rows across lanes with JSONL checkpoint and operator logging."""

from __future__ import annotations

import json
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
    iter_result_rows,
    last_progress_event,
    progress_row_key,
    write_jsonl_line,
)
from retail_brain.answer_manuals import LlmWikiHttpClient
from utils.neat_logger.neat_logger_instance import NeatLogger, NeatLoggerFactory

from .answer_pipeline import answer_from_context, retrieve_context, scoped_query
from retail_brain.evidence.verifier import verify_manual_coverage

from .manual_raw_pipeline import build_manual_raw_pipeline
from .resolved_run_profile import ResolvedRunProfile
from retail_brain.manual_pg_ingest import ensure_manual_pg_fresh  # noqa: E402

from .raw_rag_context import concat_top_k_raw_chunks
from .sku_scope import SkuScopeError, resolve_retrieval_sku, sku_scope_to_dict
from .eval_models import resolve_eval_llms
from .lanes import Lane, load_lanes
from .load_suite import SuiteQuestion, filter_question_ids, iter_questions, load_suite
from .run_config import load_merged_run_config
from .scoring import score_judged, score_negative
from .search_hits import compact_search_hits


def _git_head(repo: Path) -> str:
    """Best-effort git commit for run metadata."""
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


def _ops_logger(run_id: str, *, retrieval_mode: str = "llm_wiki") -> NeatLogger:
    """Per-run tee under logs/ops for tail -f during long benchmarks."""
    safe = run_id.replace("/", "_")
    if retrieval_mode == "raw_rag":
        return NeatLoggerFactory.create(
            "OPS",
            "RETAIL_RAW_RAG",
            log_file_name=f"retail-lane-abcd-raw-{safe}.log",
            log_output="both",
        )
    return NeatLoggerFactory.create(
        "OPS",
        "RETAIL_ABCD",
        log_file_name=f"retail-lane-abcd-{safe}.log",
        log_output="both",
    )


@dataclass
class _RunContext:
    """Mutable benchmark run state (checkpoint + operator log)."""

    repo_root: Path
    out_dir: Path
    jsonl_path: Path
    run_id: str
    kind: str
    lane_ids: list[str]
    cfg: dict[str, Any]
    log: NeatLogger
    completed: set[str]
    total_planned: int
    retrieval_mode: str
    raw_retrieval: str
    raw_agentic: bool
    force_reindex: bool
    skip_index_check: bool
    resolved: ResolvedRunProfile | None
    profile_id: str


def _emit_progress(ctx: _RunContext, **fields: Any) -> None:
    """Write one progress event to JSONL and neat_logger."""
    rec = {"type": "progress", **fields}
    write_jsonl_line(ctx.jsonl_path, rec)
    step = fields.get("step", "?")
    lane = fields.get("lane", "?")
    qid = fields.get("question_id", "?")
    idx = fields.get("index", "?")
    ctx.log.info(f"[{idx}/{ctx.total_planned}] {lane} {qid} — {step}")


def _flush_results_json(ctx: _RunContext, questions: list[SuiteQuestion]) -> None:
    """Rebuild results.json from checkpoint JSONL (safe after each row)."""
    rows = list(iter_result_rows(ctx.jsonl_path))
    payload = {
        "schema_version": "1.0",
        "run_id": ctx.run_id,
        "kind": ctx.kind,
        "git_head": _git_head(ctx.repo_root),
        "question_count": len(questions),
        "lane_ids": ctx.lane_ids,
        "config_snapshot": ctx.cfg,
        "rows_complete": len(rows),
        "rows_planned": ctx.total_planned,
        "rows": rows,
    }
    (ctx.out_dir / "results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _fallback_resolved(ctx: _RunContext) -> ResolvedRunProfile:
    """Legacy raw_rag when ResolvedRunProfile was not built (tests/direct runner calls only).

    Normal CLI: __main__ applies run-config default_run_profile when --profile is omitted.
    """
    d3 = ctx.raw_retrieval or str(
        ((ctx.cfg.get("retail_raw_rag") or {}).get("retrieval") or {}).get("default_mode") or "vector"
    )
    if d3 == "hybrid_rrf_rerank":
        d3 = "hybrid_rrf"
    return ResolvedRunProfile(
        profile_id=ctx.profile_id or "cli",
        retrieval_mode=ctx.retrieval_mode,
        d3_engine=d3,
        lane_ids=list(ctx.lane_ids),
        d5_rerank_enabled=ctx.raw_retrieval == "hybrid_rrf_rerank",
        d5_verifier_enabled=ctx.raw_agentic,
        d5_agentic_enabled=ctx.raw_agentic,
    )


def _run_one_row(
    ctx: _RunContext,
    *,
    lane: Lane,
    q: SuiteQuestion,
    wiki: LlmWikiHttpClient | None,
    index: int,
    answer_llm: Any,
    judge_llm: Any,
    literal: str,
    top_k: int,
    page_prefix: int,
    chunk_max_per: int,
    template: str,
) -> None:
    """Execute one lane × question with step progress (pinpoints timeouts)."""
    key = progress_row_key(lane.lane_id, q.question_id)
    if key in ctx.completed:
        ctx.log.info(f"skip completed {key}")
        return

    query = scoped_query(template, model_id=q.model_id, question=q.question)
    from retail_brain.product_scope import resolve_product_scope

    product_scope = resolve_product_scope(query, suite_model=q.model_id or None)
    retrieval_product = product_scope.manual_filter
    retrieval_filter_id = product_scope.ingest_key or q.model_id or ""
    _emit_progress(
        ctx,
        step="row_start",
        lane=lane.lane_id,
        question_id=q.question_id,
        difficulty=q.difficulty,
        index=index,
    )

    try:
        _emit_progress(ctx, step="retrieve_start", lane=lane.lane_id, question_id=q.question_id, index=index)
        ctx.log.debug(
            f"retrieve query={query[:120]!r} top_k={top_k} page_prefix_chars={page_prefix}"
        )
        verifier_summary: dict[str, Any] | None = None
        agentic_meta: dict[str, Any] | None = None
        context = ""
        retrieval_ms = 0
        hits: list[dict[str, Any]] = []
        if ctx.retrieval_mode == "raw_rag":
            embed_cfg = (ctx.cfg.get("retail_raw_rag") or {}).get("embedding") or {}
            raw_cfg = ctx.cfg.get("retail_raw_rag") or {}
            resolved = ctx.resolved or _fallback_resolved(ctx)
            mode = resolved.d3_engine
            _emit_progress(
                ctx,
                step="raw_search_start",
                lane=lane.lane_id,
                question_id=q.question_id,
                index=index,
                raw_mode=mode,
                profile_id=resolved.profile_id,
            )
            answer_cfg = ctx.cfg.get("answer") or {}
            pipeline = build_manual_raw_pipeline(
                lane,
                resolved,
                embed_cfg=embed_cfg,
                top_k=top_k,
                page_prefix_chars=page_prefix,
                max_chars_per_chunk=chunk_max_per,
                raw_rag_cfg=raw_cfg,
                answer_llm_cfg=answer_cfg,
            )
            if pipeline.rank_fn_active:
                _emit_progress(ctx, step="rerank_start", lane=lane.lane_id, question_id=q.question_id, index=index)
            if pipeline.agentic is not None:
                agent_out = pipeline.agentic.retrieve_with_verifier(
                    query,
                    q.question,
                    model_id=q.model_id or retrieval_filter_id,
                    force_reindex=ctx.force_reindex,
                    skip_index_check=ctx.skip_index_check,
                )
                pkg = agent_out.package
                verifier_summary = agent_out.verifier.to_dict()
                agentic_meta = {
                    "subquery_used": agent_out.subquery_used,
                    "loops": agent_out.loops,
                }
            else:
                pkg = pipeline.retriever.retrieve(
                    query,
                    model_id=q.model_id or retrieval_filter_id,
                    product_filter=retrieval_product,
                    force_reindex=ctx.force_reindex,
                    skip_index_check=ctx.skip_index_check,
                )
                if resolved.d5_verifier_enabled:
                    verifier_summary = verify_manual_coverage(pkg, q.question).to_dict()
            if pipeline.rank_fn_active:
                _emit_progress(ctx, step="rerank_done", lane=lane.lane_id, question_id=q.question_id, index=index)
            if verifier_summary is not None:
                _emit_progress(
                    ctx,
                    step="verifier_done",
                    lane=lane.lane_id,
                    question_id=q.question_id,
                    index=index,
                    sufficient=verifier_summary.get("sufficient"),
                )
            retrieval_ms = pkg.latency_ms
            hits = [
                {
                    "chunk_id": c.chunk_id,
                    "source_relpath": c.source_relpath,
                    "model_id": c.model_id,
                    "text": c.text,
                    **c.scores,
                }
                for c in pkg.chunks
            ]
            if not context:
                context = concat_top_k_raw_chunks(
                    hits,
                    page_prefix_chars=page_prefix,
                    max_chars_per_chunk=chunk_max_per,
                )
            _emit_progress(
                ctx,
                step="raw_search_done",
                lane=lane.lane_id,
                question_id=q.question_id,
                index=index,
                retrieval_ms=retrieval_ms,
            )
        else:
            if wiki is None:
                raise RuntimeError("wiki client required for llm_wiki retrieval_mode")
            hits, context, retrieval_ms = retrieve_context(
                wiki,
                query,
                top_k=top_k,
                page_prefix_chars=page_prefix,
                wiki_evidence=ctx.cfg.get("wiki_evidence"),
            )
            wiki_answer = ctx.cfg.get("wiki_answer") or {}
            from tests.retail_multi_profiles.lib.wiki_uncertainty import uncertainty_label_for_hits

            brain_rel = Path(str(lane.brain_relpath or "brain/retail-md"))
            registry = (ctx.repo_root / brain_rel / ".wiki-claim-audit" / "claims.jsonl").resolve()
            paths = [str(h.get("path") or "") for h in hits]
            unc = uncertainty_label_for_hits(
                paths,
                registry_path=registry,
                enabled=bool(wiki_answer.get("uncertainty_enabled", True)),
            )
            setattr(ctx, "wiki_preamble", unc or "")
        ctx.log.debug(
            f"retrieve done paths={hits[:3]!r} context_chars={len(context)} ms={retrieval_ms}"
        )
        _emit_progress(
            ctx,
            step="retrieve_done",
            lane=lane.lane_id,
            question_id=q.question_id,
            index=index,
            retrieval_ms=retrieval_ms,
        )

        ctx.log.debug(
            f"answer LLM provider={answer_llm.provider} model={answer_llm.model}"
        )
        with ctx.log.heartbeat(f"{lane.lane_id} {q.question_id} answer LLM"):
            wiki_answer = ctx.cfg.get("wiki_answer") or {}
            pre = str(getattr(ctx, "wiki_preamble", "") or "")
            prov_label = str(wiki_answer.get("provisional_label") or "").strip()
            if ctx.retrieval_mode == "llm_wiki" and prov_label:
                pre = f"{prov_label}\n{pre}".strip()
            candidate, answer_ms = answer_from_context(
                q.question,
                context,
                provider=answer_llm.provider,
                model=answer_llm.model,
                temperature=answer_llm.temperature,
                preamble=pre,
                insight_mode=ctx.retrieval_mode == "llm_wiki" and bool(prov_label),
            )
        _emit_progress(
            ctx,
            step="answer_done",
            lane=lane.lane_id,
            question_id=q.question_id,
            index=index,
            answer_ms=answer_ms,
        )

        judge_ms = 0
        if q.difficulty == "negative":
            passed, rationale = score_negative(candidate, literal=literal)
        else:
            _emit_progress(
                ctx,
                step="judge_start",
                lane=lane.lane_id,
                question_id=q.question_id,
                index=index,
                judge_provider=judge_llm.provider,
                judge_model=judge_llm.model,
            )
            ctx.log.debug(
                f"judge LLM provider={judge_llm.provider} model={judge_llm.model} "
                f"candidate_chars={len(candidate)} gold_chars={len(q.gold_answer)}"
            )
            t_j = time.perf_counter()
            with ctx.log.heartbeat(f"{lane.lane_id} {q.question_id} judge LLM"):
                passed, rationale = score_judged(
                    q.question,
                    q.gold_answer,
                    candidate,
                    provider=judge_llm.provider,
                    model=judge_llm.model,
                    temperature=judge_llm.temperature,
                )
            judge_ms = int((time.perf_counter() - t_j) * 1000)
            _emit_progress(
                ctx,
                step="judge_done",
                lane=lane.lane_id,
                question_id=q.question_id,
                index=index,
                judge_ms=judge_ms,
            )

        if ctx.retrieval_mode == "raw_rag":
            top_paths = [h.get("source_relpath") for h in hits[:top_k]]
            top_hits = [
                {
                    "source_relpath": h.get("source_relpath"),
                    "distance": h.get("distance"),
                    "vector_score": h.get("vector_score"),
                    "chunk_id": h.get("chunk_id"),
                }
                for h in hits[:top_k]
            ]
            resolved = ctx.resolved or _fallback_resolved(ctx)
            search_meta = {
                "mode": f"raw_rag_{resolved.d3_engine}",
                "resolved_d5": (resolved.to_dict().get("d5") or {}),
                "product_scope": product_scope.to_metadata(),
                "sku_scope": product_scope.to_metadata(),
                "context_max_chars_per_chunk": chunk_max_per,
            }
            if verifier_summary is not None:
                search_meta["verifier"] = verifier_summary
            if agentic_meta is not None:
                search_meta["agentic"] = agentic_meta
        else:
            top_paths = [h.get("path") for h in hits[:top_k]]
            top_hits = compact_search_hits(hits[:top_k])
            search_meta = dict(getattr(wiki, "last_search_meta", {}) or {})

        row = {
            "lane": lane.lane_id,
            "ingest_kind": lane.ingest_kind,
            "project_path": str(lane.project_path),
            "question_id": q.question_id,
            "model_id": q.model_id,
            "difficulty": q.difficulty,
            "query": query,
            "retrieval_mode": ctx.retrieval_mode,
            "search_meta": search_meta,
            "top_paths": top_paths,
            "top_hits": top_hits,
            "candidate_answer": candidate,
            "pass": passed,
            "judge_rationale": rationale,
            "latency_ms": {
                "retrieval": retrieval_ms,
                "answer": answer_ms,
                "judge": judge_ms,
            },
        }
        write_jsonl_line(ctx.jsonl_path, {"type": "result", "row": row})
        ctx.completed.add(key)
        _emit_progress(
            ctx,
            step="row_done",
            lane=lane.lane_id,
            question_id=q.question_id,
            index=index,
            passed=passed,
        )
    except SkuScopeError as e:
        _emit_progress(
            ctx,
            step="row_error",
            lane=lane.lane_id,
            question_id=q.question_id,
            index=index,
            error=f"{type(e).__name__}: {e}",
        )
        ctx.log.error(f"sku scope rejected {key}: {e}")
        row = {
            "lane": lane.lane_id,
            "ingest_kind": lane.ingest_kind,
            "project_path": str(lane.project_path),
            "question_id": q.question_id,
            "model_id": q.model_id,
            "difficulty": q.difficulty,
            "query": query,
            "retrieval_mode": ctx.retrieval_mode,
            "search_meta": {"sku_scope_error": str(e), "code": e.code},
            "top_paths": [],
            "top_hits": [],
            "candidate_answer": "",
            "pass": False,
            "judge_rationale": f"sku_scope_rejected: {e}",
            "latency_ms": {"retrieval": 0, "answer": 0, "judge": 0},
        }
        write_jsonl_line(ctx.jsonl_path, {"type": "result", "row": row})
        ctx.completed.add(key)
        _emit_progress(
            ctx,
            step="row_done",
            lane=lane.lane_id,
            question_id=q.question_id,
            index=index,
            passed=False,
        )
    except Exception as e:
        _emit_progress(
            ctx,
            step="row_error",
            lane=lane.lane_id,
            question_id=q.question_id,
            index=index,
            error=f"{type(e).__name__}: {e}",
        )
        ctx.log.error(f"failed {key}: {type(e).__name__}: {e}")
        ctx.log.error(traceback.format_exc().splitlines()[-1])
        raise


def _run_rows(ctx: _RunContext, *, lanes: list[Lane], questions: list[SuiteQuestion]) -> None:
    """Execute retrieval → answer → score for each lane × question."""
    cfg = ctx.cfg
    literal = str(cfg.get("insufficient_literal") or "")
    top_k = int(cfg.get("search_top_k") or 5)
    page_prefix = int(cfg.get("page_prefix_chars") or 8000)
    chunk_max_per = int(cfg.get("context_max_chars_per_chunk") or 0)
    template = str(cfg.get("query_template") or "{model_id} {question}")
    answer_llm, judge_llm = resolve_eval_llms(cfg)

    embed_cfg = (cfg.get("retail_raw_rag") or {}).get("embedding") or {}
    index = 0
    for lane in lanes:
        wiki: LlmWikiHttpClient | None = None
        if ctx.retrieval_mode == "raw_rag":
            if not lane.raw_rag_enabled:
                raise ValueError(f"lane {lane.lane_id} is not raw_rag_enabled")
            _emit_progress(
                ctx,
                step="index_preflight_start",
                lane=lane.lane_id,
                question_id="*",
                index=index,
            )
            with ctx.log.heartbeat(f"{lane.lane_id} manual PG preflight"):
                import os

                dsn = os.environ.get("RETAIL_DATABASE_URL")
                if not dsn:
                    raise RuntimeError(
                        "raw_rag manual lanes require RETAIL_DATABASE_URL"
                    )
                ensure_manual_pg_fresh(
                    dsn,
                    lane,
                    embed_cfg,
                    force=ctx.force_reindex,
                    skip_check=ctx.skip_index_check,
                )
            _emit_progress(
                ctx,
                step="index_preflight_done",
                lane=lane.lane_id,
                question_id="*",
                index=index,
            )
        else:
            wiki = LlmWikiHttpClient(str(lane.project_path), timeout=120.0)
        for q in questions:
            index += 1
            _run_one_row(
                ctx,
                lane=lane,
                q=q,
                wiki=wiki,
                index=index,
                answer_llm=answer_llm,
                judge_llm=judge_llm,
                literal=literal,
                top_k=top_k,
                page_prefix=page_prefix,
                chunk_max_per=chunk_max_per,
                template=template,
            )
            _flush_results_json(ctx, questions)
            time.sleep(0.3)


def run_benchmark(
    repo_root: Path,
    *,
    lane_ids: list[str],
    questions: list[SuiteQuestion],
    kind: str,
    run_id: str | None = None,
    resume: bool = False,
    retrieval_mode: str = "llm_wiki",
    raw_retrieval: str = "",
    raw_agentic: bool = False,
    force_reindex: bool = False,
    skip_index_check: bool = False,
    profile_id: str = "",
    resolved: ResolvedRunProfile | None = None,
) -> Path:
    """Run selected questions on lanes; checkpoint JSONL + incremental results.json."""
    cfg = load_merged_run_config(repo_root)
    if resolved is not None:
        cfg = dict(cfg)
        cfg["resolved_profile"] = resolved.to_dict()
    lanes_map = load_lanes(repo_root)
    selected = [lanes_map[lid] for lid in lane_ids]

    rid = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    runs_root = (
        "retail-lane-abcd-raw"
        if retrieval_mode == "raw_rag"
        else "retail-lane-abcd"
    )
    out_dir = repo_root / "ops" / "runs" / runs_root / rid
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "results.jsonl"
    log = _ops_logger(rid, retrieval_mode=retrieval_mode)

    completed = completed_row_keys(jsonl_path) if resume else set()
    if resume and completed:
        log.info(f"resume: skipping {len(completed)} completed row(s)")
        prev = last_progress_event(jsonl_path)
        if prev:
            log.info(
                f"last progress before resume: {prev.get('step')} "
                f"{prev.get('lane')} {prev.get('question_id')}"
            )

    total_planned = len(questions) * len(selected)
    ctx = _RunContext(
        repo_root=repo_root,
        out_dir=out_dir,
        jsonl_path=jsonl_path,
        run_id=rid,
        kind=kind,
        lane_ids=lane_ids,
        cfg=cfg,
        log=log,
        completed=completed,
        total_planned=total_planned,
        retrieval_mode=retrieval_mode,
        raw_retrieval=raw_retrieval,
        raw_agentic=raw_agentic,
        force_reindex=force_reindex,
        skip_index_check=skip_index_check,
        resolved=resolved,
        profile_id=profile_id,
    )

    if retrieval_mode == "raw_rag" and resolved is not None and selected:
        build_manual_raw_pipeline(
            selected[0],
            resolved,
            embed_cfg=(cfg.get("retail_raw_rag") or {}).get("embedding") or {},
            top_k=int(cfg.get("search_top_k") or 5),
            page_prefix_chars=int(cfg.get("page_prefix_chars") or 8000),
            max_chars_per_chunk=int(cfg.get("context_max_chars_per_chunk") or 0),
            raw_rag_cfg=cfg.get("retail_raw_rag") or {},
            answer_llm_cfg=cfg.get("answer") or {},
        )

    t0 = time.perf_counter()
    log.step(
        f"retail lane benchmark {kind} mode={retrieval_mode} raw={raw_retrieval or 'default'} "
        f"profile={profile_id or '-'} run_id={rid} rows={total_planned}"
    )
    try:
        _run_rows(ctx, lanes=selected, questions=questions)
    finally:
        _flush_results_json(ctx, questions)
        elapsed = int(time.perf_counter() - t0)
        log.info(f"benchmark {kind} done rows={len(ctx.completed)}/{total_planned} elapsed_sec={elapsed}")

    return out_dir


def run_smoke(
    repo_root: Path,
    *,
    lane_ids: list[str],
    question_ids: list[str],
    run_id: str | None = None,
    resume: bool = False,
    retrieval_mode: str = "llm_wiki",
    raw_retrieval: str = "",
    raw_agentic: bool = False,
    force_reindex: bool = False,
    skip_index_check: bool = False,
    profile_id: str = "",
    resolved: ResolvedRunProfile | None = None,
) -> Path:
    """Execute smoke questions on selected lanes; write ops run directory."""
    suite_path = repo_root / "tests/retail_multi_profiles/data/retail-manual-qa-test-suite.json"
    data = load_suite(suite_path)
    questions = filter_question_ids(data, set(question_ids))
    if len(questions) != len(question_ids):
        found = {q.question_id for q in questions}
        missing = set(question_ids) - found
        raise ValueError(f"missing question ids: {missing}")
    return run_benchmark(
        repo_root,
        lane_ids=lane_ids,
        questions=questions,
        kind="smoke",
        run_id=run_id,
        resume=resume,
        retrieval_mode=retrieval_mode,
        raw_retrieval=raw_retrieval,
        raw_agentic=raw_agentic,
        force_reindex=force_reindex,
        skip_index_check=skip_index_check,
        profile_id=profile_id,
        resolved=resolved,
    )


def run_full(
    repo_root: Path,
    *,
    lane_ids: list[str],
    limit: int = 0,
    run_id: str | None = None,
    resume: bool = False,
    retrieval_mode: str = "llm_wiki",
    raw_retrieval: str = "",
    raw_agentic: bool = False,
    force_reindex: bool = False,
    skip_index_check: bool = False,
    profile_id: str = "",
    resolved: ResolvedRunProfile | None = None,
) -> Path:
    """Run full suite (90 questions) per lane; optional ``limit`` truncates for dry runs."""
    suite_path = repo_root / "tests/retail_multi_profiles/data/retail-manual-qa-test-suite.json"
    data = load_suite(suite_path)
    questions = list(iter_questions(data))
    if limit > 0:
        questions = questions[:limit]
    return run_benchmark(
        repo_root,
        lane_ids=lane_ids,
        questions=questions,
        kind="full" if limit <= 0 else f"full-limit-{limit}",
        run_id=run_id,
        resume=resume,
        retrieval_mode=retrieval_mode,
        raw_retrieval=raw_retrieval,
        raw_agentic=raw_agentic,
        force_reindex=force_reindex,
        skip_index_check=skip_index_check,
        profile_id=profile_id,
        resolved=resolved,
    )
