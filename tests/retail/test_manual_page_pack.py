"""P3 — page_top5 caps candidates per source file."""

from __future__ import annotations

from retail_brain.manual_page_pack import apply_page_pack_to_ranked_rows


def test_page_top5_limits_per_source_relpath() -> None:
    """Six rows from one file collapse to five under page_top5."""
    rows = [
        {"chunk_id": f"c{i}", "source_relpath": "a.md", "text": f"t{i}"}
        for i in range(6)
    ]
    out = apply_page_pack_to_ranked_rows(rows, mode="page_top5", per_page_k=5)
    assert len(out) == 5
    assert apply_page_pack_to_ranked_rows(rows, mode="global_top5", per_page_k=5) == rows
