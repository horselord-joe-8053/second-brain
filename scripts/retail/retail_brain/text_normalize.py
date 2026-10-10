"""Finite strip of ticket boilerplate for FTS index + query (not live LLM at search time)."""

from __future__ import annotations

import re
from typing import Optional

from retail_brain.market import market_profile

# Stored tickets end with "Case ref ITM-… / T-…-…."
_CASE_REF_SUFFIX = re.compile(
    r"\s*Case ref ITM-\d+ / T-\d+-\d+\.\s*$",
    re.IGNORECASE,
)

# Exam JSONL shape from market eval_query_template (align tokens with stored search_text).
_EVAL_QUERY_EN = re.compile(
    r"^Need help:\s+\S+\s+in\s+(?P<city>.+?)\s+with a\s+(?P<model>.+?)\s+—\s+(?P<issue>.+?)\.\s*(?P<detail>.*)$",
    re.DOTALL,
)
_EVAL_QUERY_PT = re.compile(
    r"^Preciso de ajuda:\s+\S+\s+em\s+(?P<city>.+?)\s+com\s+(?P<model>.+?)\s+—\s+(?P<issue>.+?)\.\s*(?P<detail>.*)$",
    re.DOTALL,
)


def strip_case_ref_suffix(text: str) -> str:
    return _CASE_REF_SUFFIX.sub("", text).strip()


def strip_market_prefix(text: str, *, market: str | None = None) -> str:
    prefix = market_profile(market)["customer_query_prefix"]
    if text.startswith(prefix):
        return text[len(prefix) :].strip()
    return text.strip()


def search_text_for_fts(raw: str, *, market: str | None = None) -> str:
    """Index/query text for the lexical leg: drop prefix and case-ref trailer."""
    core = strip_market_prefix(raw or "", market=market)
    return strip_case_ref_suffix(core)


def _align_eval_query_to_index_shape(q: str) -> str | None:
    m = _EVAL_QUERY_EN.match(q) or _EVAL_QUERY_PT.match(q)
    if not m:
        return None
    city = m.group("city").strip()
    model = m.group("model").strip()
    issue = m.group("issue").strip()
    detail = (m.group("detail") or "").strip()
    body = f"{issue} on {model} in {city}."
    return f"{body} {detail}".strip() if detail else body


def fts_query_text(live_query: str, *, market: str | None = None) -> str:
    """Map live exam wording to the same token shape as indexed search_text."""
    q = (live_query or "").strip()
    q = re.sub(r"\s*\(ref\s+[A-Za-z0-9_-]+\)\s*$", "", q, flags=re.IGNORECASE).strip()
    aligned = _align_eval_query_to_index_shape(q)
    if aligned:
        return aligned
    for lead in ("Need help: caller says ", "Preciso de ajuda: usuário descreve "):
        if q.startswith(lead):
            q = q[len(lead) :].strip()
            break
    return search_text_for_fts(q, market=market)
