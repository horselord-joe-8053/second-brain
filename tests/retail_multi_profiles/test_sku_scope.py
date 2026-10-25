"""Central SKU scope: legit catalog, query parse, unknown rejection."""

from __future__ import annotations

import pytest

from tests.retail_multi_profiles.lib.sku_scope import (
    SkuScopeError,
    find_unknown_vendor_skus,
    resolve_retrieval_sku,
)


def test_resolve_single_sku_from_query() -> None:
    scope = resolve_retrieval_sku("samsung_RF28K9070SG door alarm")
    assert scope.filter_model_id == "samsung_RF28K9070SG"
    assert scope.source == "query_single"


def test_suite_fallback_when_query_has_no_sku_token() -> None:
    scope = resolve_retrieval_sku("door alarm reset", suite_model_id="ge_GNE27JYMFS")
    assert scope.filter_model_id == "ge_GNE27JYMFS"
    assert scope.source == "suite_fallback"


def test_multi_sku_query_opens_pool() -> None:
    q = "Compare samsung_RF28K9070SG and kitchenaid_KRFF507HPS ice makers"
    scope = resolve_retrieval_sku(q, suite_model_id="ge_GNE27JYMFS")
    assert scope.filter_model_id is None
    assert scope.source == "query_multi_open"
    assert len(scope.mentioned) == 2


def test_unknown_vendor_sku_raises() -> None:
    with pytest.raises(SkuScopeError, match="Unknown SKU"):
        resolve_retrieval_sku("samsung_RF28FAKE9999 temperature")


def test_find_unknown_vendor_skus() -> None:
    assert find_unknown_vendor_skus("ge_GNE27JYMFS ok") == []
    bad = find_unknown_vendor_skus("help with ge_GNE99ZZZZ")
    assert bad == ["ge_GNE99ZZZZ"]
