"""P2 — manual PG ingest manifest parity (strict-TDD)."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from retail_brain.manual_pg_ingest import (
    ensure_manual_pg_fresh,
    ingest_lane_to_pg,
    pg_index_is_fresh,
    read_manual_pg_meta,
)
from tests.retail_multi_profiles.lib.lanes import Lane


def _fake_embed(texts: list[str]) -> list[list[float]]:
    """Small deterministic vectors for ingest tests."""
    return [[0.1, 0.2, 0.3] * 512 for _ in texts]


@pytest.fixture
def tiny_lane(tmp_path: Path) -> Lane:
    """Single markdown source under raw glob."""
    raw_dir = tmp_path / "raw" / "sources" / "fridge-docs_md" / "sku_a"
    raw_dir.mkdir(parents=True)
    (raw_dir / "guide.md").write_text("Door alarm reset steps.\n" * 5, encoding="utf-8")
    return Lane(
        lane_id="B",
        project_path=tmp_path,
        ingest_kind="external_markdown",
        raw_rag_enabled=True,
        raw_glob="raw/sources/fridge-docs_md/**/*.md",
    )


def test_pg_index_is_fresh_false_without_meta(tiny_lane: Lane) -> None:
    """Missing manual_pg_meta.json must trigger rebuild."""
    embed_cfg = {"provider": "openai", "model": "test-model"}
    assert pg_index_is_fresh(tiny_lane, embed_cfg=embed_cfg) is False


def test_ingest_lane_to_pg_upserts_and_writes_meta(
    tiny_lane: Lane, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ingest calls schema apply, upsert, delete stale, and persists meta."""
    calls: dict[str, Any] = {"upsert": 0, "delete": 0}

    class FakeCursor:
        def execute(self, *_a, **_k) -> None:
            return None

        def __enter__(self):
            return self

        def __exit__(self, *_a) -> None:
            return None

    class FakeConn:
        def cursor(self):
            return FakeCursor()

        def commit(self) -> None:
            return None

        def close(self) -> None:
            return None

    import psycopg2

    monkeypatch.setattr(psycopg2, "connect", lambda _dsn: FakeConn())

    def _apply(_cur) -> None:
        calls["schema"] = True

    def _upsert(_cur, rows) -> int:
        calls["upsert"] = len(list(rows))
        return calls["upsert"]

    def _delete(_cur, *, lane_id: str, keep_ids: set[str]) -> int:
        calls["delete"] = len(keep_ids)
        return 0

    monkeypatch.setattr("retail_brain.manual_pg_ingest.apply_manual_chunks_schema", _apply)
    monkeypatch.setattr("retail_brain.manual_pg_ingest.upsert_manual_chunks", _upsert)
    monkeypatch.setattr("retail_brain.manual_pg_ingest.delete_manual_chunks_for_lane", _delete)

    embed_cfg = {"provider": "openai", "model": "test-model"}
    meta = ingest_lane_to_pg("postgresql://fake", tiny_lane, embed_cfg, embed_fn=_fake_embed)
    assert calls.get("schema") is True
    assert calls["upsert"] >= 1
    assert calls["delete"] >= 1
    assert meta.get("chunk_count", 0) >= 1
    saved = read_manual_pg_meta(tiny_lane)
    assert saved is not None
    assert saved.get("manifest_fingerprint") == meta.get("manifest_fingerprint")


def test_ensure_manual_pg_fresh_skips_when_fresh(
    tiny_lane: Lane, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fresh meta must not call ingest_lane_to_pg."""
    from retail_brain.manual_pg_ingest import write_manual_pg_meta
    from tests.retail_multi_profiles.lib.raw_chunking import chunk_policy_version
    from tests.retail_multi_profiles.lib.raw_embed import embed_model_id
    from tests.retail_multi_profiles.lib.raw_manifest import build_manifest, manifest_fingerprint

    embed_cfg = {"provider": "openai", "model": "test-model"}
    manifest = build_manifest(tiny_lane)
    write_manual_pg_meta(
        tiny_lane,
        {
            "lane_id": tiny_lane.lane_id,
            "chunk_policy_version": chunk_policy_version(),
            "embed_model_id": embed_model_id(embed_cfg),
            "manifest_fingerprint": manifest_fingerprint(manifest),
            "chunk_count": 1,
        },
    )
    mock_ingest = MagicMock()
    monkeypatch.setattr("retail_brain.manual_pg_ingest.ingest_lane_to_pg", mock_ingest)
    ensure_manual_pg_fresh("postgresql://fake", tiny_lane, embed_cfg)
    mock_ingest.assert_not_called()
