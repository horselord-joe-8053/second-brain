"""Offline ticket search over in-memory ``TicketRow`` lists (CSV-backed tests).

Mirrors ``pg_search`` fusion semantics but:
  - Vectors: re-embed each candidate row per query (no pgvector index).
  - Lexical: token overlap score, not Tantivy/bm25x — fast, deterministic in pytest.

Use ``pg_search`` for Postgres-backed eval and production reload paths.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from retail_brain.embeddings import cosine_distance, embed_text
from retail_brain.models import RESOLVED
from retail_brain.rrf import code_boost_scores, reciprocal_rank_fusion
from retail_brain.search_mode import (
    code_boost_enabled,
    is_hybrid_mode,
    lexical_code_boost_lambda,
    resolve_ticket_search_mode,
    rrf_list_weights,
)
from retail_brain.text_normalize import fts_query_text, search_text_for_fts, text_for_embedding


@dataclass
class TicketRow:
    """One resolved-ticket row for offline search (subset of PG ``service_queries`` columns)."""

    ticket_id: str
    model: str
    status: str
    customer_query_text: str
    resolution_text: str


def _tokenize(text: str) -> set[str]:
    """Lowercase alphanumeric tokens for overlap scoring."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def lexical_score(query: str, document: str) -> float:
    """Fraction of query tokens present in document — stand-in for BM25 in offline tests."""
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
    """Rank resolved tickets by embedding distance to the query (dense leg, in-memory)."""
    q_emb = embed_text(query, task_type="RETRIEVAL_QUERY")
    candidates = [
        r
        for r in rows
        if r.status == RESOLVED and (model_filter is None or r.model == model_filter)
    ]
    scored = sorted(
        (
            (
                r.ticket_id,
                cosine_distance(q_emb, embed_text(text_for_embedding(r.customer_query_text))),
            )
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
    """Rank resolved tickets by token overlap after ``fts_query_text`` normalization."""
    candidates = [
        r
        for r in rows
        if r.status == RESOLVED and (model_filter is None or r.model == model_filter)
    ]
    q_norm = fts_query_text(query)
    scored = sorted(
        (
            (
                r.ticket_id,
                lexical_score(
                    q_norm,
                    search_text_for_fts(r.customer_query_text),
                ),
            )
            for r in candidates
        ),
        key=lambda x: (-x[1], x[0]),
    )
    return [tid for tid, score in scored[:limit] if score > 0]


def hybrid_enabled() -> bool:
    """Legacy boolean; prefer resolve_ticket_search_mode()."""
    return is_hybrid_mode()


def _fuse(
    query: str,
    rows: Sequence[TicketRow],
    v_list: List[str],
    l_list: List[str],
    *,
    mode: str,
    limit: int,
) -> List[str]:
    """RRF-merge vector and lexical lists with optional V1.2 SAM-E term boost."""
    w_v, w_l = rrf_list_weights(mode)
    extra: Dict[str, float] = {}
    if code_boost_enabled(mode):
        by_id = {r.ticket_id: search_text_for_fts(r.customer_query_text) for r in rows}
        candidates = set(v_list) | set(l_list)
        extra = code_boost_scores(
            query,
            list(candidates),
            id_to_search_text=by_id,
            lambda_boost=lexical_code_boost_lambda(),
        )
    fused = reciprocal_rank_fusion(
        [v_list, l_list],
        list_weights=[w_v, w_l],
        lexical_rank_order=l_list,
        extra_score_by_id=extra,
    )
    return [doc_id for doc_id, _ in fused[:limit]]


def search_ticket_ids(
    query: str,
    rows: Sequence[TicketRow],
    *,
    model_filter: Optional[str] = None,
    limit: int = 10,
) -> List[str]:
    """Vector-only or RRF fusion depending on RETAIL_TICKET_SEARCH_MODE."""
    mode = resolve_ticket_search_mode()
    if mode == "vector_only":
        return vector_rank(query, rows, model_filter=model_filter, limit=limit)
    v_list = vector_rank(query, rows, model_filter=model_filter, limit=limit * 2)
    l_list = lexical_rank(query, rows, model_filter=model_filter, limit=limit * 2)
    return _fuse(query, rows, v_list, l_list, mode=mode, limit=limit)


def row_by_id(rows: Sequence[TicketRow]) -> Dict[str, TicketRow]:
    """Index ticket rows by ``ticket_id`` for sidecar hydration."""
    return {r.ticket_id: r for r in rows}
