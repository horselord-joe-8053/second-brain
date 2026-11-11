"""Retrieve wiki context per lane and produce an answer string."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List

REPO = Path(__file__).resolve().parents[3]
RETAIL_PKG = REPO / "scripts" / "retail"
if str(RETAIL_PKG) not in sys.path:
    sys.path.insert(0, str(RETAIL_PKG))

from retail_brain.answer_manuals import LlmWikiHttpClient  # noqa: E402
from retail_brain.wiki_page_context import concat_hit_pages, concat_top_k_wiki_pages  # noqa: E402

from .llm_generate import llm_generate


def scoped_query(template: str, *, model_id: str, question: str) -> str:
    """Fill run-config query template."""
    return template.format(model_id=model_id, question=question)


def retrieve_context(
    wiki: LlmWikiHttpClient,
    query: str,
    *,
    top_k: int,
    page_prefix_chars: int = 8000,
    wiki_evidence: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], str, int]:
    """Search, optional wiki_evidence filter, read pages; return hits, context, latency ms."""
    from .wiki_evidence import apply_wiki_evidence_mode, wiki_evidence_settings

    t0 = time.perf_counter()
    hits = wiki.search(query, limit=top_k)
    ev = wiki_evidence_settings(wiki_evidence or {})
    hits = apply_wiki_evidence_mode(
        hits,
        mode=str(ev["mode"]),
        sources_prefix=str(ev["sources_prefix"]),
    )
    context, _read_ms = concat_hit_pages(wiki, hits, page_prefix_chars=page_prefix_chars)
    latency_ms = int((time.perf_counter() - t0) * 1000)
    return hits, context, latency_ms


def answer_from_context(
    question: str,
    context: str,
    *,
    provider: str,
    model: str,
    temperature: float = 0.0,
    preamble: str = "",
    insight_mode: bool = False,
    generate: Callable[..., str] | None = None,
) -> tuple[str, int]:
    """One LLM call with a fixed prompt. ``generate`` overrides the live LLM in tests."""
    if insight_mode:
        lead = (preamble or "[provisional insight]").strip()
        prompt = (
            f"{lead}\n"
            "Answer as organizational orientation using ONLY the excerpts below. "
            "Label uncertainty when excerpts are thin.\n\n"
            f"Question: {question}\n\nExcerpts:\n{context or '(no excerpts)'}"
        )
    else:
        prompt = (
            "Answer using ONLY the manual excerpts below. If the excerpts do not contain "
            "enough information, reply exactly: Insufficient_Information_Based_On_Given_PDF\n\n"
            f"Question: {question}\n\nExcerpts:\n{context or '(no excerpts)'}"
        )
    if preamble and not insight_mode:
        prompt = f"{preamble.strip()}\n\n{prompt}"
    t0 = time.perf_counter()
    fn = generate or llm_generate
    text = fn(prompt, provider=provider, model=model, temperature=temperature)
    latency_ms = int((time.perf_counter() - t0) * 1000)
    return text.strip(), latency_ms
