"""P2 — page_heading chunk policy splits on Markdown headings."""

from __future__ import annotations

from tests.retail_multi_profiles.lib.raw_chunking import chunk_text_page_heading


def test_page_heading_splits_sections() -> None:
    """Two h2 sections become at least two chunks."""
    md = "# Title\n\n## Ice maker\nReset steps here.\n\n## Water filter\nReplace every six months."
    parts = chunk_text_page_heading(md, max_chars=2000)
    assert len(parts) >= 2
    assert any("Ice maker" in p for p in parts)
    assert any("Water filter" in p for p in parts)
