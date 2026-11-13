"""In-memory vector ranking for manual chunk rows (PG pool or fixtures)."""

from __future__ import annotations

import math
from typing import Any


def cosine_distance(a: list[float], b: list[float]) -> float:
    """L2 distance on normalized vectors (1 − cosine similarity)."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 1.0
    cos = dot / (na * nb)
    return 1.0 - cos


def rank_chunks_vector(
    query_vector: list[float],
    chunks: list[dict[str, Any]],
    *,
    top_n: int,
) -> list[dict[str, Any]]:
    """Order chunk dicts by cosine distance to query_vector."""
    scored: list[tuple[float, str, dict[str, Any]]] = []
    for row in chunks:
        vec = list(row.get("vector") or [])
        if not vec:
            continue
        dist = cosine_distance(query_vector, vec)
        cid = str(row.get("chunk_id") or "")
        scored.append(
            (dist, cid, {**row, "distance": dist, "vector_score": 1.0 / (1.0 + dist)})
        )
    scored.sort(key=lambda x: (x[0], x[1]))
    return [row for _, _, row in scored[:top_n]]
