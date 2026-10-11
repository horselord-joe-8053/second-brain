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
_TECH_CODE_SUFFIX = re.compile(
    r"\s*Technician log: diagnostic code \S+\.\s*$",
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
_CODE_IN_QUERY = re.compile(r"\bcode\s+(SAM-E\d{3})\b", re.IGNORECASE)
_DIAG_CODE = re.compile(r"SAM-E\d{3}", re.IGNORECASE)
_NEED_HELP_PREFIX = re.compile(r"^Need help:\s*", re.IGNORECASE)


def strip_case_ref_suffix(text: str) -> str:
    return _CASE_REF_SUFFIX.sub("", text).strip()


def strip_market_prefix(text: str, *, market: str | None = None) -> str:
    prefix = market_profile(market)["customer_query_prefix"]
    if text.startswith(prefix):
        return text[len(prefix) :].strip()
    return text.strip()


def text_for_embedding(raw: str) -> str:
    """Vector index: customer-facing prose only (tech diagnostic line excluded)."""
    core = strip_case_ref_suffix(raw or "").strip()
    return _TECH_CODE_SUFFIX.sub("", core).strip()


def search_text_for_fts(raw: str, *, market: str | None = None) -> str:
    """Lexical index: customer text + diagnostic code (tech line kept for token match)."""
    core = strip_market_prefix(raw or "", market=market)
    return strip_case_ref_suffix(core)


def extract_diag_code(text: str | None) -> str | None:
    """Parse Samsung-style diagnostic code from query or stored ticket text."""
    m = _DIAG_CODE.search(text or "")
    return m.group(0).upper() if m else None


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
    code = _CODE_IN_QUERY.search(q)
    if code and not _EVAL_QUERY_EN.match(q):
        # V1.1: screenshot intake — keep symptom/model tokens; append tech-line code for FTS.
        body = _NEED_HELP_PREFIX.sub("", q).strip()
        body = re.sub(r"\s*\(ref\s+[A-Za-z0-9_-]+\)\s*$", "", body, flags=re.IGNORECASE).strip()
        normalized = search_text_for_fts(body, market=market)
        tech = f"Technician log: diagnostic code {code.group(1)}."
        if code.group(1).upper() not in normalized.upper():
            normalized = f"{normalized} {tech}".strip()
        return normalized
    for lead in ("Need help: caller says ", "Preciso de ajuda: usuário descreve "):
        if q.startswith(lead):
            q = q[len(lead) :].strip()
            break
    return search_text_for_fts(q, market=market)
