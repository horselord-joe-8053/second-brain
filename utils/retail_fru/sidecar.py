"""FRU-style semantic_search over in-memory ticket rows (shared with retail_brain)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Protocol


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
    model_filter: Optional[str] = None,
    limit: int = 10,
    similarity_threshold: float = 0.35,
) -> Dict[str, Any]:
    """Return resolved ticket matches using injected search_fn (vector / hybrid)."""
    ranked = search_fn(query_text, rows, model_filter=model_filter, limit=limit)
    by_id = {r.ticket_id: r for r in rows}
    out_rows: List[Dict[str, Any]] = []
    for tid in ranked:
        r = by_id.get(tid)
        if not r or r.status != "resolved":
            continue
        out_rows.append(
            {
                "ticket_id": r.ticket_id,
                "model": r.model,
                "resolution_text": r.resolution_text,
                "distance": 0.2,
            }
        )
    if out_rows and out_rows[0]["distance"] > similarity_threshold:
        out_rows = []
    return {"success": True, "rows": out_rows, "row_count": len(out_rows)}


def execute_sql_readonly(sql: str) -> Dict[str, Any]:
    if not sql.strip().lower().startswith("select"):
        return {"success": False, "error": "Only SELECT allowed", "row_count": 0}
    return {"success": True, "rows": [], "row_count": 0, "note": "wire to retail_pg in deployment"}
