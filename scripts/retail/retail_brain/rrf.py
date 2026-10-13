"""Reciprocal rank fusion for hybrid ticket retrieval."""

from __future__ import annotations

from typing import Dict, List, Mapping, Sequence, Tuple


def reciprocal_rank_fusion(
    ranked_lists: Sequence[Sequence[str]],
    k: int = 60,
    *,
    list_weights: Sequence[float] | None = None,
    lexical_rank_order: Sequence[str] | None = None,
    extra_score_by_id: Mapping[str, float] | None = None,
) -> List[Tuple[str, float]]:
    """Merge ranked id lists; higher score is better.

    list_weights: per-leg multiplier on each 1/(k+rank) term (V1.1 equal, V1.2 0.7/0.3).
    extra_score_by_id: V1.3 code boost (λ · 1/(k+1)) added after leg fusion.
    """
    scores: Dict[str, float] = {}
    for li, ranked in enumerate(ranked_lists):
        w = 1.0
        if list_weights and li < len(list_weights):
            w = float(list_weights[li])
        for rank, doc_id in enumerate(ranked, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + w * (1.0 / (k + rank))
    for doc_id, bump in (extra_score_by_id or {}).items():
        scores[doc_id] = scores.get(doc_id, 0.0) + float(bump)
    # Tie-break: prefer higher lexical rank when RRF scores tie (stable, deterministic ids last).
    lex_rank: Dict[str, int] = {
        doc_id: rank for rank, doc_id in enumerate(lexical_rank_order or (), start=1)
    }

    def sort_key(item: Tuple[str, float]) -> Tuple[float, int, str]:
        """Sort by descending RRF score, then lexical rank, then ticket id."""
        doc_id, score = item
        return (-score, lex_rank.get(doc_id, 10_000), doc_id)

    return sorted(scores.items(), key=sort_key)


def code_boost_scores(
    query: str,
    candidate_ids: Sequence[str],
    *,
    id_to_search_text: Mapping[str, str],
    k: int = 60,
    lambda_boost: float = 10.0,
) -> Dict[str, float]:
    """Extra RRF mass for tickets whose indexed text contains the query's diag code."""
    from retail_brain.text_normalize import extract_diag_code

    code = extract_diag_code(query)
    if not code:
        return {}
    bump = lambda_boost / (k + 1)
    out: Dict[str, float] = {}
    for tid in candidate_ids:
        if extract_diag_code(id_to_search_text.get(tid, "")) == code:
            out[tid] = bump
    return out
