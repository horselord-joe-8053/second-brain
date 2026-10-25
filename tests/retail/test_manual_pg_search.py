"""P3 — manual PG hybrid search (RRF over PG-loaded pool)."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from retail_brain.manual_pg_search import hybrid_pg_rrf_search
from tests.retail_multi_profiles.lib.lanes import Lane


def _fake_embed(texts: list[str]) -> list[list[float]]:
    out: list[list[float]] = []
    for t in texts:
        n = min(len(t), 64)
        out.append([n / 64.0, 1.0 - n / 64.0, 0.5] * 512)
    return out


@pytest.fixture
def lane(tmp_path: Path) -> Lane:
    return Lane(
        lane_id="B",
        project_path=tmp_path,
        ingest_kind="external_markdown",
        raw_rag_enabled=True,
        raw_glob="raw/sources/**/*.md",
    )


def test_hybrid_pg_rrf_respects_sku_filter(lane: Lane, monkeypatch: pytest.MonkeyPatch) -> None:
    """PG hybrid path filters pool by model_id like Lance hybrid."""
    pool = [
        {
            "chunk_id": "a",
            "model_id": "ge_GNE27JYMFS",
            "text": "door alarm reset GE",
            "vector": _fake_embed(["door alarm"])[0],
        },
        {
            "chunk_id": "b",
            "model_id": "samsung_RF28K9070SG",
            "text": "ice maker samsung",
            "vector": _fake_embed(["ice maker"])[0],
        },
    ]

    monkeypatch.setattr(
        "retail_brain.manual_pg_search.ensure_manual_pg_fresh",
        lambda *_a, **_k: {},
    )

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

    monkeypatch.setattr(
        "retail_brain.manual_pg_search.list_manual_chunks",
        lambda _cur, *, lane_id, limit: list(pool),
    )
    import psycopg2

    monkeypatch.setattr(psycopg2, "connect", lambda _dsn: FakeConn())

    embed_cfg = {"provider": "openai", "model": "test-model"}
    hits = hybrid_pg_rrf_search(
        "postgresql://fake",
        lane,
        "samsung_RF28K9070SG ice maker",
        model_id="samsung_RF28K9070SG",
        embed_cfg=embed_cfg,
        top_k=3,
        embed_fn=_fake_embed,
    )
    assert hits
    for h in hits:
        assert str(h.get("model_id") or "").lower() == "samsung_rf28k9070sg"
