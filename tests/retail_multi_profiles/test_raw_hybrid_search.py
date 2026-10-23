"""P1.1 — raw hybrid RRF + SKU filter on fixture Lance index."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.retail_multi_profiles.lib.lanes import Lane
from tests.retail_multi_profiles.lib.raw_hybrid_search import hybrid_rrf_search
from tests.retail_multi_profiles.lib.raw_rag_index import build_index_for_lane

pytest.importorskip("lancedb")


def _fake_embed(texts: list[str]) -> list[list[float]]:
    """Deterministic vectors: longer shared prefix → closer to query embedding."""
    out: list[list[float]] = []
    for t in texts:
        n = min(len(t), 64)
        out.append([n / 64.0, 1.0 - n / 64.0, 0.5, 0.25])
    return out


@pytest.fixture
def dual_sku_lane(tmp_path: Path) -> Lane:
    """Two SKU folders: GE has strong lexical alarm text; Samsung has generic text."""
    for model, text in (
        ("ge_GNE27JYMFS", "Door alarm reset procedure for GE refrigerator.\n" * 40),
        ("samsung_RF28K9070SG", "Ice maker troubleshooting steps only.\n" * 40),
    ):
        raw_dir = tmp_path / "raw" / "sources" / "fridge-docs_md" / model
        raw_dir.mkdir(parents=True)
        (raw_dir / "guide.md").write_text(text, encoding="utf-8")
    return Lane(
        lane_id="T",
        project_path=tmp_path,
        ingest_kind="external_markdown",
        raw_rag_enabled=True,
        raw_glob="raw/sources/fridge-docs_md/**/*.md",
    )


def test_hybrid_rrf_respects_sku_filter(dual_sku_lane: Lane) -> None:
    """Wrong-SKU chunks must not appear when model_id scopes the query."""
    embed_cfg = {"provider": "openai", "model": "test-model"}
    build_index_for_lane(dual_sku_lane, embed_cfg, embed_fn=_fake_embed)
    query = "samsung_RF28K9070SG door alarm reset"
    hits = hybrid_rrf_search(
        dual_sku_lane,
        query,
        model_id="samsung_RF28K9070SG",
        embed_cfg=embed_cfg,
        top_k=5,
        embed_fn=_fake_embed,
    )
    assert hits
    for h in hits:
        mid = str(h.get("model_id") or "")
        assert mid.lower() == "samsung_rf28k9070sg"


def test_hybrid_rrf_beats_vector_only_lexical_winner(dual_sku_lane: Lane) -> None:
    """RRF should prefer samsung hit when scoped even if GE text matches query tokens better."""
    embed_cfg = {"provider": "openai", "model": "test-model"}
    build_index_for_lane(dual_sku_lane, embed_cfg, embed_fn=_fake_embed)
    query = "samsung_RF28K9070SG ice maker"
    hits = hybrid_rrf_search(
        dual_sku_lane,
        query,
        model_id="samsung_RF28K9070SG",
        embed_cfg=embed_cfg,
        top_k=3,
        embed_fn=_fake_embed,
    )
    assert hits[0]["model_id"] == "samsung_RF28K9070SG"
    assert "ice" in str(hits[0].get("text") or "").lower()
