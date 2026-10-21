"""Replay mixed-outcome tickets using only wiki/sources pages from a top-k search."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from retail_brain.answer_manuals import LlmWikiHttpClient
from retail_brain.wiki_page_context import concat_hit_pages

from .answer_pipeline import answer_from_context, scoped_query
from .eval_models import resolve_eval_llms
from .lanes import load_lanes
from .load_suite import iter_questions, load_suite
from .run_config import load_merged_run_config
from .scoring import score_judged
from .search_hits import compact_search_hits, source_only_hits


def load_question_ids(path: Path) -> list[str]:
    """Question ids from the mixed-outcome JSON (`tickets[].question_id`)."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    tickets = payload.get("tickets") or []
    return [str(item["question_id"]) for item in tickets]


def run_sources_only_replay(
    repo_root: Path,
    *,
    ticket_file: Path,
    lane_ids: list[str] | None = None,
    top_k: int = 10,
    run_id: str = "abcd-sources-only-topk10",
) -> Path:
    """Search top_k, keep wiki/sources hits, answer and judge those excerpts only.

    This compares source-page text that already ranked inside top_k. Pages that
    rank below top_k are not read.
    """
    cfg = load_merged_run_config(repo_root)
    page_prefix = int(cfg.get("page_prefix_chars") or 8000)
    template = str(cfg.get("query_template") or "{model_id} {question}")
    answer_llm, judge_llm = resolve_eval_llms(cfg)
    lanes = load_lanes(repo_root)
    selected = [lanes[lid] for lid in (lane_ids or ["B", "D"])]
    suite = load_suite(repo_root / "tests/retail_multi_profiles/data/retail-manual-qa-test-suite.json")
    questions = {q.question_id: q for q in iter_questions(suite)}
    wanted = load_question_ids(ticket_file)

    out_dir = repo_root / "ops" / "runs" / "retail-lane-abcd" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "results.jsonl"
    jsonl_path.write_text("", encoding="utf-8")
    rows: list[dict[str, Any]] = []

    for lane in selected:
        wiki = LlmWikiHttpClient(str(lane.project_path), timeout=120.0)
        for question_id in wanted:
            q = questions[question_id]
            query = scoped_query(template, model_id=q.model_id, question=q.question)
            hits = wiki.search(query, limit=top_k)
            kept = source_only_hits(hits)
            context, read_ms = concat_hit_pages(wiki, kept, page_prefix_chars=page_prefix)
            candidate, answer_ms = answer_from_context(
                q.question,
                context,
                provider=answer_llm.provider,
                model=answer_llm.model,
                temperature=answer_llm.temperature,
            )
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
            row = {
                "lane": lane.lane_id,
                "question_id": question_id,
                "difficulty": q.difficulty,
                "query": query,
                "search_top_k": top_k,
                "source_filter": "wiki/sources/",
                "search_meta": dict(getattr(wiki, "last_search_meta", {}) or {}),
                "top_hits_searched": compact_search_hits(hits),
                "source_hits_used": compact_search_hits(kept),
                "source_hit_count": len(kept),
                "candidate_answer": candidate,
                "pass": passed,
                "judge_rationale": rationale,
                "latency_ms": {"read": read_ms, "answer": answer_ms, "judge": judge_ms},
            }
            rows.append(row)
            with jsonl_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({"type": "result", "row": row}, ensure_ascii=False) + "\n")
            time.sleep(0.3)

    summary = _summarize(rows)
    payload = {
        "run_id": run_id,
        "kind": "sources_only_replay",
        "search_top_k": top_k,
        "source_filter": "wiki/sources/",
        "ticket_file": str(ticket_file),
        "summary": summary,
        "rows": rows,
    }
    out_path = out_dir / "results.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out_path


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Pass counts and how often a source page was actually in the top-k window."""
    by_lane: dict[str, dict[str, int]] = {}
    for row in rows:
        bucket = by_lane.setdefault(row["lane"], {"pass": 0, "total": 0, "rows_with_sources": 0})
        bucket["total"] += 1
        bucket["pass"] += int(bool(row.get("pass")))
        bucket["rows_with_sources"] += int(int(row.get("source_hit_count") or 0) > 0)
    return by_lane
