"""Reciprocal rank fusion for hybrid ticket retrieval."""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple


def reciprocal_rank_fusion(
    ranked_lists: Sequence[Sequence[str]],
    k: int = 60,
    *,
    lexical_rank_order: Sequence[str] | None = None,
) -> List[Tuple[str, float]]:
    """Merge multiple ranked id lists; higher score is better.

    When RRF scores tie, prefer the document ranked higher on the lexical leg
    (lower rank index). Stage-1 hybrid demo: vector may favor a twin intake shape
    while lexical ranks the gold ticket on error code.
    """
    scores: Dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, doc_id in enumerate(ranked, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    lex_rank: Dict[str, int] = {
        doc_id: rank for rank, doc_id in enumerate(lexical_rank_order or (), start=1)
    }

    def sort_key(item: Tuple[str, float]) -> Tuple[float, int, str]:
        doc_id, score = item
        return (-score, lex_rank.get(doc_id, 10_000), doc_id)

    return sorted(scores.items(), key=sort_key)
