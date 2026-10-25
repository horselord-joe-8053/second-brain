"""Context assembly for raw RAG hits (total budget + per-chunk cap)."""

from __future__ import annotations

from tests.retail_multi_profiles.lib.raw_rag_search import concat_top_k_raw_chunks


def test_concat_respects_total_budget() -> None:
    hits = [
        {"source_relpath": "a.md", "text": "x" * 5000},
        {"source_relpath": "b.md", "text": "y" * 5000},
    ]
    ctx = concat_top_k_raw_chunks(hits, page_prefix_chars=6000, max_chars_per_chunk=0)
    assert len(ctx) <= 6000 + 50
    assert "b.md" not in ctx


def test_concat_per_chunk_cap_before_total_budget() -> None:
    hits = [
        {"source_relpath": "a.md", "text": "a" * 4000},
        {"source_relpath": "b.md", "text": "b" * 4000},
    ]
    ctx = concat_top_k_raw_chunks(hits, page_prefix_chars=8000, max_chars_per_chunk=500)
    assert "a" * 501 not in ctx
    assert "b.md" in ctx
