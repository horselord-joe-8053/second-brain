"""CLI entry to build raw Lance indexes with operator logging."""

from __future__ import annotations

import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from logging_utils.run_progress import write_jsonl_line
from utils.neat_logger.neat_logger_instance import NeatLoggerFactory

from .lanes import load_lanes
from .raw_rag_index import build_index_for_lane, ensure_index_fresh
from .run_config import load_merged_run_config


def _git_head(repo: Path) -> str:
    """Best-effort commit hash for index run metadata."""
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


def run_index_raw(
    repo_root: Path,
    *,
    lane_ids: list[str],
    run_id: str | None = None,
    force_reindex: bool = False,
    skip_index_check: bool = False,
) -> Path:
    """Build or refresh raw vector indexes for selected lanes."""
    cfg = load_merged_run_config(repo_root)
    embed_cfg = (cfg.get("retail_raw_rag") or {}).get("embedding") or {}
    lanes_map = load_lanes(repo_root)
    selected = [lanes_map[lid] for lid in lane_ids]

    rid = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = repo_root / "ops" / "runs" / "retail-lane-abcd-raw" / rid
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "index_progress.jsonl"
    log = NeatLoggerFactory.create(
        "OPS",
        "RETAIL_RAW_INDEX",
        log_file_name=f"retail-lane-abcd-raw-index-{rid.replace('/', '_')}.log",
        log_output="both",
    )

    log.step(f"raw index run_id={rid} lanes={lane_ids}")
    meta_by_lane: dict[str, Any] = {}
    for lane in selected:
        if not lane.raw_rag_enabled:
            raise ValueError(f"lane {lane.lane_id} is not raw_rag_enabled")
        write_jsonl_line(
            jsonl_path,
            {"type": "progress", "step": "index_build_start", "lane": lane.lane_id},
        )
        t0 = time.perf_counter()
        with log.heartbeat(f"{lane.lane_id} embed + Lance write"):
            if force_reindex or skip_index_check:
                meta = build_index_for_lane(lane, embed_cfg)
            else:
                meta = ensure_index_fresh(
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
                "step": "index_build_done",
                "lane": lane.lane_id,
                "elapsed_sec": elapsed,
                "chunk_count": meta.get("chunk_count"),
            },
        )
        log.info(f"lane {lane.lane_id} index chunks={meta.get('chunk_count')} sec={elapsed}")

    summary = {
        "run_id": rid,
        "git_head": _git_head(repo_root),
        "lanes": meta_by_lane,
        "embed_model_id": meta_by_lane.get(lane_ids[0], {}).get("embed_model_id") if lane_ids else "",
    }
    (out_dir / "index_summary.json").write_text(
        __import__("json").dumps(summary, indent=2),
        encoding="utf-8",
    )
    return out_dir
