#!/usr/bin/env python3
"""Build HTML flip-case tables for PG vs Lance A2 manual RAG analysis (operator re-run)."""

from __future__ import annotations

import html
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNS = REPO / "ops" / "runs" / "retail-lane-abcd-raw"
SUITE = REPO / "tests" / "retail_multi_profiles" / "data" / "retail-manual-qa-test-suite.json"


def _load_gold() -> dict[str, dict[str, str]]:
    raw = json.loads(SUITE.read_text(encoding="utf-8"))
    out: dict[str, dict[str, str]] = {}
    for model in raw.get("models") or []:
        for q in model.get("questions") or []:
            qid = str(q["id"])
            out[qid] = {
                "question": str(q.get("question") or ""),
                "gold": str(q.get("answer") or ""),
                "difficulty": str(q.get("difficulty") or ""),
            }
    return out


def _load_lane_b_answerable(run_id: str) -> dict[str, dict]:
    path = RUNS / run_id / "results.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("rows") or []
    return {
        str(r["question_id"]): r
        for r in rows
        if r.get("lane") == "B" and r.get("difficulty") in ("easy", "hard")
    }


def _rank1(row: dict) -> str:
    hits = row.get("top_hits") or []
    if not hits:
        return ""
    return str(hits[0].get("chunk_id") or "")


def _pref(cid: str) -> str:
    return (cid or "")[:8]


def _top_k_ids(row: dict, k: int = 5) -> list[str]:
    return [str(h.get("chunk_id") or "") for h in (row.get("top_hits") or [])[:k] if h.get("chunk_id")]


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _truncate_words(text: str, max_words: int = 100) -> str:
    words = (text or "").split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "…"


def _cell_text(text: str) -> str:
    """Escape and keep multiline content inside HTML table cells (no raw newlines for MD parsers)."""
    return html.escape(text).replace("\r\n", "\n").replace("\n", "<br>")


def _method_cell(row: dict) -> str:
    ans = _truncate_words(str(row.get("candidate_answer") or ""), 100)
    passed = bool(row.get("pass"))
    rationale = str(row.get("judge_rationale") or "")
    judge_label = "pass" if passed else "fail"
    color = "#2e7d32" if passed else "#c62828"
    return (
        f"<div>{_cell_text(ans)}</div>"
        f'<div style="margin-top:0.45em;padding-top:0.35em;border-top:1px solid #bdbdbd">'
        f'<span style="font-size:0.72em;color:#616161;font-weight:600">Judge ({judge_label})</span><br>'
        f'<span style="color:{color}">{_cell_text(rationale)}</span></div>'
    )


def _rank_cell(left: dict, right: dict) -> str:
    a, b = _pref(_rank1(left)), _pref(_rank1(right))
    if a == b:
        return '<span style="font-size:0.85em"><em>same</em></span>'
    return (
        f'<code style="font-size:0.7em">{html.escape(a)}</code><br>→<br>'
        f'<code style="font-size:0.7em">{html.escape(b)}</code>'
    )


def _why_flip(left: dict, right: dict, *, left_label: str, right_label: str, win: str) -> str:
    """Short retrieval-focused why for a pass flip."""
    same_r1 = _pref(_rank1(left)) == _pref(_rank1(right))
    top5_j = _jaccard(set(_top_k_ids(left)), set(_top_k_ids(right)))
    if win == "right":
        who, loser = right_label, left_label
    else:
        who, loser = left_label, right_label
    parts = [f"{who} pass where {loser} fail."]
    if same_r1:
        parts.append(
            "Same rank‑1 chunk id — flip likely answer/judge variance, not retrieval head swap."
        )
    else:
        parts.append(f"Rank‑1 chunk changed; top‑5 Jaccard {top5_j:.2f}.")
    return " ".join(parts)


def _id_cell(qid: str, gold_meta: dict) -> str:
    short = qid.split("_", 1)[-1] if "_" in qid else qid
    diff = (gold_meta.get("difficulty") or "?")[0]
    return f'<code style="font-size:0.68em">{html.escape(short)}</code><br>{html.escape(diff)}'


def _flip_rows(
    left: dict[str, dict],
    right: dict[str, dict],
    gold: dict[str, dict],
    *,
    left_name: str,
    right_name: str,
    win_tag: str,
    lose_tag: str,
    win_badge: str,
    lose_badge: str,
) -> tuple[list[str], int, int]:
    """Return HTML tr lines, wins, losses (right wins on pass flip)."""
    wins: list[tuple[str, dict, dict]] = []
    losses: list[tuple[str, dict, dict]] = []
    for qid in sorted(left.keys()):
        if qid not in right:
            continue
        lp, rp = bool(left[qid].get("pass")), bool(right[qid].get("pass"))
        if not lp and rp:
            wins.append((qid, left[qid], right[qid]))
        elif lp and not rp:
            losses.append((qid, left[qid], right[qid]))

    trs: list[str] = []
    n = 0
    for qid, lrow, rrow in wins:
        n += 1
        gm = gold.get(qid, {})
        trs.append(_one_tr(n, win_badge, qid, gm, lrow, rrow, left_name, right_name, "right", left_name, right_name))
    for qid, lrow, rrow in losses:
        n += 1
        gm = gold.get(qid, {})
        trs.append(_one_tr(n, lose_badge, qid, gm, lrow, rrow, left_name, right_name, "left", left_name, right_name))
    return trs, len(wins), len(losses)


def _one_tr(
    n: int,
    badge: str,
    qid: str,
    gm: dict,
    lrow: dict,
    rrow: dict,
    left_col: str,
    right_col: str,
    winner: str,
    left_name: str,
    right_name: str,
) -> str:
    bg = "#e8f5e9" if badge.endswith("+") or "PG+" in badge or "R+" in badge or badge.startswith("P") else "#ffebee"
    if "−" in badge or "-" in badge:
        bg = "#ffebee" if "−" in badge else bg
    if "+" in badge:
        bg = "#e8f5e9"
    qtext = _cell_text(gm.get("question") or lrow.get("query") or "")
    gtext = _cell_text(_truncate_words(gm.get("gold") or "", 100))
    why = _cell_text(_why_flip(lrow, rrow, left_label=left_name, right_label=right_name, win=winner))
    return (
        f'<tr style="background:{bg}">'
        f'<td style="font-size:0.78em;vertical-align:top">{n}</td>'
        f'<td style="font-size:0.78em;vertical-align:top">{badge}</td>'
        f'<td style="font-size:0.75em;vertical-align:top;word-break:break-all">{_id_cell(qid, gm)}</td>'
        f'<td style="font-size:0.9em;vertical-align:top">{qtext}</td>'
        f'<td style="font-size:0.9em;vertical-align:top;background:#fffde7">{gtext}</td>'
        f'<td style="font-size:0.72em;vertical-align:top">{_rank_cell(lrow, rrow)}</td>'
        f'<td style="font-size:0.88em;vertical-align:top">{_method_cell(lrow)}</td>'
        f'<td style="font-size:0.88em;vertical-align:top">{_method_cell(rrow)}</td>'
        f'<td style="font-size:0.85em;vertical-align:top">{why}</td>'
        f"</tr>"
    )


def _retrieval_ms(row: dict) -> float:
    """Per-row retrieval wall time from harness results.json."""
    lat = row.get("latency_ms") or {}
    if isinstance(lat, dict) and lat.get("retrieval") is not None:
        return float(lat["retrieval"])
    return 0.0


def _percentile(sorted_vals: list[float], p: float) -> float:
    """Simple percentile on pre-sorted values (p in 0..100)."""
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def _overlap_stats(run_a: str, run_b: str) -> dict[str, float]:
    a = _load_lane_b_answerable(run_a)
    b = _load_lane_b_answerable(run_b)
    jaccards: list[float] = []
    same_r1 = 0
    for qid in a:
        if qid not in b:
            continue
        ja = _jaccard(set(_top_k_ids(a[qid])), set(_top_k_ids(b[qid])))
        jaccards.append(ja)
        if _pref(_rank1(a[qid])) == _pref(_rank1(b[qid])):
            same_r1 += 1
    n = len(jaccards) or 1
    return {
        "mean_jaccard_top5": sum(jaccards) / n,
        "min_jaccard_top5": min(jaccards) if jaccards else 0.0,
        "pct_jaccard_ge_080": 100.0 * sum(1 for x in jaccards if x >= 0.80) / n,
        "count_jaccard_lt_1": float(sum(1 for x in jaccards if x < 1.0)),
        "same_rank1_pct": 100.0 * same_r1 / n,
        "n": float(n),
    }


def _perf_compare(lance_run: str, pg_run: str) -> dict[str, float | int]:
    """Aggregate retrieval latency + overlap for Lance vs PG on paired rows."""
    lc = _load_lane_b_answerable(lance_run)
    pg = _load_lane_b_answerable(pg_run)
    lance_ms: list[float] = []
    pg_ms: list[float] = []
    ratios: list[float] = []
    jaccards: list[float] = []
    for qid in sorted(lc.keys()):
        if qid not in pg:
            continue
        lm = _retrieval_ms(lc[qid])
        pm = _retrieval_ms(pg[qid])
        lance_ms.append(lm)
        pg_ms.append(pm)
        if lm > 0:
            ratios.append(pm / lm)
        jaccards.append(_jaccard(set(_top_k_ids(lc[qid])), set(_top_k_ids(pg[qid]))))
    n = len(lance_ms) or 1
    lance_ms.sort()
    pg_ms.sort()
    ratios.sort()
    return {
        "n": len(lance_ms),
        "mean_jaccard": sum(jaccards) / n,
        "min_jaccard": min(jaccards) if jaccards else 0.0,
        "lance_mean_ms": sum(lance_ms) / n,
        "pg_mean_ms": sum(pg_ms) / n,
        "mean_ratio_pg_over_lance": sum(ratios) / len(ratios) if ratios else 0.0,
        "lance_p50": _percentile(lance_ms, 50),
        "lance_p95": _percentile(lance_ms, 95),
        "pg_p50": _percentile(pg_ms, 50),
        "pg_p95": _percentile(pg_ms, 95),
        "ratio_p50": _percentile(ratios, 50) if ratios else 0.0,
        "ratio_p95": _percentile(ratios, 95) if ratios else 0.0,
        "ratio_max": max(ratios) if ratios else 0.0,
        "count_ratio_gt_125": sum(1 for r in ratios if r > 1.25),
        "count_jaccard_lt_1": sum(1 for j in jaccards if j < 1.0),
    }


def _short_qid(qid: str) -> str:
    return qid.split("_", 1)[-1] if "_" in qid else qid


def _perf_ticket_rows(lance_run: str, pg_run: str, gold: dict[str, dict[str, str]]) -> list[str]:
    """HTML table rows: per-question retrieval wall time Lance vs PG."""
    lc = _load_lane_b_answerable(lance_run)
    pg = _load_lane_b_answerable(pg_run)
    trs: list[str] = []
    for i, qid in enumerate(sorted(lc.keys()), start=1):
        if qid not in pg:
            continue
        lm = _retrieval_ms(lc[qid])
        pm = _retrieval_ms(pg[qid])
        ratio = (pm / lm) if lm > 0 else 0.0
        jac = _jaccard(set(_top_k_ids(lc[qid])), set(_top_k_ids(pg[qid])))
        r1 = "Y" if _pref(_rank1(lc[qid])) == _pref(_rank1(pg[qid])) else "N"
        diff = (gold.get(qid) or {}).get("difficulty") or "?"
        bg = "#ffffff"
        if jac < 1.0:
            bg = "#ffebee"
        elif ratio > 1.25:
            bg = "#fff3e0"
        elif ratio <= 1.0:
            bg = "#e8f5e9"
        trs.append(
            f'<tr style="background:{bg}">'
            f'<td style="font-size:0.78em">{i}</td>'
            f'<td style="font-size:0.72em"><code>{html.escape(_short_qid(qid))}</code></td>'
            f'<td style="font-size:0.78em;text-align:center">{html.escape(diff[0])}</td>'
            f'<td style="font-size:0.82em;text-align:right">{jac:.2f}</td>'
            f'<td style="font-size:0.82em;text-align:right">{lm:.0f}</td>'
            f'<td style="font-size:0.82em;text-align:right">{pm:.0f}</td>'
            f'<td style="font-size:0.82em;text-align:right">{pm - lm:+.0f}</td>'
            f'<td style="font-size:0.82em;text-align:right">{ratio:.2f}×</td>'
            f'<td style="font-size:0.78em;text-align:center">{r1}</td>'
            f"</tr>"
        )
    return trs


def _latency_stats(run_id: str) -> tuple[float, float]:
    rows = _load_lane_b_answerable(run_id).values()
    rets = []
    rows_total = []
    for r in rows:
        lat = r.get("latency_ms") or {}
        if isinstance(lat, dict):
            if lat.get("retrieval") is not None:
                rets.append(float(lat["retrieval"]))
            if lat.get("retrieval") is not None and lat.get("answer") is not None:
                rows_total.append(float(lat["retrieval"]) + float(lat.get("answer", 0)) + float(lat.get("judge", 0)))
    mean_ret = sum(rets) / len(rets) if rets else 0.0
    mean_row = sum(rows_total) / len(rows_total) if rows_total else 0.0
    return mean_ret, mean_row


def _table_header(left_hdr: str, right_hdr: str) -> str:
    return f"""<table style="table-layout:fixed;width:100%;border-collapse:collapse"><col style="width:2%"/><col style="width:4%"/><col style="width:7%"/><col style="width:14%"/><col style="width:12%"/><col style="width:6%"/><col style="width:14%"/><col style="width:14%"/><col style="width:11%"/>
<thead>
<tr style="background:#1565c0;color:white;font-size:0.82em"><th>#</th><th>Δ</th><th>Id</th><th>Question</th><th>Gold</th><th>Rank‑1</th><th>{html.escape(left_hdr)}</th><th>{html.escape(right_hdr)}</th><th>Why</th></tr></thead><tbody>
"""


def main() -> None:
    gold = _load_gold()
    # Comparison 1: PG hybrid vs Lance hybrid (fair D3 store swap)
    pg_h = _load_lane_b_answerable("a2-pg-hybrid-b-v1")
    lc_h = _load_lane_b_answerable("a2-hybrid-rrf-b-v2")
    trs_h, w_h, l_h = _flip_rows(
        lc_h,
        pg_h,
        gold,
        left_name="Lance",
        right_name="PG",
        win_tag="PG+",
        lose_tag="PG−",
        win_badge='<span style="background:#c8e6c9;color:#1b5e20;padding:1px 3px;font-size:0.72em">PG+</span>',
        lose_badge='<span style="background:#ffcdd2;color:#b71c1c;padding:1px 3px;font-size:0.72em">PG−</span>',
    )

    pg_r = _load_lane_b_answerable("a2-pg-hybrid-rerank-b-v1")
    lc_r = _load_lane_b_answerable("a2-hybrid-rerank-b-v2")
    trs_r, w_r, l_r = _flip_rows(
        lc_r,
        pg_r,
        gold,
        left_name="Lance",
        right_name="PG",
        win_tag="PG+",
        lose_tag="PG−",
        win_badge='<span style="background:#c8e6c9;color:#1b5e20;padding:1px 3px;font-size:0.72em">PG+</span>',
        lose_badge='<span style="background:#ffcdd2;color:#b71c1c;padding:1px 3px;font-size:0.72em">PG−</span>',
    )

    ov_h = _overlap_stats("a2-hybrid-rrf-b-v2", "a2-pg-hybrid-b-v1")
    ov_r = _overlap_stats("a2-hybrid-rerank-b-v2", "a2-pg-hybrid-rerank-b-v1")
    lat_lc_h, row_lc_h = _latency_stats("a2-hybrid-rrf-b-v2")
    lat_pg_h, row_pg_h = _latency_stats("a2-pg-hybrid-b-v1")
    lat_lc_r, row_lc_r = _latency_stats("a2-hybrid-rerank-b-v2")
    lat_pg_r, row_pg_r = _latency_stats("a2-pg-hybrid-rerank-b-v1")
    perf_h = _perf_compare("a2-hybrid-rrf-b-v2", "a2-pg-hybrid-b-v1")
    perf_r = _perf_compare("a2-hybrid-rerank-b-v2", "a2-pg-hybrid-rerank-b-v1")
    ticket_h = _perf_ticket_rows("a2-hybrid-rrf-b-v2", "a2-pg-hybrid-b-v1", gold)
    ticket_r = _perf_ticket_rows("a2-hybrid-rerank-b-v2", "a2-pg-hybrid-rerank-b-v1", gold)

    out_path = Path(__file__).with_name("_pg_vs_lance_generated.htmlfrag")
    fragments = {
        "overlap_hybrid": ov_h,
        "overlap_rerank": ov_r,
        "latency_hybrid": (lat_lc_h, lat_pg_h, row_lc_h, row_pg_h),
        "latency_rerank": (lat_lc_r, lat_pg_r, row_lc_r, row_pg_r),
        "hybrid_trs": trs_h,
        "hybrid_net": (w_h, l_h),
        "rerank_trs": trs_r,
        "rerank_net": (w_r, l_r),
    }
    out_path.write_text(json.dumps(fragments, indent=0), encoding="utf-8")
    md_path = Path(__file__).with_name("TEST_ANALYSIS_A2_MANUAL_RAG_PG.md")
    md_path.write_text(
        _render_markdown(
            trs_h=trs_h,
            trs_r=trs_r,
            w_h=w_h,
            l_h=l_h,
            w_r=w_r,
            l_r=l_r,
            ov_h=ov_h,
            ov_r=ov_r,
            lat_h=(lat_lc_h, lat_pg_h, row_lc_h, row_pg_h),
            lat_r=(lat_lc_r, lat_pg_r, row_lc_r, row_pg_r),
            perf_h=perf_h,
            perf_r=perf_r,
            ticket_h=ticket_h,
            ticket_r=ticket_r,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {out_path}")
    print(f"Wrote {md_path}")
    print(f"Hybrid flips PG+={w_h} PG-={l_h}")
    print(f"Rerank flips PG+={w_r} PG-={l_r}")
    print(f"Overlap hybrid mean Jaccard={ov_h['mean_jaccard_top5']:.3f}")


def _ms(x: float) -> str:
    return f"~{x:.0f} ms"


def _perf_summary_table(perf_h: dict, perf_r: dict) -> str:
    """Aggregate performance comparison (overlap + retrieval ms)."""
    rh = perf_h["mean_ratio_pg_over_lance"]
    rr = perf_r["mean_ratio_pg_over_lance"]
    return f"""<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Metric</th><th>Hybrid (D5.0)</th><th>Rerank (R+V+A)</th><th>Notes</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>Top‑5 Jaccard</strong><br><small>|A∩B| ÷ |A∪B| on chunk_id</small></td><td style="background:#e8f5e9">mean <strong>{perf_h['mean_jaccard']:.2f}</strong> · min {perf_h['min_jaccard']:.2f} · {int(perf_h['count_jaccard_lt_1'])} row(s) &lt; 1.0</td><td style="background:#e8f5e9">mean <strong>{perf_r['mean_jaccard']:.2f}</strong> · min {perf_r['min_jaccard']:.2f} · {int(perf_r['count_jaccard_lt_1'])} row(s) &lt; 1.0</td><td>60 answerable Lane B rows per arm</td></tr>
<tr><td style="background:#e3f2fd"><strong>Mean retrieval wall</strong><br><small><code>latency_ms.retrieval</code></small></td><td>Lance {perf_h['lance_mean_ms']:.0f} ms · PG {perf_h['pg_mean_ms']:.0f} ms · ratio <strong>{rh:.2f}×</strong></td><td>Lance {perf_r['lance_mean_ms']:.0f} ms · PG {perf_r['pg_mean_ms']:.0f} ms · ratio <strong>{rr:.2f}×</strong></td><td>U8 informal pass if mean ≤ <strong>1.25×</strong></td></tr>
<tr><td style="background:#e3f2fd"><strong>p50 / p95 retrieval</strong></td><td>Lance {perf_h['lance_p50']:.0f} / {perf_h['lance_p95']:.0f} ms<br>PG {perf_h['pg_p50']:.0f} / {perf_h['pg_p95']:.0f} ms</td><td>Lance {perf_r['lance_p50']:.0f} / {perf_r['lance_p95']:.0f} ms<br>PG {perf_r['pg_p50']:.0f} / {perf_r['pg_p95']:.0f} ms</td><td>Per-question distribution</td></tr>
<tr><td style="background:#e3f2fd"><strong>PG ÷ Lance ratio</strong></td><td>p50 {perf_h['ratio_p50']:.2f}× · p95 {perf_h['ratio_p95']:.2f}× · max {perf_h['ratio_max']:.2f}×</td><td>p50 {perf_r['ratio_p50']:.2f}× · p95 {perf_r['ratio_p95']:.2f}× · max {perf_r['ratio_max']:.2f}×</td><td><span style="background:#ffcdd2;padding:1px 3px">{int(perf_h['count_ratio_gt_125'])}</span> hybrid · <span style="background:#ffcdd2;padding:1px 3px">{int(perf_r['count_ratio_gt_125'])}</span> rerank rows &gt; 1.25×</td></tr>
</tbody>
</table>"""


def _perf_ticket_table_header() -> str:
    return """<table style="width:100%;border-collapse:collapse;font-size:0.85em">
<thead>
<tr style="background:#1565c0;color:white"><th>#</th><th>Question id</th><th>D</th><th>Jaccard<br><small>top‑5</small></th><th>Lance<br>ret ms</th><th>PG<br>ret ms</th><th>Δ ms</th><th>PG/Lance</th><th>R1<br>same</th></tr>
</thead><tbody>
"""


def _render_markdown(
    *,
    trs_h: list[str],
    trs_r: list[str],
    w_h: int,
    l_h: int,
    w_r: int,
    l_r: int,
    ov_h: dict,
    ov_r: dict,
    lat_h: tuple[float, float, float, float],
    lat_r: tuple[float, float, float, float],
    perf_h: dict,
    perf_r: dict,
    ticket_h: list[str],
    ticket_r: list[str],
) -> str:
    """Emit full mrkd-shaped analysis doc with embedded HTML flip tables."""
    lat_lc_h, lat_pg_h, row_lc_h, row_pg_h = lat_h
    lat_lc_r, lat_pg_r, row_lc_r, row_pg_r = lat_r
    hy_head = _table_header("Lance hybrid", "PG hybrid")
    rr_head = _table_header("Lance rerank", "PG rerank")
    perf_summary = _perf_summary_table(perf_h, perf_r)
    ticket_h_block = _perf_ticket_table_header() + "".join(ticket_h) + "</tbody></table>"
    ticket_r_block = _perf_ticket_table_header() + "".join(ticket_r) + "</tbody></table>"
    ratio_h_mean = perf_h["pg_mean_ms"] / perf_h["lance_mean_ms"] if perf_h["lance_mean_ms"] else 0
    ratio_r_mean = perf_r["pg_mean_ms"] / perf_r["lance_mean_ms"] if perf_r["lance_mean_ms"] else 0
    return f"""<h1 id="a2-pg-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">TEST_ANALYSIS — A2 manual RAG Postgres vs Lance (Lane B)</h1>

**Status:** Operator **P4.1** complete (2026-10-25). **HG-PG-AB:** pending sign-off (**U8**).

**Ingest:** 208 rows in `manual_chunks` (Lane **B**).

<h2 id="a2-pg-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Retrieval overlap and latency pass](#a2-pg-overlap) — definitions + aggregate figures.
 1.1 [Performance summary](#a2-pg-perf-summary) — mean / p50 / p95 retrieval.
 1.2 [Per-question retrieval (hybrid)](#a2-pg-perf-ticket-hybrid) — 60-row wall-time table.
 1.3 [Per-question retrieval (rerank)](#a2-pg-perf-ticket-rerank) — 60-row wall-time table.
2. [Fair v1 runs](#a2-pg-runs) — run ids and headline passes.
 2.1 [Answer context pipeline](#a2-pg-answer-pipeline) — top‑5 excerpts, not rank‑1 only.
 2.2 [Interpreting pass flips (U8)](#a2-pg-flip-read) — PG+ / PG− vs Jaccard 1.00.
3. [Comparison 1 — PG hybrid vs Lance hybrid](#a2-pg-cmp-hybrid) — summary + [win/lose cases](#a2-pg-cmp-hybrid-cases).
4. [Comparison 2 — PG rerank vs Lance rerank](#a2-pg-cmp-rerank) — summary + [win/lose cases](#a2-pg-cmp-rerank-cases).
5. [Commands and regen](#a2-pg-commands).

---

<h2 id="a2-pg-overlap" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Retrieval overlap and latency pass</h2>

Gate **before** trusting judge pass deltas (plan Phase 4 reference targets; **U8** operator sign-off):

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Check</th><th>Definition</th><th>Hybrid (D5.0)</th><th>Rerank (R+V+A)</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>Retrieval overlap</strong></td><td>For each of <strong>60</strong> answerable Lane B rows: Jaccard on top‑5 <code>chunk_id</code> in <code>top_hits</code> (PG vs Lance). <strong>1.00</strong> = same five ids.</td><td style="background:#e8f5e9">mean <strong>{ov_h['mean_jaccard_top5']:.2f}</strong> · min {ov_h['min_jaccard_top5']:.2f} · {int(ov_h['count_jaccard_lt_1'])} &lt; 1.0 · {ov_h['pct_jaccard_ge_080']:.0f}% ≥ 0.80</td><td style="background:#e8f5e9">mean <strong>{ov_r['mean_jaccard_top5']:.2f}</strong> · rank‑1 same <strong>{ov_r['same_rank1_pct']:.0f}%</strong> · {int(ov_r['count_jaccard_lt_1'])} &lt; 1.0</td></tr>
<tr><td style="background:#e3f2fd"><strong>Latency pass</strong></td><td>Mean <code>latency_ms.retrieval</code>: <strong>ratio of means</strong> (PG mean ÷ Lance mean) and <strong>mean of per-row</strong> PG/Lance ratios. Informal guide ≤ <strong>1.25×</strong>.</td><td style="background:#e8f5e9">means <strong>{ratio_h_mean:.2f}×</strong> ({perf_h['pg_mean_ms']:.0f}/{perf_h['lance_mean_ms']:.0f} ms) · rows avg <strong>{perf_h['mean_ratio_pg_over_lance']:.2f}×</strong></td><td style="background:#e8f5e9">means <strong>{ratio_r_mean:.2f}×</strong> ({perf_r['pg_mean_ms']:.0f}/{perf_r['lance_mean_ms']:.0f} ms) · rows avg <strong>{perf_r['mean_ratio_pg_over_lance']:.2f}×</strong></td></tr>
</tbody>
</table>

Hybrid overlap **1.00** everywhere → **+1** judge pass is not retrieval drift (§3.1). Rerank: top‑5 <strong>sets</strong> still Jaccard 1.00; listwise changes rank‑1 on ~{100 - ov_r['same_rank1_pct']:.0f}% of rows.

<h3 id="a2-pg-perf-summary" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">1.1 Performance summary (retrieval wall time)</h3>

{perf_summary}

<h3 id="a2-pg-perf-ticket-hybrid" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">1.2 Per-question retrieval wall time — hybrid (`a2-hybrid-rrf-b-v2` vs `a2-pg-hybrid-b-v1`)</h3>

**Legend:** <span style="background:#e8f5e9;padding:1px 4px">green</span> PG/Lance ≤ 1.0× · <span style="background:#fff3e0;padding:1px 4px">amber</span> ratio &gt; 1.25× · <span style="background:#ffebee;padding:1px 4px">red</span> Jaccard &lt; 1.0 · **R1 same** = rank‑1 chunk prefix match.

{ticket_h_block}

<h3 id="a2-pg-perf-ticket-rerank" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">1.3 Per-question retrieval wall time — rerank (`a2-hybrid-rerank-b-v2` vs `a2-pg-hybrid-rerank-b-v1`)</h3>

Includes listwise rerank + optional agentic retrieve in the retrieval leg (same field as Lance rerank v2).

{ticket_r_block}

---

<h2 id="a2-pg-runs" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Fair v1 runs</h2>

| Profile | D3 store | run_id | Answerable pass |
|---------|----------|--------|-----------------|
| `MANUAL_B_RAW_PG_HYBRID` | PG | `a2-pg-hybrid-b-v1` | **35/60** |
| `MANUAL_B_RAW_HYBRID` | Lance | `a2-hybrid-rrf-b-v2` | **34/60** |
| `MANUAL_B_RAW_PG_HYBRID_RERANK` | PG | `a2-pg-hybrid-rerank-b-v1` | **36/60** |
| `MANUAL_B_RAW_HYBRID_RERANK` | Lance | `a2-hybrid-rerank-b-v2` | **37/60** |

Paths: `ops/runs/retail-lane-abcd-raw/<run_id>/`.

<h3 id="a2-pg-answer-pipeline" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.1 Answer context pipeline (both Lance and PG)</h3>

Harness **raw_rag** does **not** answer from rank‑1 alone. Each row:

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Step</th><th>Behavior</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>Retrieve</strong></td><td><code>search_top_k = 5</code> → five <code>top_hits</code> (hybrid RRF; rerank profiles add listwise rerank + verifier + agentic on the same five).</td></tr>
<tr><td style="background:#e3f2fd"><strong>Context</strong></td><td><code>concat_top_k_raw_chunks</code> joins chunk text <strong>in rank order</strong> (default ≤2000 chars/chunk, ≤8000 chars total in run-config).</td></tr>
<tr><td style="background:#e3f2fd"><strong>Answer</strong></td><td>One <code>answer_from_context</code> LLM call: “Answer using ONLY the manual excerpts below…”</td></tr>
<tr><td style="background:#e3f2fd"><strong>Flip tables “Rank‑1”</strong></td><td>Diagnostic only — whether the <strong>first</strong> <code>chunk_id</code> matches. All five excerpts still feed the answer step unless the char budget truncates the tail.</td></tr>
</tbody>
</table>

<h3 id="a2-pg-flip-read" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.2 Interpreting pass flips (U8 sign-off)</h3>

**Jaccard 1.00** on a row = PG and Lance logged the **same set** of five <code>chunk_id</code>s in <code>top_hits</code> (order may differ). **§3.1 / §4.1** list only rows where the **judge pass flipped** (Lance pass ↔ PG pass), not every row with different wording.

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Pattern</th><th>Retrieval</th><th>Likely cause of flip</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>PG+</strong> (e.g. rerank E07, H07)<br><small>rank‑1 <em>same</em></small></td><td style="background:#e8f5e9">Same top‑5 set and order → same excerpt block (separate runs may still differ slightly).</td><td style="background:#fff3e0">Answer + judge variance — <strong>not</strong> PG vs Lance chunk drift.</td></tr>
<tr><td style="background:#e3f2fd"><strong>PG−</strong> (rerank H06, H10, E02)<br><small>rank‑1 swapped, Jaccard 1.00</small></td><td style="background:#e8f5e9">Same five chunks; <strong>list order</strong> in the prompt changes (lead chunk + possible tail truncation at 8000 chars).</td><td style="background:#fff3e0">Downstream: rerank ordering → one-shot answer LLM → judge — <strong>not</strong> “PG retrieved worse chunks.”</td></tr>
<tr><td style="background:#e3f2fd"><strong>Hybrid +1</strong> (§3.1 H01)<br><small>rank‑1 same, Jaccard 1.00 all 60</small></td><td style="background:#e8f5e9">Cleanest “identical retrieval context, different pass” case.</td><td style="background:#fff3e0">Answer/judge only.</td></tr>
</tbody>
</table>

**Operator read for HG-PG-AB:** PG manual store **matches Lance on top‑5 sets** (hybrid and rerank). Rerank **−1** ({w_r} PG wins − {l_r} PG losses = **{w_r - l_r:+d}**) is **not** missing-chunk drift at top‑5 — it is **ordering / generation / judging** on shared evidence, plus **{w_r}** PG wins from the same bucket.

---

<h2 id="a2-pg-cmp-hybrid" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Comparison 1 — PG hybrid vs Lance hybrid (D5.0)</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Aspect</th><th>Lance</th><th>PG</th><th>Δ (PG − Lance)</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>Answerable pass</strong></td><td>34/60</td><td style="background:#e8f5e9"><strong>35/60</strong></td><td style="background:#e8f5e9"><strong>+1</strong></td></tr>
<tr><td style="background:#e3f2fd"><strong>Top‑5 chunk ids</strong></td><td colspan="2" style="background:#e8f5e9;text-align:center">Identical all 60 rows</td><td>0 drift</td></tr>
<tr><td style="background:#e3f2fd"><strong>Mean retrieval latency</strong></td><td>{_ms(lat_lc_h)}</td><td style="background:#fff3e0">{_ms(lat_pg_h)}</td><td>+{lat_pg_h - lat_lc_h:.0f} ms</td></tr>
<tr><td style="background:#e3f2fd"><strong>Mean row latency</strong></td><td>{_ms(row_lc_h)}</td><td>{_ms(row_pg_h)}</td><td>+{row_pg_h - row_lc_h:.0f} ms</td></tr>
</tbody>
</table>

<h3 id="a2-pg-cmp-hybrid-cases" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">3.1 Win / lose cases (PG hybrid vs Lance hybrid)</h3>

**Pass flip rule:** **PG+** = Lance fail → PG pass; **PG−** = Lance pass → PG fail. **Net:** **+{w_h - l_h}** = **{w_h}** − **{l_h}**. **Rank‑1:** Lance → PG (8-char prefix). **Δ:** <span style="background:#c8e6c9;padding:1px 3px;font-size:0.85em">PG+</span> · <span style="background:#ffcdd2;padding:1px 3px;font-size:0.85em">PG−</span>.

<div markdown="0">

{hy_head}{"".join(trs_h)}</tbody></table>

</div>

---

<h2 id="a2-pg-cmp-rerank" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Comparison 2 — PG rerank vs Lance rerank (R+V+A)</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Aspect</th><th>Lance</th><th>PG</th><th>Δ</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>Answerable pass</strong></td><td>37/60</td><td>36/60</td><td style="background:#fff3e0"><strong>−1</strong></td></tr>
<tr><td style="background:#e3f2fd"><strong>Mean retrieval latency</strong></td><td>{_ms(lat_lc_r)}</td><td>{_ms(lat_pg_r)}</td><td>+{lat_pg_r - lat_lc_r:.0f} ms</td></tr>
<tr><td style="background:#e3f2fd"><strong>Mean row latency</strong></td><td>{_ms(row_lc_r)}</td><td>{_ms(row_pg_r)}</td><td>+{row_pg_r - row_lc_r:.0f} ms</td></tr>
</tbody>
</table>

<h3 id="a2-pg-cmp-rerank-cases" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.1 Win / lose cases (PG rerank vs Lance rerank)</h3>

**Net:** **{w_r - l_r:+d}** = **{w_r}** wins − **{l_r}** losses.

<div markdown="0">

{rr_head}{"".join(trs_r)}</tbody></table>

</div>

---

<h2 id="a2-pg-commands" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Commands and regen</h2>

```bash
bash scripts/retail/ops/pg_up_and_load.sh
python -m tests.retail_multi_profiles --ingest-manual-pg --lanes B
python -m tests.retail_multi_profiles --full --profile MANUAL_B_RAW_PG_HYBRID --run-id a2-pg-hybrid-b-v1 --retrieval-mode raw_rag
python -m tests.retail_multi_profiles --full --profile MANUAL_B_RAW_PG_HYBRID_RERANK --run-id a2-pg-hybrid-rerank-b-v1 --retrieval-mode raw_rag
./scripts/py docs_manual_gen/artifacts/_build_pg_vs_lance_flip_tables.py
```

**Related:** [`TEST_ANALYSIS_A2_MANUAL_RAG.md`](./TEST_ANALYSIS_A2_MANUAL_RAG.md) · [`REFACTOR_UNIFIED_PG_MANUAL_EMBEDDINGS.md`](../ref_plan/completed/REFACTOR_UNIFIED_PG_MANUAL_EMBEDDINGS.md).
"""


if __name__ == "__main__":
    main()
