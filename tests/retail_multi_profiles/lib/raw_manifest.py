"""JSON manifest of raw corpus files for index freshness checks."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .lanes import Lane
from .raw_corpus import RawSourceFile, iter_raw_source_files


def build_manifest(lane: Lane) -> dict[str, Any]:
    """Snapshot of all raw source files for one lane project."""
    files = iter_raw_source_files(lane.project_path, lane.raw_glob)
    return {
        "lane_id": lane.lane_id,
        "project_path": str(lane.project_path),
        "raw_glob": lane.raw_glob,
        "files": [
            {
                "source_relpath": f.source_relpath,
                "content_sha256": f.content_sha256,
                "mtime_ns": f.mtime_ns,
                "size_bytes": f.size_bytes,
                "model_id": f.model_id,
            }
            for f in files
        ],
    }


def manifest_fingerprint(manifest: dict[str, Any]) -> str:
    """Stable hash key for whether corpus changed."""
    payload = json.dumps(manifest, sort_keys=True, ensure_ascii=False)
    import hashlib

    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    """Persist manifest next to the vector index."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def read_manifest(path: Path) -> dict[str, Any] | None:
    """Load manifest if present."""
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def source_files_from_manifest(manifest: dict[str, Any], project_path: Path) -> list[RawSourceFile]:
    """Rehydrate RawSourceFile list from a saved manifest."""
    out: list[RawSourceFile] = []
    for row in manifest.get("files") or []:
        rel = str(row["source_relpath"])
        abs_path = (project_path / rel).resolve()
        out.append(
            RawSourceFile(
                source_relpath=rel,
                absolute_path=abs_path,
                model_id=str(row.get("model_id") or ""),
                content_sha256=str(row["content_sha256"]),
                size_bytes=int(row.get("size_bytes") or 0),
                mtime_ns=int(row.get("mtime_ns") or 0),
            )
        )
    return out
