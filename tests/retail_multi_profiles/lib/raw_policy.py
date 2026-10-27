"""Shared constants for raw-sources RAG chunking and index metadata."""

from __future__ import annotations

import os

RAW_RAG_DIRNAME = ".retail-raw-rag"

_CHUNK_V1 = "v1-char-2000-overlap-200"
_CHUNK_V2_PAGE = "v2-page-heading-max2000"


def manual_d2_chunk_policy() -> str:
    """D2 chunk policy: ``fixed_2k`` (default) or ``page_heading`` (evo-18 P2)."""
    return (os.environ.get("RETAIL_MANUAL_D2_CHUNK") or "fixed_2k").strip().lower()


def manual_d2_page_pack_mode() -> str:
    """Sub-knob when D2=page_heading: ``global_top5`` or ``page_top5`` (per source file cap)."""
    return (os.environ.get("RETAIL_D2_PAGE_PACK") or "global_top5").strip().lower()


def d7_query_mode() -> str:
    """D7 orchestration: ``none`` or ``decompose`` (multi-unit manual retrieval)."""
    return (os.environ.get("RETAIL_D7") or "none").strip().lower()


def manual_lexical_backend_name() -> str:
    """Manual keyword leg: ``tantivy`` (T0) or ``overlap`` (legacy)."""
    return (os.environ.get("RETAIL_MANUAL_LEXICAL_BACKEND") or "tantivy").strip().lower()


def chunk_policy_version_for_meta() -> str:
    """Resolve stored chunk_policy_version string from env D2 policy."""
    if manual_d2_chunk_policy() == "page_heading":
        return _CHUNK_V2_PAGE
    return _CHUNK_V1
