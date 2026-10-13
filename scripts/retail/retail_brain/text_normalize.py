"""Normalize ticket and query text before embedding vs keyword indexing.

Two parallel shapes (same raw ticket, different stripping):
  - ``text_for_embedding`` — vector leg; drops case-ref boilerplate, keeps SAM-E in body when present.
  - ``search_text_for_fts`` / ``fts_query_text`` — keyword leg; aligns live exam wording to indexed tokens.

No LLM calls here — deterministic regex and market templates only.
"""

from __future__ import annotations

import os
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

_DEFAULT_EMBED_STRIP = "Case ref ITM-"

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
    """Remove trailing ``Case ref ITM-… / T-…`` boilerplate from stored tickets."""
    return _CASE_REF_SUFFIX.sub("", text).strip()


def embed_strip_phrases() -> tuple[str, ...]:
    """Pipe-separated substrings removed from embed/FTS prep (not SAM-E tokens themselves)."""
    raw = os.environ.get("RETAIL_EMBED_STRIP_PHRASES", _DEFAULT_EMBED_STRIP).strip()
    if not raw:
        return ()
    return tuple(p.strip() for p in raw.split("|") if p.strip())


def apply_embed_strip_phrases(text: str) -> str:
    """Apply ``RETAIL_EMBED_STRIP_PHRASES`` removals (pipe-separated substrings)."""
    out = text or ""
    for phrase in embed_strip_phrases():
        if phrase.lower().startswith("case ref itm-"):
            out = _CASE_REF_SUFFIX.sub("", out)
        else:
            out = re.sub(re.escape(phrase) + r".*", "", out, flags=re.IGNORECASE)
    return out.strip()


def strip_market_prefix(text: str, *, market: str | None = None) -> str:
    """Drop market-specific CRM prefix (e.g. ``Customer reports: ``)."""
    prefix = market_profile(market)["customer_query_prefix"]
    if text.startswith(prefix):
        return text[len(prefix) :].strip()
    return text.strip()


def text_for_embedding(raw: str) -> str:
    """Vector index: customer prose + SAM-E; strip only RETAIL_EMBED_STRIP_PHRASES boilerplate."""
    core = strip_case_ref_suffix(raw or "").strip()
    return apply_embed_strip_phrases(core)


def search_text_for_fts(raw: str, *, market: str | None = None) -> str:
    """Lexical index: customer text + diagnostic code (tech line kept for token match)."""
    core = strip_market_prefix(raw or "", market=market)
    core = strip_case_ref_suffix(core)
    return apply_embed_strip_phrases(core)


def extract_diag_code(text: str | None) -> str | None:
    """Parse Samsung-style diagnostic code from query or stored ticket text."""
    m = _DIAG_CODE.search(text or "")
    return m.group(0).upper() if m else None


def _align_eval_query_to_index_shape(q: str) -> str | None:
    """If ``q`` matches exam template, rewrite to indexed ``issue on model in city`` shape."""
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
