"""Product scope: catalog sku vs OEM model for multi-leg retrieval."""

from __future__ import annotations

from retail_brain.product_scope import resolve_product_scope


def test_b20_bare_oem_suite_maps_to_brand_model_on_both_legs() -> None:
    """BND-E01-style row: suite model GNE27JYMFS → GE + GNE27JYMFS on manual and ticket filters."""
    scope = resolve_product_scope(
        "GNE27JYMFS touch panel dead",
        suite_model="GNE27JYMFS",
        manual_anchor_question_id="ge_GNE27JYMFS-E02",
    )
    assert scope.brand == "GE"
    assert scope.oem_model == "GNE27JYMFS"
    assert scope.ingest_key == "ge_GNE27JYMFS"
    assert scope.manual_filter.brand == "GE"
    assert scope.manual_filter.oem_model == "GNE27JYMFS"
    assert scope.ticket_filter == scope.manual_filter


def test_query_with_ingest_token_resolves_brand_model() -> None:
    scope = resolve_product_scope(
        "samsung_RF28K9070SG ice maker",
        suite_model="GNE27JYMFS",
    )
    assert scope.brand == "Samsung"
    assert scope.oem_model == "RF28K9070SG"
    assert scope.ingest_key == "samsung_RF28K9070SG"
    assert scope.source == "query_single"
