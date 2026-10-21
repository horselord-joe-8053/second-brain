"""Lane registry A–D → absolute LLM Wiki project paths."""

from __future__ import annotations

from dataclasses import dataclass
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
BRAIN_SCRIPTS = REPO / "scripts" / "brain"
if str(BRAIN_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(BRAIN_SCRIPTS))

from brain_stack import _parse_simple_yaml  # noqa: E402


@dataclass(frozen=True)
class Lane:
    """One ingest experiment arm."""

    lane_id: str
    project_path: Path
    ingest_kind: str


def load_lanes(repo_root: Path, config_path: Path | None = None) -> dict[str, Lane]:
    """Load lane map from YAML; resolve paths relative to repo root."""
    cfg_path = config_path or (repo_root / "config" / "retail-ingest-lanes.yaml")
    raw: dict[str, Any] = _parse_simple_yaml(cfg_path.read_text(encoding="utf-8"))
    out: dict[str, Lane] = {}
    for lane_id, entry in (raw.get("lanes") or {}).items():
        rel = str(entry["path"])
        out[str(lane_id)] = Lane(
            lane_id=str(lane_id),
            project_path=(repo_root / rel).resolve(),
            ingest_kind=str(entry.get("ingest_kind") or ""),
        )
    return out
