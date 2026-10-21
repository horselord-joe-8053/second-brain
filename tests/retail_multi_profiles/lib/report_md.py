"""Markdown scoreboard from results.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def render_scoreboard_md(results: dict[str, Any]) -> str:
    """Lane × question table for smoke or full runs."""
    lines = [
        f"# Retail lane benchmark — {results.get('run_id', '')}",
        "",
        f"Kind: **{results.get('kind', 'run')}** · Git: `{results.get('git_head', '')}`",
        "",
        "| Lane | Question | Diff | Pass | Top wiki path |",
        "|------|----------|------|------|---------------|",
    ]
    for row in results.get("rows") or []:
        top = (row.get("top_paths") or ["—"])[0]
        mark = "yes" if row.get("pass") else "no"
        lines.append(
            f"| {row.get('lane')} | {row.get('question_id')} | {row.get('difficulty')} | {mark} | `{top}` |"
        )
    lines.extend(["", "## Summary by lane", ""])
    by_lane: dict[str, list[bool]] = {}
    for row in results.get("rows") or []:
        by_lane.setdefault(str(row.get("lane")), []).append(bool(row.get("pass")))
    for lane, passes in sorted(by_lane.items()):
        n = len(passes)
        ok = sum(1 for p in passes if p)
        lines.append(f"- **Lane {lane}:** {ok}/{n} pass")
    return "\n".join(lines) + "\n"


def write_scoreboard_md(results_path: Path) -> Path:
    """Write sibling scoreboard.md."""
    data = json.loads(results_path.read_text(encoding="utf-8"))
    out = results_path.parent / "scoreboard.md"
    out.write_text(render_scoreboard_md(data), encoding="utf-8")
    return out
