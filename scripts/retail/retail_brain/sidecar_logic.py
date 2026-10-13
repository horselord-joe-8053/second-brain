"""Agent sidecar entry: semantic ticket search + readonly SQL over in-memory rows.

Wires ``utils.retail_fru.sidecar`` to ``hybrid_search.search_ticket_ids`` (respects search mode env).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from retail_brain.hybrid_search import TicketRow, row_by_id, search_ticket_ids
from utils.retail_fru.sidecar import execute_sql_readonly as execute_sql_readonly
from utils.retail_fru.sidecar import semantic_search as _semantic_search


def semantic_search(
    rows: Sequence[TicketRow],
    *,
    query_text: str,
    model_filter: Optional[str] = None,
    limit: int = 10,
    similarity_threshold: float = 0.35,
) -> Dict[str, Any]:
    """Sidecar semantic search tool: ranked tickets + similarity metadata."""
    return _semantic_search(
        rows,
        query_text=query_text,
        search_fn=search_ticket_ids,
        model_filter=model_filter,
        limit=limit,
        similarity_threshold=similarity_threshold,
    )


__all__ = ["semantic_search", "execute_sql_readonly", "row_by_id", "TicketRow"]
