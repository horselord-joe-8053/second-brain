"""Render wiki compilation join (multi-layer) A1 vs A3 report."""

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


def _wiki_layers(paths: list[str]) -> set[str]:
    """Classify top-hit paths into compilation layers (exclude news compiles)."""
    layers: set[str] = set()
    for p in paths:
        if "newsmd" in p or "fridge-news" in p:
            continue
        if "/wiki/entities/" in p or p.startswith("wiki/entities/"):
            layers.add("entity")
        elif "/wiki/concepts/" in p or p.startswith("wiki/concepts/"):
            layers.add("concept")
        elif "/wiki/sources/" in p and "docsmd" in p:
            layers.add("source_doc")
    return layers


def _gap_explain(sa: int, sb: int, w: dict, b: dict) -> str:
    """One-line explanation when scores diverge by at least fifteen points."""
    delta = sa - sb
    if abs(delta) < 15:
        return "—"
    poorer_arm = "A3" if sb < sa else "A1"
    poorer = b if poorer_arm == "A3" else w
    wl, bl = _wiki_layers(list(w.get("top_hit_paths") or [])), _wiki_layers(
        list(b.get("top_hit_paths") or [])
    )
    parts: list[str] = []
    if poorer_arm == "A3" and len(wl) >= 2 and len(bl) < 2:
        parts.append("A1 hit multiple wiki layers; A3 leaned on raw user-guide chunks.")
    elif poorer_arm == "A1" and len(bl) >= len(wl):
        parts.append("A3 matched guide depth; A1 compiled pages thin or off-topic in context.")

    cand = (poorer.get("candidate") or "").lower()
    if "uncertain" in cand or "no mention" in cand or "not provided" in cand:
        parts.append(f"{poorer_arm} hedged.")

    crit = (poorer.get("criterion_scores") or [{}])[0]
    reason = str(crit.get("reason") or "")
    if reason:
        parts.append(_abbrev_words(reason, 18))

    if not parts:
        parts.append(_abbrev_words(str(poorer.get("judge_rationale") or ""), 20) or f"{poorer_arm} lower.")

    return " ".join(parts)


def render(
    repo: Path,
    *,
    suite_path: Path,
    results_path: Path,
    run_id: str,
    out_path: Path,
) -> None:
    """Write analysis markdown for wiki_compile_join benchmark."""
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
        bg = sc(score, other)
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

    a1_multi = sum(
        1
        for qid in sorted(gold)
        if len(_wiki_layers(list(by[qid]["wiki"].get("top_hit_paths") or []))) >= 2
    )
    a3_multi = sum(
        1
        for qid in sorted(gold)
        if len(_wiki_layers(list(by[qid]["bundled"].get("top_hit_paths") or []))) >= 2
    )

    body: list[str] = []
    body.append(
        '<h1 id="wcj-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;'
        'border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">'
        "A1 vs A3 — wiki compilation join (n=10)</h1>"
    )
    body.append("")
    body.append(
        f"**Run:** `{run_id}` · **Suite:** M01–M10 · **Construct:** multi-layer "
        "`wiki/entities` + `wiki/concepts` (+ doc `wiki/sources`) · **Gold:** ≤75 words · "
        "**Answers:** ≤150 words · **Judge:** `gemini-4-carbon`"
    )
    body.append("")
    body.append("## Document outline")
    body.append("")
    body.append("1. [Hypothesis & metrics](#wcj-title) — does multi-layer wiki gold favor A1?")
    body.append("2. [Pattern](#wcj-pattern) — retrieval layers vs manuals.")
    body.append("3. [Matrix](#wcj-matrix) — scores, provenance, gap notes.")
    body.append("4. [Artifacts](#wcj-notes) — suite and run paths.")
    body.append("")
    body.append(
        "<p><strong>Hypothesis:</strong> When gold joins several <code>wiki/**</code> compilation "
        "files (not news-only), A1 should outperform A3 because entity and concept pages surface "
        "pre-joined facts. <strong>Falsifier:</strong> A3 wins when user-guide chunks already "
        "contain the same procedure text and wiki pages rank poorly.</p>"
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
        f'<tr><td style="background:#e3f2fd">≥2 wiki layers in top-5 (no news)</td>'
        f'<td style="background:#e8f5e9">{a1_multi} / {len(gold)}</td>'
        f'<td style="background:#fff3e0">{a3_multi} / {len(gold)}</td></tr>'
    )
    body.append("</tbody></table>")
    body.append("")
    body.append(
        f'<h2 id="wcj-pattern" style="color:#1565c0;font-size:1.22em;font-weight:650;'
        f'border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Pattern</h2>'
    )
    body.append("<ul>")
    body.append(
        "<li>Suite gold cites <code>gold_wiki_layers</code> in JSON — entity + concept (+ filter entity), "
        "explicitly excluding news compile paths.</li>"
    )
    body.append(
        "<li>When A1’s top-5 spans ≥2 layers, answers often quote the compiled feature paragraph.</li>"
    )
    body.append(
        "<li>A3 can still win on procedural rows when the user guide chunk is long and wiki concepts rank low.</li>"
    )
    body.append("</ul>")
    body.append("")
    body.append(
        f'<h2 id="wcj-matrix" style="color:#1565c0;font-size:1.22em;font-weight:650;'
        f'border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Results matrix</h2>'
    )
    body.append("<table>")
    body.append(
        '<thead><tr style="background:#1565c0;color:white">'
        "<th>Id</th><th>Question</th><th>Gold layers</th><th>Gold answer</th>"
        "<th>A1</th><th>A3</th><th>Gap notes</th><th>A1 answer</th><th>A3 answer</th>"
        "</tr></thead><tbody>"
    )
    for qid in sorted(gold):
        g = gold[qid]
        w, b = by[qid]["wiki"], by[qid]["bundled"]
        sa = int(w.get("overall_score", 0) or 0)
        sb = int(b.get("overall_score", 0) or 0)
        layers = "<br>".join(f"<code>{html.escape(p)}</code>" for p in (g.get("gold_wiki_layers") or []))
        body.append("<tr>")
        body.append(f'<td style="background:#e3f2fd;vertical-align:top"><code>{qid}</code></td>')
        body.append(f'<td style="background:#fafafa;vertical-align:top">{cell_para(g["question"])}</td>')
        body.append(f'<td style="background:#e8eaf6;vertical-align:top;font-size:0.88em">{layers}</td>')
        body.append(f'<td style="background:#f3e5f5;vertical-align:top">{cell_para(g["answer"])}</td>')
        body.append(score_cell(sa, sb, list(w.get("top_hit_paths") or [])))
        body.append(score_cell(sb, sa, list(b.get("top_hit_paths") or [])))
        body.append(
            f'<td style="background:#fff8e1;vertical-align:top;font-size:0.92em">'
            f"{html.escape(_gap_explain(sa, sb, w, b))}</td>"
        )
        body.append(f'<td style="background:#e3f2fd;vertical-align:top">{cell_para(w.get("candidate", ""))}</td>')
        body.append(f'<td style="background:#ede7f6;vertical-align:top">{cell_para(b.get("candidate", ""))}</td>')
        body.append("</tr>")
    body.append("</tbody></table>")
    body.append("")
    body.append(
        f'<h2 id="wcj-notes" style="color:#1565c0;font-size:1.22em;font-weight:650;'
        f'border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Artifacts</h2>'
    )
    body.append("<ul>")
    body.append(f"<li>Suite: <code>{suite_path.relative_to(repo)}</code></li>")
    body.append(f"<li>Rows: <code>{results_path.relative_to(repo)}</code></li>")
    body.append("</ul>")

    out_path.write_text("\n".join(body) + "\n", encoding="utf-8")


def main() -> int:
    """CLI entry."""
    parser = argparse.ArgumentParser(description="Render wiki_compile_join analysis")
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--suite",
        type=Path,
        default=Path("tests/retail_multi_profiles/data/retail-wiki-compile-join-l10.json"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs_manual_gen/artifacts/TEST_ANALYSIS_A1_A3_WIKI_COMPILE_JOIN.md"),
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
