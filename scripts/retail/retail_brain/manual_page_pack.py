"""D2.page_pack — cap hybrid candidates per source file before RRF (evo-18 P3)."""

from __future__ import annotations

from typing import Any


def page_key_for_chunk(row: dict[str, Any]) -> str:
    """Grouping key: source_relpath (one manual file ≈ one logical page in Lane B)."""
    return str(row.get("source_relpath") or row.get("chunk_id") or "")


def apply_page_pack_to_ranked_rows(
    ranked: list[dict[str, Any]],
    *,
    mode: str,
    per_page_k: int = 5,
) -> list[dict[str, Any]]:
    """When mode is ``page_top5``, keep at most ``per_page_k`` rows per source file (order preserved)."""
    if (mode or "").strip().lower() != "page_top5":
        return list(ranked)
    counts: dict[str, int] = {}
    out: list[dict[str, Any]] = []
    for row in ranked:
        key = page_key_for_chunk(row)
        n = counts.get(key, 0)
        if n >= per_page_k:
            continue
        counts[key] = n + 1
        out.append(row)
    return out
