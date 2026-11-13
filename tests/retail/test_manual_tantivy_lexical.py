"""Manual Tantivy BM25 ranks substantive terms above stopword overlap (evo-18 T0)."""

from __future__ import annotations

import pytest

pytest.importorskip("tantivy")

from retail_brain.lexical_search.manual_tantivy_index import ManualTantivyLexicalIndex


def test_manual_tantivy_prefers_pressure_spec_over_generic_chunk(tmp_path) -> None:
    """Gold-like chunk with psi range outranks generic ambient prose for a pressure query."""
    idx = ManualTantivyLexicalIndex(path=tmp_path / "manual_tix")
    rows = [
        (
            "noise_chunk",
            "The refrigerator is quiet in normal operation. The and a the ambient sound level.",
            "GE",
            "GNE27JYMFS",
        ),
        (
            "pressure_chunk",
            "Water supply pressure must be between 25 and 120 psi for the ice maker.",
            "GE",
            "GNE27JYMFS",
        ),
    ]
    idx.rebuild(rows)
    hits = idx.search_scored(
        "GNE27JYMFS water supply pressure range psi ice maker",
        k=2,
        brand_filter="GE",
        oem_model_filter="GNE27JYMFS",
    )
    assert hits[0][0] == "pressure_chunk"
