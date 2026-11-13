"""Bundled harness resolves TYPE_B_B20 suite model to brand + OEM model product scope."""

from __future__ import annotations

from retail_brain.product_scope import resolve_product_scope


def test_manual_filter_uses_brand_and_oem_not_ingest_slug() -> None:
    """GNE27JYMFS in TYPE_B_B20 must filter manuals on GE + GNE27JYMFS, not bare OEM or ge_* slug alone."""
    scope = resolve_product_scope(
        "GNE27JYMFS touch panel dead",
        suite_model="GNE27JYMFS",
        manual_anchor_question_id="ge_GNE27JYMFS-E02",
    )
    assert scope.manual_filter.brand == "GE"
    assert scope.manual_filter.oem_model == "GNE27JYMFS"
