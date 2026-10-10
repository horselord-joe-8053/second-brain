"""Shared eval hit logic: strict gold (D6) vs optional LLM-authored acceptable set."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


def score_top1(case: dict, top_ticket_id: Optional[str]) -> Tuple[bool, Optional[bool]]:
    """Returns (strict_hit, acceptable_hit or None if no acceptable_ticket_ids)."""
    strict = set(case.get("expected_ticket_ids") or [])
    if not top_ticket_id:
        acc = case.get("acceptable_ticket_ids")
        return False, (False if acc is not None else None)
    hit_strict = top_ticket_id in strict
    acc = case.get("acceptable_ticket_ids")
    if acc is None:
        return hit_strict, None
    return hit_strict, top_ticket_id in set(acc)


def aggregate_recall(
    results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Summarize strict recall@1 and optional acceptable_recall@1."""
    n = len(results)
    strict_hits = sum(1 for r in results if r["hit_strict"])
    out: Dict[str, Any] = {
        "total": n,
        "recall_at_1": strict_hits / n if n else 0.0,
    }
    if any(r.get("hit_acceptable") is not None for r in results):
        acc_hits = sum(1 for r in results if r.get("hit_acceptable"))
        out["acceptable_recall_at_1"] = acc_hits / n if n else 0.0
    return out
