"""Join wiki baseline run with raw-RAG run for pass-rate deltas."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def _pass_rates(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Compute pass rate overall and by difficulty per lane."""
    by_lane: dict[str, list[bool]] = defaultdict(list)
    by_lane_diff: dict[tuple[str, str], list[bool]] = defaultdict(list)
    for row in rows:
        lane = str(row.get("lane") or "")
        diff = str(row.get("difficulty") or "")
        passed = bool(row.get("pass"))
        by_lane[lane].append(passed)
        by_lane_diff[(lane, diff)].append(passed)

    def rate(vals: list[bool]) -> float:
        return (sum(1 for v in vals if v) / len(vals)) if vals else 0.0

    out: dict[str, dict[str, float]] = {}
    for lane, vals in by_lane.items():
        out[lane] = {"overall": rate(vals)}
        for diff in ("easy", "hard", "negative"):
            out[lane][diff] = rate(by_lane_diff.get((lane, diff), []))
    return out


def load_results(path: Path) -> dict[str, Any]:
    """Load results.json from an ops run directory."""
    return json.loads(path.read_text(encoding="utf-8"))


def compare_runs(
    wiki_results_path: Path,
    raw_results_path: Path,
) -> dict[str, Any]:
    """Build comparison payload from two canonical results.json files."""
    if not wiki_results_path.is_file():
        raise FileNotFoundError(f"wiki baseline missing: {wiki_results_path}")
    if not raw_results_path.is_file():
        raise FileNotFoundError(f"raw run missing: {raw_results_path}")

    wiki = load_results(wiki_results_path)
    raw = load_results(raw_results_path)
    wiki_rates = _pass_rates(list(wiki.get("rows") or []))
    raw_rates = _pass_rates(list(raw.get("rows") or []))

    lanes = sorted(set(wiki_rates) & set(raw_rates))
    if not lanes:
        lanes = sorted(set(raw_rates) or set(wiki_rates))
    table: list[dict[str, Any]] = []
    for lane in lanes:
        w = wiki_rates.get(lane, {})
        r = raw_rates.get(lane, {})
        table.append(
            {
                "lane": lane,
                "wiki_overall_pct": round(100.0 * w.get("overall", 0.0), 1),
                "raw_overall_pct": round(100.0 * r.get("overall", 0.0), 1),
                "delta_raw_minus_wiki": round(
                    100.0 * (r.get("overall", 0.0) - w.get("overall", 0.0)), 1
                ),
                "wiki_hard_pct": round(100.0 * w.get("hard", 0.0), 1),
                "raw_hard_pct": round(100.0 * r.get("hard", 0.0), 1),
            }
        )

    return {
        "wiki_run_id": wiki.get("run_id"),
        "raw_run_id": raw.get("run_id"),
        "wiki_path": str(wiki_results_path),
        "raw_path": str(raw_results_path),
        "lanes": table,
    }


def write_compare_markdown(payload: dict[str, Any], out_path: Path) -> Path:
    """Write a simple markdown scoreboard for wiki vs raw."""
    lines = [
        "# Wiki vs raw-sources RAG",
        "",
        f"- Wiki run: `{payload.get('wiki_run_id')}`",
        f"- Raw run: `{payload.get('raw_run_id')}`",
        "",
        "| Lane | Wiki % | Raw % | Δ (raw−wiki) | Wiki hard % | Raw hard % |",
        "|------|--------|-------|--------------|-------------|------------|",
    ]
    for row in payload.get("lanes") or []:
        lines.append(
            f"| {row['lane']} | {row['wiki_overall_pct']} | {row['raw_overall_pct']} | "
            f"{row['delta_raw_minus_wiki']} | {row['wiki_hard_pct']} | {row['raw_hard_pct']} |"
        )
    lines.append("")
    lines.append(
        "_Lane D: wiki used full-copy `wiki/sources/`; raw uses split-less files under `raw/sources/`._"
    )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path
