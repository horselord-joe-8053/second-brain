"""Concatenate top-k LLM Wiki pages for agent or eval context (shared retrieval shape)."""

from __future__ import annotations

import time
from typing import Any, Protocol


class WikiSearchRead(Protocol):
    """Minimal search + read surface used by benchmark and future bundle modes."""

    def search(self, query: str, *, limit: int) -> list[dict[str, Any]]:
        """Ranked wiki hits with at least ``path``."""
        ...

    def read(self, path: str) -> str:
        """Full page text for a project-relative wiki path."""
        ...


def concat_hit_pages(
    wiki: WikiSearchRead,
    hits: list[dict[str, Any]],
    *,
    page_prefix_chars: int = 8000,
) -> tuple[str, int]:
    """Read the given hits and join page prefixes; return context and read latency ms."""
    t0 = time.perf_counter()
    chunks: list[str] = []
    cap = max(1, page_prefix_chars)
    for h in hits:
        path = str(h.get("path") or "")
        if not path:
            continue
        try:
            text = wiki.read(path)
        except Exception:
            continue
        chunks.append(f"--- {path} ---\n{text[:cap]}")
    latency_ms = int((time.perf_counter() - t0) * 1000)
    return "\n\n".join(chunks), latency_ms


def concat_top_k_wiki_pages(
    wiki: WikiSearchRead,
    query: str,
    *,
    top_k: int,
    page_prefix_chars: int = 8000,
) -> tuple[list[dict[str, Any]], str, int]:
    """Search, read each hit, return hits, concatenated context, retrieval latency ms."""
    t0 = time.perf_counter()
    hits = wiki.search(query, limit=top_k)
    context, _read_ms = concat_hit_pages(wiki, hits, page_prefix_chars=page_prefix_chars)
    latency_ms = int((time.perf_counter() - t0) * 1000)
    return hits, context, latency_ms
