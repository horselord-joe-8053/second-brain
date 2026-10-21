"""Retrieve wiki context per lane and produce an answer string."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[3]
RETAIL_PKG = REPO / "scripts" / "retail"
if str(RETAIL_PKG) not in sys.path:
    sys.path.insert(0, str(RETAIL_PKG))

from retail_brain.answer_manuals import LlmWikiHttpClient  # noqa: E402
from retail_brain.wiki_page_context import concat_top_k_wiki_pages  # noqa: E402

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
) -> tuple[list[dict[str, Any]], str, int]:
    """Search and read top wiki pages; return hits, context text, retrieval latency ms."""
    return concat_top_k_wiki_pages(
        wiki, query, top_k=top_k, page_prefix_chars=page_prefix_chars
    )


def answer_from_context(
    question: str,
    context: str,
    *,
    provider: str,
    model: str,
    temperature: float = 0.0,
) -> tuple[str, int]:
    """One LLM call with fixed system-style prompt."""
    prompt = (
        "Answer using ONLY the manual excerpts below. If the excerpts do not contain "
        "enough information, reply exactly: Insufficient_Information_Based_On_Given_PDF\n\n"
        f"Question: {question}\n\nExcerpts:\n{context or '(no excerpts)'}"
    )
    t0 = time.perf_counter()
    text = llm_generate(prompt, provider=provider, model=model, temperature=temperature)
    latency_ms = int((time.perf_counter() - t0) * 1000)
    return text.strip(), latency_ms
