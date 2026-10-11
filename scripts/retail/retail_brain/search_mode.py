"""Ticket search mode: V1 vector-only through V1.3 weighted RRF + code boost."""

from __future__ import annotations

import os

VALID_MODES = (
    "vector_only",
    "rrf_normal",
    "rrf_weighted",
    "rrf_weighted_boosted",
)


def resolve_ticket_search_mode() -> str:
    """RETAIL_TICKET_SEARCH_MODE wins; legacy RETAIL_TICKET_HYBRID_SEARCH maps to rrf_normal."""
    explicit = os.environ.get("RETAIL_TICKET_SEARCH_MODE", "").strip().lower()
    if explicit in VALID_MODES:
        return explicit
    legacy = os.environ.get("RETAIL_TICKET_HYBRID_SEARCH", "0").strip().lower()
    if legacy in ("1", "true", "yes"):
        return "rrf_normal"
    return "vector_only"


def is_hybrid_mode(mode: str | None = None) -> bool:
    mode = mode or resolve_ticket_search_mode()
    return mode != "vector_only"


def rrf_list_weights(mode: str | None = None) -> tuple[float, float]:
    mode = mode or resolve_ticket_search_mode()
    if mode in ("rrf_weighted", "rrf_weighted_boosted"):
        return 0.7, 0.3
    return 0.5, 0.5


def code_boost_enabled(mode: str | None = None) -> bool:
    mode = mode or resolve_ticket_search_mode()
    return mode == "rrf_weighted_boosted"


def lexical_code_boost_lambda() -> float:
    return float(os.environ.get("RETAIL_LEXICAL_CODE_BOOST", "10"))
