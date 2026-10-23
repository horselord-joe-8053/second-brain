"""Simple lexical ranking over raw chunk rows (BM25-ish token overlap)."""

from __future__ import annotations

import math
import re
from typing import Any

_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    """Lowercase alphanumeric tokens for overlap scoring."""
    return [t.lower() for t in _TOKEN_RE.findall(text)]


def lexical_score(query: str, chunk_text: str) -> float:
    """Sum of query term hits in chunk (log-damped repeat hits)."""
    q_tokens = tokenize(query)
    if not q_tokens:
        return 0.0
    c_tokens = tokenize(chunk_text)
    if not c_tokens:
        return 0.0
    freq: dict[str, int] = {}
    for t in c_tokens:
        freq[t] = freq.get(t, 0) + 1
    score = 0.0
    for qt in q_tokens:
        hits = freq.get(qt, 0)
        if hits:
            score += 1.0 + math.log1p(hits - 1)
    return score


def rank_chunks_lexical(
    query: str,
    chunks: list[dict[str, Any]],
    *,
    top_n: int,
) -> list[dict[str, Any]]:
    """Return chunks sorted by lexical_score desc, stable on chunk_id."""
    scored: list[tuple[float, str, dict[str, Any]]] = []
    for row in chunks:
        cid = str(row.get("chunk_id") or "")
        sc = lexical_score(query, str(row.get("text") or ""))
        scored.append((sc, cid, row))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [row for sc, _, row in scored[:top_n] if sc > 0] or [row for _, _, row in scored[:top_n]]
