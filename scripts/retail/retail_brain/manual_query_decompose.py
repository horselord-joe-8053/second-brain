"""D7 — split compound manual queries into retrieval units (sentence-safe, no LLM)."""

from __future__ import annotations

import re

_MIN_UNIT_LEN = 12
_SPLIT_RE = re.compile(r"(?<=[?.!])\s+")


def split_query_units(query: str, *, max_units: int = 4) -> list[str]:
    """Return 1..max_units non-empty clauses; fall back to full query when split is useless."""
    q = (query or "").strip()
    if not q:
        return [""]
    parts = [p.strip() for p in _SPLIT_RE.split(q) if p.strip()]
    units = [p for p in parts if len(p) >= _MIN_UNIT_LEN]
    if len(units) <= 1:
        return [q]
    return units[:max_units]
