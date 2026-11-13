"""Render limit-join v2 A1 vs A3 report from suite JSON and results JSONL."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


def _abbrev_words(text: str, max_words: int = 26) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + " ..."


def _has_compiled_news(paths: list[str]) -> bool:
    return any("wiki/sources/" in p and "newsmd" in p for p in paths)


def _has_raw_news(paths: list[str]) -> bool:
    return any("fridge-news_md" in p for p in paths)


def _gap_explain(sa: int, sb: int, w: dict, b: dict) -> str:
    """One-line explanation when scores diverge by at least fifteen points."""
    delta = sa - sb
    if abs(delta) < 15:
        return "—"
    poorer_arm = "A3" if sb < sa else "A1"
    poorer = b if poorer_arm == "A3" else w
    richer = w if poorer_arm == "A3" else b
    parts: list[str] = []

    w_news = _has_compiled_news(list(w.get("top_hit_paths") or []))
    b_news = _has_raw_news(list(b.get("top_hit_paths") or []))
    b_wiki_news = _has_compiled_news(list(b.get("top_hit_paths") or []))

    if poorer_arm == "A3" and w_news and not b_news:
        parts.append("A1 opened compiled news; A3 context lacked matching raw news chunks.")
    elif poorer_arm == "A3" and w_news and b_news and not any(
        "KitchenAid" in p and "news" in p for p in (b.get("top_hit_paths") or [])
    ) and "KitchenAid" in poorer.get("candidate", ""):
        parts.append("A3 pulled manuals or wrong-brand files; KitchenAid news chunk missed the pool.")

    cand = (poorer.get("candidate") or "").lower()
    if "uncertain" in cand or "no mention" in cand or "no explicit" in cand:
        parts.append(f"{poorer_arm} hedged despite partial facts.")

    crit = (poorer.get("criterion_scores") or [{}])[0]
    status = str(crit.get("status") or "")
    if status in ("partly_met", "not_met"):
        reason = str(crit.get("reason") or "")
        if reason:
            parts.append(_abbrev_words(reason, 18))
        elif status == "not_met":
            parts.append("Critical refusal not stated plainly.")

    if not parts:
        rationale = str(poorer.get("judge_rationale") or "")
        parts.append(_abbrev_words(rationale, 22) if rationale else f"{poorer_arm} lower on judge partial credit.")

    return " ".join(parts)


def render(
    repo: Path,
    *,
    suite_path: Path,
    results_path: Path,
    run_id: str,
    out_path: Path,
) -> None:
    """Write HTML-flavored markdown analysis for one completed run."""
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    gold = {q["id"]: q for q in suite["questions"]}
    rows = [
        json.loads(line)
        for line in results_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    by: dict[str, dict[str, dict]] = {}
    for row in rows:
        by.setdefault(row["question_id"], {})[row["arm"]] = row

    missing = [qid for qid in sorted(gold) if set(by.get(qid, {})) != {"wiki", "bundled"}]
    if missing:
        raise SystemExit(f"missing arms for: {missing[:5]}{'...' if len(missing) > 5 else ''}")

    def sc(sa: int, sb: int) -> str:
        if sa > sb:
            return "#e8f5e9"
        if sa < sb:
            return "#ffebee"
        return "#fafafa"

    def score_cell(score: int, other: int, paths: list[str]) -> str:
        bg = sc(score, other) if score != other else sc(score, other)
        items = "".join(
            f'<li><code>{html.escape(p)}</code></li>' for p in paths if p
        ) or '<li><em>(none)</em></li>'
        return (
            f'<td style="background:{bg};vertical-align:top">'
            f"<strong>{score}</strong>"
            f"<br><small>top hits</small>"
            f'<ol style="margin:0.4em 0 0 1.1em;padding:0;font-size:0.88em">{items}</ol>'
            f"</td>"
        )

    def cell_para(text: str) -> str:
        return html.escape(text or "").replace("\n", "<br>")

    a1_scores = [by[i]["wiki"].get("overall_score", 0) for i in sorted(gold)]
    a3_scores = [by[i]["bundled"].get("overall_score", 0) for i in sorted(gold)]
    m1 = sum(a1_scores) / len(a1_scores)
    m3 = sum(a3_scores) / len(a3_scores)
    w1 = sum(1 for x, y in zip(a1_scores, a3_scores) if x > y)

    wiki_news_hits = sum(
        1 for qid in sorted(gold) if _has_compiled_news(list(by[qid]["wiki"].get("top_hit_paths") or []))
    )
    a3_raw_news = sum(
        1 for qid in sorted(gold) if _has_raw_news(list(by[qid]["bundled"].get("top_hit_paths") or []))
    )

    body: list[str] = []
    body.append(
        '<h1 id="lj2-report-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;'
        'border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">A1 vs A3 — limit-join v2</h1>'
    )
    body.append("")
    body.append(
        f"**Run:** `{run_id}` · **Suite:** V01–V{len(gold):02d} · **Gold:** ≤75 words · "
        "**Answers:** ≤150 words · **Judge:** `gemini-4-carbon`"
    )
    body.append("")
    body.append("## Document outline")
    body.append("")
    body.append("1. [Summary metrics](#lj2-report-title) — mean scores and retrieval counts.")
    body.append("2. [Pattern](#lj2-pattern) — where gold lives and why arms diverge.")
    body.append("3. [Results matrix](#lj2-matrix) — full answers, hits, gap notes.")
    body.append("4. [Artifacts](#lj2-notes) — suite and raw run paths.")
    body.append("")
    body.append(
        "<p><strong>Design read (objective):</strong> This construct supports a dual-arm chief-of-staff design "
        "for <em>limit-join</em> staff questions when gold lives in compiled news summaries "
        "(<code>wiki/sources/*news*</code>) that state what must <strong>not</strong> be promised. "
        "It does <strong>not</strong> prove LLM Wiki wins all Type-C questions; W20-style cross-manual "
        "synthesis and thin concept pages remain separate failures.</p>"
    )
    body.append("")
    body.append("<table>")
    body.append(
        '<thead><tr style="background:#1565c0;color:white">'
        "<th>Metric</th><th>A1 wiki</th><th>A3 bundled</th></tr></thead><tbody>"
    )
    body.append(
        f'<tr><td style="background:#e3f2fd">Mean score</td>'
        f'<td style="background:#e8f5e9"><strong>{m1:.1f}</strong></td>'
        f'<td style="background:#ffebee"><strong>{m3:.1f}</strong></td></tr>'
    )
    body.append(
        f'<tr><td style="background:#e3f2fd">Rows ahead</td>'
        f'<td style="background:#e8f5e9"><strong>{w1} / {len(gold)}</strong></td>'
        f'<td style="background:#fff3e0">{len(gold) - w1} / {len(gold)}</td></tr>'
    )
    body.append(
        f'<tr><td style="background:#e3f2fd">Compiled news in A1 top-5</td>'
        f'<td colspan="2">{wiki_news_hits} / {len(gold)} questions</td></tr>'
    )
    body.append(
        f'<tr><td style="background:#e3f2fd">Raw news in A3 top-5</td>'
        f'<td colspan="2">{a3_raw_news} / {len(gold)} questions</td></tr>'
    )
    body.append("</tbody></table>")
    body.append("")
    body.append(
        '<h2 id="lj2-pattern" style="color:#1565c0;font-size:1.22em;font-weight:650;'
        'border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Pattern</h2>'
    )
    body.append("<ul>")
    body.append(
        "<li>Each row joins a still-valid user guide with a 2026 news limit. "
        "Gold is authored from <code>raw/sources/fridge-news_md/*.md</code> and "
        "the matching <code>wiki/sources/*newsmd*</code> compile.</li>"
    )
    body.append(
        "<li>A1 advantage correlates with opening <code>wiki/sources/…news…</code> "
        "where the refusal is already written.</li>"
    )
    body.append(
        "<li>A3 loses when the matching news chunk is outside the 200-chunk pool "
        "or loses RRF to long manual overlap; answers then hedge and miss the critical criterion.</li>"
    )
    body.append(
        "<li>Large score gaps (≥15) usually pair retrieval miss with hedge, not a wrong opening sentence.</li>"
    )
    body.append("</ul>")
    body.append("")
    body.append(
        '<h2 id="lj2-matrix" style="color:#1565c0;font-size:1.22em;font-weight:650;'
        'border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Results matrix (full answers)</h2>'
    )
    body.append("<table>")
    body.append(
        '<thead><tr style="background:#1565c0;color:white">'
        "<th>Id</th><th>Question</th><th>Gold</th>"
        "<th>A1 · hits</th><th>A3 · hits</th>"
        "<th>Gap notes</th><th>A1 answer</th><th>A3 answer</th>"
        "</tr></thead><tbody>"
    )
    for qid in sorted(gold):
        g = gold[qid]
        w, b = by[qid]["wiki"], by[qid]["bundled"]
        sa = int(w.get("overall_score", 0) or 0)
        sb = int(b.get("overall_score", 0) or 0)
        explain = html.escape(_gap_explain(sa, sb, w, b))
        body.append("<tr>")
        body.append(f'<td style="background:#e3f2fd;vertical-align:top"><code>{qid}</code></td>')
        body.append(f'<td style="background:#fafafa;vertical-align:top">{cell_para(g["question"])}</td>')
        body.append(f'<td style="background:#f3e5f5;vertical-align:top">{cell_para(g["answer"])}</td>')
        body.append(score_cell(sa, sb, list(w.get("top_hit_paths") or [])))
        body.append(score_cell(sb, sa, list(b.get("top_hit_paths") or [])))
        body.append(f'<td style="background:#fff8e1;vertical-align:top;font-size:0.92em">{explain}</td>')
        body.append(f'<td style="background:#e3f2fd;vertical-align:top">{cell_para(w.get("candidate", ""))}</td>')
        body.append(f'<td style="background:#ede7f6;vertical-align:top">{cell_para(b.get("candidate", ""))}</td>')
        body.append("</tr>")
    body.append("</tbody></table>")
    body.append("")
    body.append(
        '<h2 id="lj2-notes" style="color:#1565c0;font-size:1.22em;font-weight:650;'
        'border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Artifacts</h2>'
    )
    body.append("<ul>")
    body.append(f"<li>Suite: <code>{suite_path.relative_to(repo)}</code></li>")
    body.append(f"<li>Rows: <code>{results_path.relative_to(repo)}</code></li>")
    body.append("</ul>")

    out_path.write_text("\n".join(body) + "\n", encoding="utf-8")


def main() -> int:
    """CLI for regenerating the v2 analysis artifact after a benchmark run."""
    parser = argparse.ArgumentParser(description="Render limit-join v2 analysis markdown")
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--suite",
        type=Path,
        default=Path("tests/retail_multi_profiles/data/retail-limit-join-v2.json"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs_manual_gen/artifacts/TEST_ANALYSIS_A1_A3_LIMIT_JOINS_V2.md"),
    )
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    results = repo / "ops" / "runs" / "retail-cos-insight" / args.run_id / "results.jsonl"
    render(
        repo,
        suite_path=repo / args.suite,
        results_path=results,
        run_id=args.run_id,
        out_path=repo / args.out,
    )
    print(repo / args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
