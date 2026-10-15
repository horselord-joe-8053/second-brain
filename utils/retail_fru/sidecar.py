"""FRU-style semantic_search over in-memory ticket rows (shared with retail_brain)."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Sequence, Protocol


class TicketLike(Protocol):
    ticket_id: str
    model: str
    status: str
    customer_query_text: str
    resolution_text: str


def semantic_search(
    rows: Sequence[TicketLike],
    *,
    query_text: str,
    search_fn,
    similarity_fn: Callable[[str, Sequence[TicketLike]], Dict[str, float]],
    model_filter: Optional[str] = None,
    limit: int = 10,
    similarity_threshold: float = 0.35,
) -> Dict[str, Any]:
    """Resolved ticket matches from injected ``search_fn``; ``distance = 1 - cosine`` from ``similarity_fn``.

    ``similarity_threshold`` is a max distance: if the best hit is farther, no rows are returned.
    """
    ranked = search_fn(query_text, rows, model_filter=model_filter, limit=limit)
    by_id = {r.ticket_id: r for r in rows}
    hits = [by_id[tid] for tid in ranked if tid in by_id and by_id[tid].status == "resolved"]
    cos = similarity_fn(query_text, hits) if hits else {}
    out_rows: List[Dict[str, Any]] = [
        {
            "ticket_id": r.ticket_id,
            "model": r.model,
            "resolution_text": r.resolution_text,
            "distance": round(1.0 - cos[r.ticket_id], 4),
        }
        for r in hits
    ]
    if out_rows and out_rows[0]["distance"] > similarity_threshold:
        out_rows = []
    return {"success": True, "rows": out_rows, "row_count": len(out_rows)}


def execute_sql_readonly(sql: str) -> Dict[str, Any]:
    if not sql.strip().lower().startswith("select"):
        return {"success": False, "error": "Only SELECT allowed", "row_count": 0}
    return {"success": True, "rows": [], "row_count": 0, "note": "wire to retail_pg in deployment"}
