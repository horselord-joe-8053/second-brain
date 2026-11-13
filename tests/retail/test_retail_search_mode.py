"""RETAIL_TICKET_SEARCH_MODE and legacy hybrid flag."""

import os

from retail_brain.search_mode import (
    code_boost_enabled,
    resolve_ticket_search_mode,
    rrf_list_weights,
)


def test_default_vector_only() -> None:
    os.environ.pop("RETAIL_TICKET_SEARCH_MODE", None)
    os.environ["RETAIL_TICKET_HYBRID_SEARCH"] = "0"
    assert resolve_ticket_search_mode() == "vector_only"


def test_legacy_hybrid_maps_to_rrf_normal() -> None:
    os.environ.pop("RETAIL_TICKET_SEARCH_MODE", None)
    os.environ["RETAIL_TICKET_HYBRID_SEARCH"] = "1"
    assert resolve_ticket_search_mode() == "rrf_normal"


def test_explicit_term_boosted() -> None:
    """V1.2 uses equal RRF weights plus SAM-E term boost only."""
    os.environ["RETAIL_TICKET_SEARCH_MODE"] = "rrf_term_boosted"
    assert resolve_ticket_search_mode() == "rrf_term_boosted"
    assert code_boost_enabled()
    assert rrf_list_weights() == (0.5, 0.5)


def test_rrf_normal_equal_weights_no_boost() -> None:
    os.environ["RETAIL_TICKET_SEARCH_MODE"] = "rrf_normal"
    assert not code_boost_enabled()
    assert rrf_list_weights() == (0.5, 0.5)
