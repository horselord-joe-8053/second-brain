"""Build answer LLM context from retrieved manual chunk hits."""

from __future__ import annotations

from typing import Any


def concat_top_k_raw_chunks(
    hits: list[dict[str, Any]],
    *,
    page_prefix_chars: int,
    max_chars_per_chunk: int = 0,
) -> str:
    """Join chunk texts up to a total budget; optionally cap each chunk body."""
    parts: list[str] = []
    used = 0
    per_cap = max(0, int(max_chars_per_chunk or 0))
    for h in hits:
        rel = str(h.get("source_relpath") or "")
        text = str(h.get("text") or "")
        if per_cap > 0:
            text = text[:per_cap]
        block = f"--- {rel} ---\n{text}"
        if used + len(block) > page_prefix_chars and parts:
            break
        parts.append(block)
        used += len(block) + 2
    return "\n\n".join(parts)
