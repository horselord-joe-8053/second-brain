"""Run TYPE_C_C20 insight QA: A1 wiki vs A3 manual RAG, judged against suite gold."""

from __future__ import annotations

import hashlib
import json
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from retail_brain.answer_manuals import LlmWikiHttpClient
from logging_utils.run_progress import write_jsonl_line
from utils.neat_logger.neat_logger_instance import NeatLoggerFactory

from .answer_pipeline import answer_from_context, retrieve_context
from .eval_models import assert_independent_eval_providers, resolve_eval_llms
from .load_cos_insight_suite import CosInsightQuestion, InsightCriterion
from .run_config import load_merged_run_config
from .scoring import score_judged
from .w20_authoring import (
    BLINDING_SEED,
    COMPATIBILITY_PASS_SCORE,
    HUMAN_REVIEW_CONFIDENCE,
)


def score_insight_judged(
    question: str,
    gold: str,
    candidate: str,
    rubric: tuple[str, ...],
    *,
    provider: str,
    model: str,
    temperature: float = 0.0,
    llm_generate: Callable[..., str] | None = None,
) -> tuple[bool, str]:
    """Judge a Type C answer against gold text and rubric bullets."""
    if llm_generate is None:
        from .llm_generate import llm_generate as _llm

        llm_generate = _llm
    bullets = "\n".join(f"- {b}" for b in rubric)
    prompt = (
        "You are a strict grader for management insight answers. Reply JSON only: "
        '{"pass": true|false, "rationale": "one sentence"}\n'
        f"Question: {question}\nGold answer: {gold}\nRubric:\n{bullets}\n"
        f"Candidate: {candidate}\n"
        "Pass if the candidate satisfies the rubric spirit and does not add unsupported claims."
    )
    raw = llm_generate(prompt, provider=provider, model=model, temperature=temperature)
    try:
        parsed = json.loads(raw.strip().strip("`").removeprefix("json"))
        return bool(parsed.get("pass")), str(parsed.get("rationale") or raw)
    except Exception:
        ok = "true" in raw.lower() and "pass" in raw.lower()
        return ok, raw[:300]


def _bounded_int(value: object, *, low: int = 0, high: int = 4) -> int:
    """Coerce one judge dimension into its allowed integer range."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = low
    return max(low, min(high, parsed))


def _bounded_confidence(value: object) -> float:
    """Coerce model confidence into the inclusive 0–1 range."""
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = 0.0
    return max(0.0, min(1.0, parsed))


def _graded_score(
    correctness: int,
    completeness: int,
    grounding: int,
    unsupported_claims: int,
) -> int:
    """Compute the frozen weighted semantic score without trusting model arithmetic."""
    score = (
        correctness * 10.0
        + completeness * 6.25
        + grounding * 6.25
        + (4 - unsupported_claims) * 2.5
    )
    return int(round(score))


def _json_object(raw: str) -> dict[str, Any]:
    """Parse one JSON-only model response, tolerating a single fenced wrapper."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").removeprefix("json").strip()
    parsed = json.loads(cleaned)
    if not isinstance(parsed, dict):
        raise ValueError("judge response must be a JSON object")
    return parsed


def score_insight_graded(
    question: str,
    gold: str,
    candidate: str,
    criteria: tuple[InsightCriterion, ...],
    *,
    question_id: str,
    provider: str,
    model: str,
    temperature: float = 0.0,
    llm_generate: Callable[..., str] | None = None,
) -> dict[str, Any]:
    """Blindly grade one W20 v2 candidate with partial credit and deterministic caps."""
    if llm_generate is None:
        from .llm_generate import llm_generate as _llm

        llm_generate = _llm
    candidate_id = hashlib.sha256(
        f"{BLINDING_SEED}\0{question_id}\0{candidate}".encode("utf-8")
    ).hexdigest()[:16]
    criterion_payload = [
        {"index": index, "text": item.text, "critical": item.critical}
        for index, item in enumerate(criteria)
    ]
    prompt = (
        "You are an independent evaluator. Grade semantic quality with partial credit. "
        "A missed non-critical criterion lowers completeness but never forces failure. "
        "Citation presence and formatting are separate from semantic correctness. "
        "Reply with one JSON object containing integer 0-4 fields correctness, completeness, "
        "manual_grounding, unsupported_claims, and citation_score; float 0-1 "
        "correctness_confidence; verdict; rationale; and criterion_scores. Each criterion score "
        "must contain index, status (met|partly_met|not_met), contradiction (boolean), and reason. "
        "Do not compute an overall score.\n"
        f"Question: {question}\n"
        f"Gold answer: {gold}\n"
        f"Criteria: {json.dumps(criterion_payload, ensure_ascii=False)}\n"
        f"Opaque candidate id: {candidate_id}\n"
        f"Candidate answer: {candidate}"
    )
    raw = llm_generate(prompt, provider=provider, model=model, temperature=temperature)
    try:
        parsed = _json_object(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        return {
            "candidate_id": candidate_id,
            "correctness": 0,
            "completeness": 0,
            "manual_grounding": 0,
            "unsupported_claims": 4,
            "citation_score": 0,
            "correctness_confidence": 0.0,
            "criterion_scores": [],
            "overall_score": 0,
            "verdict": "incorrect",
            "judge_pass": False,
            "judge_rationale": f"Malformed judge response: {exc}",
            "human_review_flags": ["malformed_judge_response"],
        }

    correctness = _bounded_int(parsed.get("correctness"))
    completeness = _bounded_int(parsed.get("completeness"))
    grounding = _bounded_int(parsed.get("manual_grounding"))
    unsupported = _bounded_int(parsed.get("unsupported_claims"))
    citation_score = _bounded_int(parsed.get("citation_score"))
    confidence = _bounded_confidence(parsed.get("correctness_confidence"))
    raw_scores = parsed.get("criterion_scores")
    raw_scores = raw_scores if isinstance(raw_scores, list) else []
    by_index = {
        int(item.get("index")): item
        for item in raw_scores
        if isinstance(item, dict) and str(item.get("index", "")).isdigit()
    }
    normalized_scores: list[dict[str, Any]] = []
    critical_missed = False
    critical_contradiction = False
    for index, criterion in enumerate(criteria):
        source = by_index.get(index, {})
        status = str(source.get("status") or "not_met").strip().lower()
        if status not in {"met", "partly_met", "not_met"}:
            status = "not_met"
        contradiction = bool(source.get("contradiction"))
        normalized_scores.append(
            {
                "index": index,
                "text": criterion.text,
                "critical": criterion.critical,
                "status": status,
                "contradiction": contradiction,
                "reason": str(source.get("reason") or ""),
            }
        )
        if criterion.critical and status != "met":
            critical_missed = True
        if criterion.critical and contradiction:
            critical_contradiction = True

    overall = _graded_score(correctness, completeness, grounding, unsupported)
    if critical_contradiction:
        overall = min(overall, 49)
    elif critical_missed:
        overall = min(overall, 69)
    passed = (
        overall >= COMPATIBILITY_PASS_SCORE
        and correctness >= 3
        and not critical_contradiction
    )
    review_flags: list[str] = []
    if confidence < HUMAN_REVIEW_CONFIDENCE:
        review_flags.append("low_confidence")
    if 65 <= overall <= 75:
        review_flags.append("borderline_score")
    return {
        "candidate_id": candidate_id,
        "correctness": correctness,
        "completeness": completeness,
        "manual_grounding": grounding,
        "unsupported_claims": unsupported,
        "citation_score": citation_score,
        "correctness_confidence": confidence,
        "criterion_scores": normalized_scores,
        "overall_score": overall,
        "verdict": str(parsed.get("verdict") or ""),
        "judge_pass": passed,
        "judge_rationale": str(parsed.get("rationale") or ""),
        "human_review_flags": review_flags,
    }


@dataclass
class CosInsightRunContext:
    """Output paths and config for one cos insight benchmark run."""

    repo: Path
    run_id: str
    out_dir: Path
    results_path: Path
    cfg: dict[str, Any]
    progress_path: Path | None = None


def _cos_logger(run_id: str):
    """Create the standard W20 evaluation operator logger."""
    safe = run_id.replace("/", "_")
    return NeatLoggerFactory.create(
        "OPS",
        "W20_EVAL",
        log_file_name=f"w20-eval-{safe}.log",
        log_output="both",
    )


def _progress(ctx: CosInsightRunContext, payload: dict[str, Any]) -> None:
    """Append one progress checkpoint when the caller configured a path."""
    if ctx.progress_path is not None:
        write_jsonl_line(ctx.progress_path, {"type": "progress", **payload})


def _wiki_client(repo: Path) -> LlmWikiHttpClient:
    """HTTP client for Lane B brain project (raises if token missing)."""
    from .lanes import load_lanes

    base = os.environ.get("LLM_WIKI_API_BASE_URL") or "http://127.0.0.1:19828/api/v1"
    token = os.environ.get("LLM_WIKI_API_TOKEN") or ""
    if not token:
        raise RuntimeError("LLM_WIKI_API_TOKEN not set")
    lane = load_lanes(repo)["B"]
    return LlmWikiHttpClient(str(lane.project_path), api_base=base, token=token, timeout=120.0)


def retrieve_bundled_manual(
    ctx: CosInsightRunContext,
    question: str,
) -> tuple[list[dict[str, Any]], str, int]:
    """A3 arm: Lane B manual hybrid RAG from ``cos_insight_bundled_profile_id``."""
    from .lanes import load_lanes
    from .manual_raw_pipeline import build_manual_raw_pipeline
    from .raw_rag_context import concat_top_k_raw_chunks
    from .resolved_run_profile import resolve_effective_profile

    profile_id = str(ctx.cfg.get("cos_insight_bundled_profile_id") or "MANUAL_B_RAW_PG_HYBRID")
    resolved = resolve_effective_profile(ctx.cfg, profile_id=profile_id, lane_ids=["B"])
    lane = load_lanes(ctx.repo)[resolved.lane_ids[0]]
    top_k = int(ctx.cfg.get("search_top_k") or 5)
    page_prefix = int(ctx.cfg.get("page_prefix_chars") or 8000)
    chunk_max = int(ctx.cfg.get("context_max_chars_per_chunk") or 0)
    embed_cfg = (ctx.cfg.get("retail_raw_rag") or {}).get("embedding") or {}
    t0 = time.perf_counter()
    pipeline = build_manual_raw_pipeline(
        lane,
        resolved,
        embed_cfg=embed_cfg,
        top_k=top_k,
        page_prefix_chars=page_prefix,
        max_chars_per_chunk=chunk_max,
        raw_rag_cfg=ctx.cfg.get("retail_raw_rag") or {},
        answer_llm_cfg=ctx.cfg.get("answer") or {},
    )
    pkg = pipeline.retriever.retrieve(question, model_id="", skip_index_check=True)
    hits = [
        {
            "source_relpath": c.source_relpath,
            "chunk_id": c.chunk_id,
            "text": c.text,
            "path": c.source_relpath,
        }
        for c in pkg.chunks
    ]
    context = concat_top_k_raw_chunks(
        hits,
        page_prefix_chars=page_prefix,
        max_chars_per_chunk=chunk_max,
    )
    return hits, context, int((time.perf_counter() - t0) * 1000)


def run_cos_insight_row(
    ctx: CosInsightRunContext,
    q: CosInsightQuestion,
    *,
    arm: str,
    wiki: LlmWikiHttpClient | None,
    answer_llm: Any,
    judge_llm: Any,
    llm_generate: Callable[..., str] | None = None,
    bundled_retrieve: Callable[..., tuple[list[dict[str, Any]], str, int]] | None = None,
) -> dict[str, Any]:
    """Execute one question on the wiki arm (A1) or the manual-RAG arm (A3)."""
    arm = arm.strip().lower()
    t0 = time.perf_counter()
    if arm == "wiki":
        if wiki is None:
            raise RuntimeError("wiki client required for wiki arm")
        top_k = int(ctx.cfg.get("search_top_k") or 5)
        page_prefix = int(ctx.cfg.get("page_prefix_chars") or 8000)
        hits, context, retrieval_ms = retrieve_context(
            wiki,
            q.question,
            top_k=top_k,
            page_prefix_chars=page_prefix,
            wiki_evidence=ctx.cfg.get("wiki_evidence"),
        )
        wiki_answer = ctx.cfg.get("wiki_answer") or {}
        label = str(wiki_answer.get("provisional_label") or "[provisional insight]")
        candidate, answer_ms = answer_from_context(
            q.question,
            context,
            provider=answer_llm.provider,
            model=answer_llm.model,
            temperature=answer_llm.temperature,
            preamble=label,
            insight_mode=True,
            generate=llm_generate,
        )
    elif arm == "bundled":
        retrieve = bundled_retrieve or retrieve_bundled_manual
        hits, context, retrieval_ms = retrieve(ctx, q.question)
        candidate, answer_ms = answer_from_context(
            q.question,
            context,
            provider=answer_llm.provider,
            model=answer_llm.model,
            temperature=answer_llm.temperature,
            preamble="[manual retrieval]",
            insight_mode=True,
            generate=llm_generate,
        )
    else:
        raise ValueError(f"unknown arm: {arm}")
    _progress(
        ctx,
        {
            "step": "judge_start",
            "question_id": q.question_id,
            "opaque_candidate_id": hashlib.sha256(
                f"{BLINDING_SEED}\0{q.question_id}\0{candidate}".encode("utf-8")
            ).hexdigest()[:16],
        },
    )
    graded: dict[str, Any] = {}
    if q.question_class:
        graded = score_insight_graded(
            q.question,
            q.gold_answer,
            candidate,
            q.criteria,
            question_id=q.question_id,
            provider=judge_llm.provider,
            model=judge_llm.model,
            temperature=judge_llm.temperature,
            llm_generate=llm_generate,
        )
        passed = bool(graded["judge_pass"])
        rationale = str(graded["judge_rationale"])
    else:
        passed, rationale = score_insight_judged(
            q.question,
            q.gold_answer,
            candidate,
            q.rubric,
            provider=judge_llm.provider,
            model=judge_llm.model,
            temperature=judge_llm.temperature,
            llm_generate=llm_generate,
        )
    result = {
        "question_id": q.question_id,
        "question_class": q.question_class,
        "arm": arm,
        "difficulty": q.difficulty,
        "judge_pass": passed,
        "judge_rationale": rationale,
        "candidate": candidate,
        "answer_provider": answer_llm.provider,
        "answer_model": answer_llm.model,
        "judge_provider": judge_llm.provider,
        "judge_model": judge_llm.model,
        "context_chars": len(context),
        "retrieval_ms": retrieval_ms,
        "answer_ms": answer_ms,
        "elapsed_ms": int((time.perf_counter() - t0) * 1000),
        "top_hit_paths": [str(h.get("path") or "") for h in hits[:5]],
        "wiki_evidence_mode": (ctx.cfg.get("wiki_evidence") or {}).get("mode"),
    }
    result.update(graded)
    return result


def run_cos_insight_benchmark(
    repo: Path,
    questions: list[CosInsightQuestion],
    *,
    run_id: str,
    arms: tuple[str, ...] = ("wiki", "bundled"),
    wiki: LlmWikiHttpClient | None = None,
    llm_generate: Callable[..., str] | None = None,
    author_provider: str = "",
    suite_sha256: str = "",
    resume: bool = False,
) -> Path:
    """Run pending question-arm pairs and optionally resume an interrupted live run."""
    cfg = load_merged_run_config(repo)
    answer_llm, judge_llm = resolve_eval_llms(cfg)
    if author_provider:
        assert_independent_eval_providers(author_provider, judge_llm.provider)
    out_dir = repo / "ops" / "runs" / "retail-cos-insight" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    results_path = out_dir / "results.jsonl"
    progress_path = out_dir / "progress.jsonl"
    ctx = CosInsightRunContext(
        repo=repo,
        run_id=run_id,
        out_dir=out_dir,
        results_path=results_path,
        cfg=cfg,
        progress_path=progress_path,
    )
    log = _cos_logger(run_id)
    if wiki is None and "wiki" in arms:
        wiki = _wiki_client(repo)
    tasks = [(arm, q) for arm in arms for q in questions]
    if any(q.question_class for q in questions):
        random.Random(BLINDING_SEED).shuffle(tasks)
    completed: set[tuple[str, str]] = set()
    if resume and results_path.exists():
        for line in results_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            completed.add((str(row.get("arm") or ""), str(row.get("question_id") or "")))
    pending = [(arm, q) for arm, q in tasks if (arm, q.question_id) not in completed]
    log.step(
        f"W20 evaluation run_id={run_id} rows={len(tasks)} "
        f"completed={len(completed)} pending={len(pending)}"
    )
    mode = "a" if resume else "w"
    with results_path.open(mode, encoding="utf-8") as out:
        for index, (arm, q) in enumerate(pending, start=1):
            _progress(
                ctx,
                {
                    "step": "row_start",
                    "row_index": index,
                    "row_count": len(pending),
                    "question_id": q.question_id,
                },
            )
            log.info(f"row {index}/{len(pending)} question={q.question_id}")
            with log.heartbeat(f"W20 row {index}/{len(pending)}"):
                row = run_cos_insight_row(
                    ctx,
                    q,
                    arm=arm,
                    wiki=wiki,
                    answer_llm=answer_llm,
                    judge_llm=judge_llm,
                    llm_generate=llm_generate,
                )
            row["ts"] = datetime.now(timezone.utc).isoformat()
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            _progress(
                ctx,
                {
                    "step": "row_done",
                    "row_index": index,
                    "question_id": q.question_id,
                    "opaque_candidate_id": row.get("candidate_id"),
                },
            )
    summary = {
        "run_id": run_id,
        "arms": list(arms),
        "question_count": len(questions),
        "suite_sha256": suite_sha256,
        "author_provider": author_provider,
        "answer_provider": answer_llm.provider,
        "answer_model": answer_llm.model,
        "judge_provider": judge_llm.provider,
        "judge_model": judge_llm.model,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return results_path
