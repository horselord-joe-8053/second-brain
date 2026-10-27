"""P4 — D7 query unit splitting."""

from __future__ import annotations

from retail_brain.manual_query_decompose import split_query_units


def test_split_query_units_on_sentences() -> None:
    """Compound question yields multiple units."""
    q = "What is the water pressure range? Also how long should I run the dispenser?"
    units = split_query_units(q)
    assert len(units) >= 2


def test_short_query_stays_single_unit() -> None:
    """Single short question is not over-split."""
    assert split_query_units("ice maker reset") == ["ice maker reset"]
