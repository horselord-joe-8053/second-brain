"""Tests for Lance raw index build and search."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.retail_multi_profiles.lib.lanes import Lane
from tests.retail_multi_profiles.lib.raw_rag_index import (
    build_index_for_lane,
    index_is_fresh,
    vector_search,
)


@pytest.fixture
def mini_lane(tmp_path: Path) -> Lane:
    """Lane with one small raw markdown file."""
    raw_dir = tmp_path / "raw" / "sources" / "fridge-docs_md" / "ge_GNE27JYMFS"
    raw_dir.mkdir(parents=True)
    (raw_dir / "user-guide.md").write_text(
        "Door alarm reset procedure for GE refrigerator.\n" * 50,
        encoding="utf-8",
    )
    return Lane(
        lane_id="T",
        project_path=tmp_path,
        ingest_kind="external_markdown",
        raw_rag_enabled=True,
        raw_glob="raw/sources/fridge-docs_md/**/*.md",
    )


def _fake_embed(texts: list[str]) -> list[list[float]]:
    """Deterministic 4-d vectors for ANN tests."""
    out: list[list[float]] = []
    for t in texts:
        score = float(len(t) % 7) / 7.0
        out.append([score, 1.0 - score, 0.5, 0.25])
    return out


lancedb = pytest.importorskip("lancedb")


def test_build_and_search(mini_lane: Lane) -> None:
    """P3: index rows and vector_search returns ordered hits."""
    embed_cfg = {"provider": "openai", "model": "test-model"}
    meta = build_index_for_lane(mini_lane, embed_cfg, embed_fn=_fake_embed)
    assert meta["chunk_count"] >= 1
    assert index_is_fresh(mini_lane, embed_cfg=embed_cfg)
    q = _fake_embed(["door alarm"])[0]
    hits = vector_search(mini_lane, q, top_k=3)
    assert hits
    assert hits[0].get("source_relpath")


def test_empty_table_search(tmp_path: Path) -> None:
    """Missing index table → empty hits."""
    lane = Lane(
        lane_id="E",
        project_path=tmp_path,
        ingest_kind="x",
        raw_rag_enabled=True,
        raw_glob="none/**/*.md",
    )
    hits = vector_search(lane, [0.0, 1.0, 0.0, 0.0], top_k=5)
    assert hits == []
