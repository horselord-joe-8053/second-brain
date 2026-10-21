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


def _ops_logger(run_id: str) -> NeatLogger:
    """Per-run tee under logs/ops for tail -f during long benchmarks."""
    safe = run_id.replace("/", "_")
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


def _run_one_row(
    ctx: _RunContext,
    *,
    lane: Lane,
    q: SuiteQuestion,
    wiki: LlmWikiHttpClient,
    index: int,
    answer_llm: Any,
    judge_llm: Any,
    literal: str,
    top_k: int,
    page_prefix: int,
    template: str,
) -> None:
    """Execute one lane × question with step progress (pinpoints timeouts)."""
    key = progress_row_key(lane.lane_id, q.question_id)
    if key in ctx.completed:
        ctx.log.info(f"skip completed {key}")
        return

    query = scoped_query(template, model_id=q.model_id, question=q.question)
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
        hits, context, retrieval_ms = retrieve_context(
            wiki, query, top_k=top_k, page_prefix_chars=page_prefix
        )
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
            candidate, answer_ms = answer_from_context(
                q.question,
                context,
                provider=answer_llm.provider,
                model=answer_llm.model,
                temperature=answer_llm.temperature,
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

        row = {
            "lane": lane.lane_id,
            "ingest_kind": lane.ingest_kind,
            "project_path": str(lane.project_path),
            "question_id": q.question_id,
            "model_id": q.model_id,
            "difficulty": q.difficulty,
            "query": query,
            "search_meta": dict(getattr(wiki, "last_search_meta", {}) or {}),
            "top_paths": [h.get("path") for h in hits[:top_k]],
            "top_hits": compact_search_hits(hits[:top_k]),
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
    template = str(cfg.get("query_template") or "{model_id} {question}")
    answer_llm, judge_llm = resolve_eval_llms(cfg)

    index = 0
    for lane in lanes:
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
) -> Path:
    """Run selected questions on lanes; checkpoint JSONL + incremental results.json."""
    cfg = load_merged_run_config(repo_root)
    lanes_map = load_lanes(repo_root)
    selected = [lanes_map[lid] for lid in lane_ids]

    rid = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = repo_root / "ops" / "runs" / "retail-lane-abcd" / rid
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "results.jsonl"
    log = _ops_logger(rid)

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
    )

    t0 = time.perf_counter()
    log.step(f"retail lane benchmark {kind} run_id={rid} rows={total_planned}")
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
    )


def run_full(
    repo_root: Path,
    *,
    lane_ids: list[str],
    limit: int = 0,
    run_id: str | None = None,
    resume: bool = False,
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
    )
