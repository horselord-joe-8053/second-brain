"""P3.3 — wiki_evidence harness filters."""

from __future__ import annotations

from tests.retail_multi_profiles.lib.search_hits import is_wiki_source_path
from tests.retail_multi_profiles.lib.wiki_evidence import apply_wiki_evidence_mode


def test_sources_only_drops_concept_hits() -> None:
    """sources_only keeps wiki/sources paths only."""
    hits = [
        {"path": "wiki/concepts/foo.md", "score": 0.9},
        {"path": "wiki/sources/ge/manual.md", "score": 0.5},
    ]
    out = apply_wiki_evidence_mode(hits, mode="sources_only")
    assert len(out) == 1
    assert is_wiki_source_path(str(out[0]["path"]))


def test_sources_rerank_orders_by_score() -> None:
    """sources_rerank reorders filtered hits by score descending."""
    hits = [
        {"path": "wiki/sources/a.md", "score": 0.2},
        {"path": "wiki/sources/b.md", "score": 0.9},
    ]
    out = apply_wiki_evidence_mode(hits, mode="sources_rerank")
    assert out[0]["path"].endswith("b.md")


def test_uncertainty_label_when_contradicted() -> None:
    """Contradicted registry page → uncertainty label on cited hit."""
    import json
    from pathlib import Path

    from tests.retail_multi_profiles.lib.wiki_uncertainty import uncertainty_label_for_hits

    reg = Path(__file__).parent / "fixtures" / "wiki_uncertainty_mini" / "claims.jsonl"
    reg.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "page_relpath": "wiki/concepts/demo-page.md",
        "status": "contradicted",
        "claim": "x",
    }
    reg.write_text(json.dumps(row) + "\n", encoding="utf-8")
    label = uncertainty_label_for_hits(
        ["wiki/concepts/demo-page.md"],
        registry_path=reg,
        enabled=True,
    )
    assert label is not None
    assert "contradicted" in label.lower()
