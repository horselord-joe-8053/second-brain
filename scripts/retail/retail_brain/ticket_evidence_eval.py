"""Eval rows for ticket evidence-path modes (P2.5 — baseline vs retriever stack)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from retail_brain.evidence.ticket_evidence_pipeline import (
    EvidencePathMode,
    build_ticket_evidence_stack,
)
from retail_brain.pg_search import search_ticket_hits_pg


def run_evidence_path_row(
    case: dict[str, Any],
    *,
    dsn: str,
    mode: EvidencePathMode,
    repo_root: Path,
    search_fn: Callable[..., tuple[str, list[dict[str, Any]]]] | None = None,
    generate_fn: Any | None = None,
) -> dict[str, Any]:
    """Evaluate one JSONL case through the selected evidence path."""
    query = str(case["query"])
    model_filter = str(case.get("model_filter") or "")
    expected = list(case.get("expected_ticket_ids") or [])
    verifier_json: dict[str, Any] | None = None
    loops = 0
    package_meta: dict[str, Any] | None = None

    if mode == "baseline":
        search = search_fn or search_ticket_hits_pg
        _m, hits = search(dsn, query, model_filter=model_filter or None, limit=5)
        top_id = hits[0]["ticket_id"] if hits else None
    else:
        stack = build_ticket_evidence_stack(
            dsn,
            repo_root=repo_root,
            mode=mode,
            generate_fn=generate_fn,
            search_fn=search_fn,
        )
        if mode == "agentic" and stack.agentic is not None:
            agentic = stack.agentic.retrieve_with_verifier(query, model_filter=model_filter)
            pkg = agentic.package
            verifier_json = agentic.verifier.to_dict()
            loops = agentic.loops
        else:
            pkg = stack.retriever.retrieve(query, model_filter=model_filter)
            loops = 0
        top_id = pkg.chunks[0].chunk_id if pkg.chunks else None
        package_meta = {**pkg.meta, "rank_fn_active": stack.rank_fn_active}

    hit_strict = bool(top_id and top_id in expected)
    return {
        "eval_id": case.get("eval_id"),
        "stratum": case.get("stratum"),
        "evidence_path": mode,
        "top_ticket_id": top_id,
        "hit_strict": hit_strict,
        "expected_ticket_ids": expected,
        "verifier": verifier_json,
        "agentic_loops": loops,
        "package_meta": package_meta,
    }


def write_evidence_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    """Persist per-row evidence eval output."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
