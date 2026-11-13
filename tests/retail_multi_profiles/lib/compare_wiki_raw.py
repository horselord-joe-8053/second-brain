"""Join wiki baseline run with raw-RAG run for pass-rate deltas."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def _latency_ms(rows: list[dict[str, Any]]) -> dict[str, float]:
    """Mean and p50 latency (ms) for retrieval, answer, judge, and total row time."""
    buckets: dict[str, list[int]] = {
        "retrieval": [],
        "answer": [],
        "judge": [],
        "total": [],
    }
    for row in rows:
        lat = row.get("latency_ms") or {}
        ret = int(lat.get("retrieval") or 0)
        ans = int(lat.get("answer") or 0)
        jud = int(lat.get("judge") or 0)
        buckets["retrieval"].append(ret)
        buckets["answer"].append(ans)
        buckets["judge"].append(jud)
        buckets["total"].append(ret + ans + jud)

    def summarize(vals: list[int]) -> dict[str, float]:
        if not vals:
            return {"mean_ms": 0.0, "p50_ms": 0.0, "p95_ms": 0.0}
        ordered = sorted(vals)
        n = len(ordered)

        def pct(p: float) -> float:
            idx = min(n - 1, int(p * n))
            return float(ordered[idx])

        return {
            "mean_ms": round(sum(vals) / n, 1),
            "p50_ms": pct(0.5),
            "p95_ms": pct(0.95),
        }

    out: dict[str, float] = {}
    for key, vals in buckets.items():
        s = summarize(vals)
        out[f"{key}_mean_ms"] = s["mean_ms"]
        out[f"{key}_p50_ms"] = s["p50_ms"]
        out[f"{key}_p95_ms"] = s["p95_ms"]
    tot_sum = sum(buckets["total"])
    ret_sum = sum(buckets["retrieval"])
    out["retrieval_share_pct"] = round(100.0 * ret_sum / tot_sum, 1) if tot_sum else 0.0
    out["row_count"] = float(len(rows))
    return out


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
    wiki_rows = list(wiki.get("rows") or [])
    raw_rows = list(raw.get("rows") or [])
    wiki_rates = _pass_rates(wiki_rows)
    raw_rates = _pass_rates(raw_rows)

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

    compare_lanes = set(lanes)
    wiki_lat_rows = [r for r in wiki_rows if str(r.get("lane") or "") in compare_lanes]
    raw_lat_rows = [r for r in raw_rows if str(r.get("lane") or "") in compare_lanes]

    return {
        "wiki_run_id": wiki.get("run_id"),
        "raw_run_id": raw.get("run_id"),
        "wiki_path": str(wiki_results_path),
        "raw_path": str(raw_results_path),
        "lanes": table,
        "latency": {
            "wiki": _latency_ms(wiki_lat_rows),
            "raw": _latency_ms(raw_lat_rows),
            "lanes_compared": sorted(compare_lanes),
        },
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
    lat = payload.get("latency") or {}
    w_lat = lat.get("wiki") or {}
    r_lat = lat.get("raw") or {}
    if w_lat.get("row_count") and r_lat.get("row_count"):
        lines.extend(
            [
                "",
                "## Latency (harness `latency_ms`, compared lanes only)",
                "",
                f"_Rows: wiki **{int(w_lat['row_count'])}**, raw **{int(r_lat['row_count'])}** · "
                f"lanes **{', '.join(lat.get('lanes_compared') or [])}**._",
                "",
                "| Stage | Wiki mean | Wiki p50 | Raw mean | Raw p50 | Raw ÷ Wiki (mean) |",
                "|-------|-----------|----------|----------|---------|-------------------|",
            ]
        )
        for stage, label in (
            ("retrieval", "Retrieval"),
            ("answer", "Answer LLM"),
            ("judge", "Judge LLM"),
            ("total", "Row total"),
        ):
            wm = w_lat.get(f"{stage}_mean_ms", 0.0)
            wp = w_lat.get(f"{stage}_p50_ms", 0.0)
            rm = r_lat.get(f"{stage}_mean_ms", 0.0)
            rp = r_lat.get(f"{stage}_p50_ms", 0.0)
            ratio = round(wm / rm, 1) if rm else 0.0
            lines.append(f"| {label} | {wm} ms | {wp} ms | {rm} ms | {rp} ms | {ratio}× |")
        lines.extend(
            [
                "",
                f"- Wiki retrieval share of row time: **{w_lat.get('retrieval_share_pct', 0)}%**",
                f"- Raw retrieval share of row time: **{r_lat.get('retrieval_share_pct', 0)}%**",
                "",
                "_Wall clock is sequential benchmark time (see ops log `elapsed_sec`); "
                "row latencies sum to less than wall when startup/index/overhead apply._",
            ]
        )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path
