"""Operator ingest runner writes JSONL checkpoint and summary."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


def test_run_ingest_manual_pg_writes_progress_jsonl(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MANUAL_PG_INGEST path records ingest_progress.jsonl per lane."""
    from tests.retail_multi_profiles.lib import manual_pg_index_runner as mod
    from tests.retail_multi_profiles.lib.lanes import Lane

    fake_lane = Lane(
        lane_id="B",
        project_path=REPO / "brain" / "retail-md",
        brain_relpath="brain/retail-md",
        ingest_kind="raw_md",
        raw_rag_enabled=True,
        raw_glob="**/*.md",
    )

    def fake_load_lanes(_root: Path) -> dict[str, Lane]:
        return {"B": fake_lane}

    def fake_ensure(
        _dsn: str,
        lane: Lane,
        _embed_cfg: dict,
        *,
        force: bool = False,
        skip_check: bool = False,
        embed_fn=None,
    ) -> dict:
        return {"lane_id": lane.lane_id, "chunk_count": 3, "embed_model_id": "test-model"}

    monkeypatch.setattr(mod, "load_lanes", fake_load_lanes)
    monkeypatch.setattr(
        mod,
        "load_merged_run_config",
        lambda _root: {"retail_raw_rag": {"embedding": {"model": "text-embedding-3-small"}}},
    )

    out = mod.run_ingest_manual_pg(
        tmp_path,
        dsn="postgresql://local/test",
        lane_ids=["B"],
        run_id="test-ingest-v1",
        ensure_fn=fake_ensure,
    )
    assert out.is_dir()
    jsonl = out / "ingest_progress.jsonl"
    assert jsonl.is_file()
    lines = [json.loads(ln) for ln in jsonl.read_text(encoding="utf-8").splitlines() if ln.strip()]
    steps = [r["step"] for r in lines if r.get("type") == "progress"]
    assert steps == ["ingest_lane_start", "ingest_lane_done"]
    started = next(r for r in lines if r.get("step") == "ingest_lane_start")
    sources = set(started["source_relpaths"])
    assert "raw/sources/fridge-news_md/GE_GNE27JYMFS_news.md" in sources
    assert "raw/sources/fridge-news_md/KitchenAid_KRFF507HPS_news.md" in sources
    assert "raw/sources/fridge-news_md/Samsung_RF28K9070SG_news.md" in sources
    summary = json.loads((out / "ingest_summary.json").read_text(encoding="utf-8"))
    assert summary["run_id"] == "test-ingest-v1"
    assert summary["lanes"]["B"]["chunk_count"] == 3
