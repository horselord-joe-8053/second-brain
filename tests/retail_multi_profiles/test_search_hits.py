"""Source-path filter and compact search-hit shape."""

from tests.retail_multi_profiles.lib.search_hits import (
    compact_search_hit,
    is_wiki_source_path,
    source_only_hits,
)


def test_source_filter_keeps_ranked_source_pages_only() -> None:
    """Entities and concepts drop out; source order stays the search order."""
    hits = [
        {"path": "wiki/entities/ge.md", "score": 0.9},
        {"path": "wiki/sources/page-a.md", "score": 0.4},
        {"path": "wiki/concepts/filter.md", "score": 0.3},
        {"path": "wiki/sources/page-b.md", "score": 0.2},
    ]
    kept = source_only_hits(hits)
    assert [hit["path"] for hit in kept] == ["wiki/sources/page-a.md", "wiki/sources/page-b.md"]
    assert is_wiki_source_path("wiki/sources/page-a.md")
    assert not is_wiki_source_path("wiki/index.md")


def test_compact_search_hit_keeps_rank_signals() -> None:
    """Fused score and vector score survive; page body is not copied."""
    compact = compact_search_hit(
        {
            "path": "wiki/sources/a.md",
            "title": "A",
            "score": 0.03,
            "vectorScore": 0.8,
            "titleMatch": True,
            "snippet": "long",
        }
    )
    assert compact["vector_score"] == 0.8
    assert compact["score"] == 0.03
    assert "snippet" not in compact
