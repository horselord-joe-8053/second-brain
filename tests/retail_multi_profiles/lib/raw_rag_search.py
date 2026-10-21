"""Query raw Lance index and build evidence context for the answer LLM."""

from __future__ import annotations

import time
from typing import Any

from .lanes import Lane
from .raw_embed import embed_texts_batch
from .raw_rag_index import ensure_index_fresh, vector_search


def concat_top_k_raw_chunks(
    hits: list[dict[str, Any]],
    *,
    page_prefix_chars: int,
) -> str:
    """Join chunk texts up to a character budget (mirrors wiki page_prefix policy)."""
    parts: list[str] = []
    used = 0
    for h in hits:
        rel = str(h.get("source_relpath") or "")
        text = str(h.get("text") or "")
        block = f"--- {rel} ---\n{text}"
        if used + len(block) > page_prefix_chars and parts:
            break
        parts.append(block)
        used += len(block) + 2
    return "\n\n".join(parts)


def retrieve_raw_context(
    lane: Lane,
    query: str,
    *,
    embed_cfg: dict[str, Any],
    top_k: int,
    page_prefix_chars: int,
    force_reindex: bool = False,
    skip_index_check: bool = False,
    embed_fn: Any | None = None,
) -> tuple[list[dict[str, Any]], str, int]:
    """Ensure index, embed query, vector top-k, return hits + context + latency ms."""
    t0 = time.perf_counter()
    ensure_index_fresh(
        lane,
        embed_cfg,
        force=force_reindex,
        skip_check=skip_index_check,
        embed_fn=embed_fn,
    )
    if embed_fn is not None:
        qvec = embed_fn([query])[0]
    else:
        qvec = embed_texts_batch([query], embed_cfg)[0]
    hits = vector_search(lane, qvec, top_k=top_k)
    context = concat_top_k_raw_chunks(hits, page_prefix_chars=page_prefix_chars)
    ms = int((time.perf_counter() - t0) * 1000)
    return hits, context, ms
