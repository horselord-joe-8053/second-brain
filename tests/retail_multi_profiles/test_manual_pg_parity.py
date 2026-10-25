"""P3.3 — retrieval-only top-k overlap PG vs Lance on same fixture corpus."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from retail_brain.manual_pg_search import hybrid_pg_rrf_search
from tests.retail_multi_profiles.lib.lanes import Lane
from tests.retail_multi_profiles.lib.raw_hybrid_search import hybrid_rrf_search
from tests.retail_multi_profiles.lib.raw_rag_index import build_index_for_lane

pytest.importorskip("lancedb")


def _fake_embed(texts: list[str]) -> list[list[float]]:
    out: list[list[float]] = []
    for t in texts:
        n = min(len(t), 64)
        out.append([n / 64.0, 1.0 - n / 64.0, 0.5] * 512)
    return out


@pytest.fixture
def dual_lane(tmp_path: Path) -> Lane:
    for model, text in (
        ("ge_GNE27JYMFS", "Door alarm reset procedure.\n" * 30),
        ("samsung_RF28K9070SG", "Ice maker troubleshooting.\n" * 30),
    ):
        raw_dir = tmp_path / "raw" / "sources" / "fridge-docs_md" / model
        raw_dir.mkdir(parents=True)
        (raw_dir / "guide.md").write_text(text, encoding="utf-8")
    return Lane(
        lane_id="B",
        project_path=tmp_path,
        ingest_kind="external_markdown",
        raw_rag_enabled=True,
        raw_glob="raw/sources/fridge-docs_md/**/*.md",
    )


def test_pg_hybrid_top5_overlap_with_lance_fixture(dual_lane: Lane) -> None:
    """PG path with mocked DB pool copied from Lance should match top-5 chunk ids."""
    embed_cfg = {"provider": "openai", "model": "test-model"}
    build_index_for_lane(dual_lane, embed_cfg, embed_fn=_fake_embed)
    from tests.retail_multi_profiles.lib.raw_rag_index import list_index_chunks

    pool = list_index_chunks(dual_lane, limit=500)

    query = "samsung_RF28K9070SG ice maker"
    model_id = "samsung_RF28K9070SG"
    lance_hits = hybrid_rrf_search(
        dual_lane,
        query,
        model_id=model_id,
        embed_cfg=embed_cfg,
        top_k=5,
        embed_fn=_fake_embed,
        skip_index_check=True,
    )
    lance_ids = {str(h["chunk_id"]) for h in lance_hits}

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *_a) -> None:
            return None

    class FakeConn:
        def cursor(self):
            return FakeCursor()

        def close(self) -> None:
            return None

    with patch("retail_brain.manual_pg_search.ensure_manual_pg_fresh", return_value={}):
        with patch("retail_brain.manual_pg_search.list_manual_chunks", return_value=pool):
            with patch("psycopg2.connect", return_value=FakeConn()):
                pg_hits = hybrid_pg_rrf_search(
                    "postgresql://fake",
                    dual_lane,
                    query,
                    model_id=model_id,
                    embed_cfg=embed_cfg,
                    top_k=5,
                    embed_fn=_fake_embed,
                    skip_index_check=True,
                )
    pg_ids = {str(h["chunk_id"]) for h in pg_hits}
    assert pg_ids == lance_ids
