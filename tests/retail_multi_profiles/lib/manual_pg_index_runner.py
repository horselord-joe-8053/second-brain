"""CLI entry to ingest manual chunks into Postgres with operator logging."""

from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from logging_utils.run_progress import write_jsonl_line
from utils.neat_logger.neat_logger_instance import NeatLoggerFactory

from .lanes import Lane, load_lanes
from .raw_corpus import iter_raw_source_files
from .run_config import load_merged_run_config


def _git_head(repo: Path) -> str:
    """Best-effort commit hash for ingest run metadata."""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except Exception:
        return ""


def run_ingest_manual_pg(
    repo_root: Path,
    *,
    dsn: str,
    lane_ids: list[str],
    run_id: str | None = None,
    force_reindex: bool = False,
    skip_index_check: bool = False,
    ensure_fn: Any | None = None,
) -> Path:
    """Ingest or refresh manual_chunks and record each lane's source paths in the progress log."""
    from retail_brain.manual_pg_ingest import ensure_manual_pg_fresh

    fresh = ensure_fn or ensure_manual_pg_fresh
    cfg = load_merged_run_config(repo_root)
    embed_cfg = (cfg.get("retail_raw_rag") or {}).get("embedding") or {}
    lanes_map = load_lanes(repo_root)
    selected: list[Lane] = [lanes_map[lid] for lid in lane_ids]

    rid = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = repo_root / "ops" / "runs" / "retail-manual-pg-ingest" / rid
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "ingest_progress.jsonl"
    log = NeatLoggerFactory.create(
        "OPS",
        "MANUAL_PG_INGEST",
        log_file_name=f"retail-manual-pg-ingest-{rid.replace('/', '_')}.log",
        log_output="both",
    )

    log.step(f"manual PG ingest run_id={rid} lanes={lane_ids}")
    meta_by_lane: dict[str, Any] = {}
    for lane in selected:
        if not lane.raw_rag_enabled:
            raise ValueError(f"lane {lane.lane_id} is not raw_rag_enabled")
        source_relpaths = [
            item.source_relpath
            for item in iter_raw_source_files(lane.project_path, lane.raw_glob)
        ]
        write_jsonl_line(
            jsonl_path,
            {
                "type": "progress",
                "step": "ingest_lane_start",
                "lane": lane.lane_id,
                "source_relpaths": source_relpaths,
            },
        )
        t0 = time.perf_counter()
        with log.heartbeat(f"{lane.lane_id} chunk + embed + PG upsert"):
            meta = fresh(
                dsn,
                lane,
                embed_cfg,
                force=force_reindex,
                skip_check=skip_index_check,
            )
        elapsed = int(time.perf_counter() - t0)
        meta_by_lane[lane.lane_id] = meta
        write_jsonl_line(
            jsonl_path,
            {
                "type": "progress",
                "step": "ingest_lane_done",
                "lane": lane.lane_id,
                "elapsed_sec": elapsed,
                "chunk_count": meta.get("chunk_count"),
            },
        )
        log.info(
            f"lane {lane.lane_id} manual_pg chunks={meta.get('chunk_count')} sec={elapsed}"
        )

    summary = {
        "run_id": rid,
        "git_head": _git_head(repo_root),
        "lanes": meta_by_lane,
        "embed_model_id": meta_by_lane.get(lane_ids[0], {}).get("embed_model_id")
        if lane_ids
        else "",
    }
    (out_dir / "ingest_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    return out_dir
