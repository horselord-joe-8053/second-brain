"""P3 — manual PG hybrid search (RRF over PG-loaded pool)."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from retail_brain.manual_pg_search import hybrid_pg_rrf_search
from retail_brain.product_scope import ProductFilter
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


def test_hybrid_pg_rrf_respects_product_filter(lane: Lane, monkeypatch: pytest.MonkeyPatch) -> None:
    """PG hybrid path filters pool by brand + OEM model."""
    monkeypatch.setenv("RETAIL_MANUAL_LEXICAL_BACKEND", "overlap")
    pool = [
        {
            "chunk_id": "a",
            "model_id": "ge_GNE27JYMFS",
            "brand": "GE",
            "oem_model": "GNE27JYMFS",
            "text": "door alarm reset GE",
            "vector": _fake_embed(["door alarm"])[0],
        },
        {
            "chunk_id": "b",
            "model_id": "samsung_RF28K9070SG",
            "brand": "Samsung",
            "oem_model": "RF28K9070SG",
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

    def _list_filtered(_cur, *, lane_id, limit, brand=None, oem_model=None):
        rows = list(pool)
        if brand:
            rows = [r for r in rows if r.get("brand") == brand]
        if oem_model:
            rows = [r for r in rows if r.get("oem_model") == oem_model]
        return rows

    monkeypatch.setattr(
        "retail_brain.manual_pg_search.list_manual_chunks",
        _list_filtered,
    )
    import psycopg2

    monkeypatch.setattr(psycopg2, "connect", lambda _dsn: FakeConn())

    embed_cfg = {"provider": "openai", "model": "test-model"}
    hits = hybrid_pg_rrf_search(
        "postgresql://fake",
        lane,
        "samsung_RF28K9070SG ice maker",
        product_filter=ProductFilter("Samsung", "RF28K9070SG"),
        ingest_key="samsung_RF28K9070SG",
        embed_cfg=embed_cfg,
        top_k=3,
        embed_fn=_fake_embed,
    )
    assert hits
    for h in hits:
        assert str(h.get("oem_model") or "") == "RF28K9070SG"
