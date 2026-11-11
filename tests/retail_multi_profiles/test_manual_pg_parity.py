"""P3.3 — PG hybrid RRF stability on fixture corpus rows."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from retail_brain.manual_pg_ingest import _collect_chunk_rows
from retail_brain.manual_pg_search import hybrid_pg_rrf_search
from tests.retail_multi_profiles.lib.lanes import Lane


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
        brain_relpath="brain/retail-md",
        ingest_kind="external_markdown",
        raw_rag_enabled=True,
        raw_glob="raw/sources/fridge-docs_md/**/*.md",
    )


def test_pg_hybrid_top5_stable_on_fixture_pool(dual_lane: Lane) -> None:
    """RRF on a fixed PG-shaped pool returns deterministic top-5 for a SKU query."""
    embed_cfg = {"provider": "openai", "model": "test-model"}
    rows = _collect_chunk_rows(dual_lane, embed_cfg, embed_fn=_fake_embed)
    pool = [
        {
            "chunk_id": r["chunk_id"],
            "source_relpath": r["source_relpath"],
            "model_id": r["model_id"],
            "text": r["text"],
            "vector": r["embedding"],
        }
        for r in rows
    ]

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

    query = "samsung_RF28K9070SG ice maker"
    model_id = "samsung_RF28K9070SG"
    with patch("retail_brain.manual_pg_search.ensure_manual_pg_fresh", return_value={}):
        with patch("retail_brain.manual_pg_search.list_manual_chunks", return_value=pool):
            with patch("psycopg2.connect", return_value=FakeConn()):
                hits = hybrid_pg_rrf_search(
                    "postgresql://fake",
                    dual_lane,
                    query,
                    model_id=model_id,
                    embed_cfg=embed_cfg,
                    top_k=5,
                    embed_fn=_fake_embed,
                    skip_index_check=True,
                )
    assert hits
    ids = [str(h["chunk_id"]) for h in hits]
    assert len(ids) == len(set(ids))
    assert all(h.get("model_id") == model_id for h in hits)
