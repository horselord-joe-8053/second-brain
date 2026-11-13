"""Roadmap renderer uses last analyze line and marks harness-seeded (fabrication plan phase 6)."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RENDER = REPO / ".cursor" / "skills" / "fabrication" / "assets" / "render-roadmap.sh"


def test_render_roadmap_last_analyze_and_harness_done() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        log = root / "seed_grow" / "progress.jsonl"
        log.parent.mkdir(parents=True)
        lines = [
            {"ts": "2026-01-01T00:00:00Z", "phase": "analyze", "checkpoint": "analyze", "status": "done"},
            {"ts": "2026-01-02T00:00:00Z", "phase": "1", "checkpoint": "harness-seeded", "status": "done"},
            {"ts": "2026-01-03T00:00:00Z", "phase": "analyze", "checkpoint": "analyze", "status": "done"},
        ]
        log.write_text("\n".join(json.dumps(x) for x in lines) + "\n", encoding="utf-8")
        subprocess.run(["bash", str(RENDER), str(root)], check=True, cwd=REPO)
        html = (root / "seed_grow" / "roadmap.html").read_text(encoding="utf-8")
        assert "harness-seeded" in html
        assert 'class="node done current"' in html or 'class="node current"' in html
        assert html.count('class="node done') >= 2
