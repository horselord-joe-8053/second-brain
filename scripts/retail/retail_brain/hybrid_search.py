"""Ticket search: vector leg, lexical leg, optional RRF (V1 / V1.1)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from retail_brain.embeddings import cosine_distance, embed_text
from retail_brain.models import RESOLVED
from retail_brain.rrf import reciprocal_rank_fusion


@dataclass
class TicketRow:
    ticket_id: str
    model: str
    status: str
    customer_query_text: str
    resolution_text: str


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def lexical_score(query: str, document: str) -> float:
    """Simple overlap score for tsvector-style leg (offline tests)."""
    q = _tokenize(query)
    d = _tokenize(document)
    if not q:
        return 0.0
    return len(q & d) / len(q)


def vector_rank(
    query: str,
    rows: Sequence[TicketRow],
    *,
    model_filter: Optional[str] = None,
    limit: int = 25,
) -> List[str]:
    q_emb = embed_text(query, task_type="RETRIEVAL_QUERY")
    candidates = [
        r
        for r in rows
        if r.status == RESOLVED and (model_filter is None or r.model == model_filter)
    ]
    scored = sorted(
        (
            (r.ticket_id, cosine_distance(q_emb, embed_text(r.customer_query_text)))
            for r in candidates
        ),
        key=lambda x: (x[1], x[0]),
    )
    return [tid for tid, _ in scored[:limit]]


def lexical_rank(
    query: str,
    rows: Sequence[TicketRow],
    *,
    model_filter: Optional[str] = None,
    limit: int = 25,
) -> List[str]:
    candidates = [
        r
        for r in rows
        if r.status == RESOLVED and (model_filter is None or r.model == model_filter)
    ]
    scored = sorted(
        ((r.ticket_id, lexical_score(query, r.customer_query_text)) for r in candidates),
        key=lambda x: (-x[1], x[0]),
    )
    return [tid for tid, score in scored[:limit] if score > 0]


def hybrid_enabled() -> bool:
    return os.environ.get("RETAIL_TICKET_HYBRID_SEARCH", "0").strip() in ("1", "true", "yes")


def search_ticket_ids(
    query: str,
    rows: Sequence[TicketRow],
    *,
    model_filter: Optional[str] = None,
    limit: int = 10,
) -> List[str]:
    """V1 vector-only or V1.1 RRF fusion depending on env flag."""
    if not hybrid_enabled():
        return vector_rank(query, rows, model_filter=model_filter, limit=limit)
    v_list = vector_rank(query, rows, model_filter=model_filter, limit=limit * 2)
    l_list = lexical_rank(query, rows, model_filter=model_filter, limit=limit * 2)
    fused = reciprocal_rank_fusion([v_list, l_list])
    return [doc_id for doc_id, _ in fused[:limit]]


def row_by_id(rows: Sequence[TicketRow]) -> Dict[str, TicketRow]:
    return {r.ticket_id: r for r in rows}
