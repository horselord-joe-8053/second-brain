#!/usr/bin/env python3
"""One-off formatter: MRKD HTML for TEST_ANALYSIS_WIKI_VS_RAW_RAG_BCD.md sections 4–7."""

from __future__ import annotations

import ast
import html
import re
from pathlib import Path

DOC = Path(__file__).with_name("TEST_ANALYSIS_WIKI_VS_RAW_RAG_BCD.md")

H3_STYLE = (
    'style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em"'
)
# Lane §5–§7: three visual levels (case study → sample group → ticket).
H3_CASE_STYLE = (
    'style="color:#00695c;font-size:1.08em;font-weight:600;margin-top:1em;'
    'border-left:4px solid #00897b;padding-left:10px"'
)
H3_RAW_GROUP_STYLE = (
    'style="color:#1565c0;font-size:1.06em;font-weight:650;margin-top:1.2em;'
    'border-left:4px solid #42a5f5;padding-left:10px"'
)
H3_WIKI_GROUP_STYLE = (
    'style="color:#e65100;font-size:1.06em;font-weight:650;margin-top:1.2em;'
    'border-left:4px solid #ff9800;padding-left:10px"'
)
H4_RAW_TICKET_STYLE = (
    'style="color:#5e35b1;font-size:0.98em;font-weight:600;margin-top:1em"'
)
H4_WIKI_TICKET_STYLE = (
    'style="color:#2e7d32;font-size:0.98em;font-weight:600;margin-top:1em"'
)
H4_STYLE = H4_RAW_TICKET_STYLE  # default for formatter; renumber pass sets context
CARD = 'style="border:1px solid #90caf9;border-radius:8px;margin:1.25em 0;overflow:hidden"'
TH = 'style="background:#1565c0;color:white"'
ASP = 'style="background:#e3f2fd;font-weight:600;width:110px;vertical-align:top"'
PASS_OK = 'style="background:#c8e6c9;text-align:center"'
PASS_NO = 'style="background:#ffcdd2;text-align:center"'


def _esc(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return html.escape(s, quote=False).replace("&lt;strong&gt;", "<strong>").replace(
        "&lt;/strong&gt;", "</strong>"
    )


def _short_path(p: str, max_len: int = 72) -> str:
    p = p.strip().strip("`")
    if len(p) <= max_len:
        return p
    return "…" + p[-(max_len - 1) :]


def _parse_top5(text: str) -> list[str]:
    """Parse Python list after 'Wiki top-5:' or 'Raw top-5:' label."""
    chunk = text.strip()
    m = re.search(r"`(\[.*?\])`", chunk, re.DOTALL)
    if m:
        chunk = m.group(1)
    else:
        m2 = re.search(r"(\[[^\]]*(?:'[^']*'[^\]]*)*\])", chunk, re.DOTALL)
        if not m2:
            return []
        chunk = m2.group(1)
    try:
        return [str(x) for x in ast.literal_eval(chunk)]
    except (SyntaxError, ValueError):
        return []


def _pass_badge(val: str) -> str:
    v = val.strip().lower()
    if v == "true":
        return f'<td {PASS_OK}><span style="background:#2e7d32;color:white;padding:2px 6px">PASS</span></td>'
    return f'<td {PASS_NO}><span style="background:#c62828;color:white;padding:2px 6px">FAIL</span></td>'


def _truncate_quote(text: str, max_len: int = 2800) -> str:
    """Cap excerpt length while keeping whole lines when possible."""
    t = text.strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"


def _format_quote_body(raw: str) -> str:
    """Render retrieved-file excerpt with in-quote heading levels (MRKD quote style)."""
    raw = _truncate_quote(raw)
    if not raw or raw == "—":
        return '<span style="display:block;color:#9e9e9e">(no excerpt)</span>'
    parts: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        esc = html.escape(line)
        if stripped == "---":
            parts.append(
                '<span style="display:block;color:#9e9e9e;font-weight:600">'
                f"{esc}</span>"
            )
        elif re.match(r"^## PDF page \d+", stripped):
            parts.append(
                '<span style="display:block;color:#1565c0;font-size:1.08em;font-weight:700;'
                f'margin:0.65em 0 0.2em">{esc}</span>'
            )
        elif stripped.startswith("## "):
            parts.append(
                '<span style="display:block;color:#1565c0;font-size:1.02em;font-weight:650;'
                f'margin:0.5em 0 0.15em">{esc}</span>'
            )
        elif stripped.startswith("### Original figure") or stripped.startswith("!["):
            parts.append(
                '<span style="display:block;color:#00695c;font-size:0.9em;font-weight:600;'
                f'font-style:italic;margin:0.35em 0">{esc}</span>'
            )
        elif stripped.startswith("### "):
            parts.append(
                '<span style="display:block;color:#00695c;font-size:0.95em;font-weight:600;'
                f'margin:0.4em 0 0.1em">{esc}</span>'
            )
        elif stripped.startswith("#### "):
            parts.append(
                '<span style="display:block;color:#5e35b1;font-size:0.9em;font-weight:600;'
                f'margin:0.3em 0 0.08em">{esc}</span>'
            )
        elif stripped.startswith("# "):
            parts.append(
                '<span style="display:block;color:#0d47a1;font-size:1em;font-weight:700;'
                f'margin:0.25em 0">{esc}</span>'
            )
        elif re.match(r"^(type|title|created|updated|tags|related|sources):", stripped):
            parts.append(f'<span style="display:block;color:#546e7a">{esc}</span>')
        else:
            parts.append(f'<span style="display:block">{esc}</span>')
    return "".join(parts)


def _evidence_quote_cell(label: str, text: str, kind: str) -> str:
    """Side-by-side rank-1 quote panel (wiki vs raw), screenshot-style."""
    if kind == "wiki":
        border, outer, header = "#ffb74d", "#fff8e1", "#ffe0b2"
    else:
        border, outer, header = "#81c784", "#f1f8e9", "#c8e6c9"
    body = _format_quote_body(text)
    return (
        f'<td style="vertical-align:top;width:50%;padding:6px 4px">'
        f'<div style="border:1px solid {border};border-radius:8px;overflow:hidden;background:{outer}">'
        f'<div style="background:{header};padding:8px 10px;font-size:0.84em;font-weight:650;'
        f'color:#37474f;border-bottom:1px solid {border}">{html.escape(label)}</div>'
        f'<div style="padding:10px 12px;max-height:260px;overflow:auto;background:#fafafa;'
        f"font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:0.76em;"
        f'line-height:1.42;color:#263238">{body}</div></div></td>'
    )


def _excerpt_block(label: str, text: str, tint: str) -> str:
    """Legacy wrapper — tint ignored; kind inferred from label."""
    kind = "wiki" if "Wiki" in label else "raw"
    return _evidence_quote_cell(label, text, kind)


def _standalone_file_quote(caption: str, text: str, *, kind: str = "raw") -> str:
    """Single-column quoted excerpt (e.g. E02 case study snippet)."""
    border = "#81c784" if kind == "raw" else "#ffb74d"
    header_bg = "#c8e6c9" if kind == "raw" else "#ffe0b2"
    body = _format_quote_body(text)
    return (
        f'<div style="margin:0.6em 1em 1em;border:1px solid {border};border-radius:8px;overflow:hidden">'
        f'<div style="background:{header_bg};padding:8px 10px;font-size:0.84em;font-weight:650;'
        f'color:#37474f;border-bottom:1px solid {border}">{html.escape(caption)}</div>'
        f'<div style="padding:10px 12px;max-height:220px;overflow:auto;background:#fafafa;'
        f"font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:0.76em;"
        f'line-height:1.42;color:#263238">{body}</div></div>'
    )


def upgrade_file_quotes(text: str) -> str:
    """Replace legacy <pre> evidence blocks with structured quote panels."""
    wiki_pre = re.compile(
        r'<td style="background:#fff3e0;vertical-align:top;width:50%;font-size:0\.9em">'
        r"<strong>Wiki rank-1 evidence</strong><br>"
        r'<pre style="[^"]*">(.*?)</pre></td>',
        re.DOTALL,
    )
    raw_pre = re.compile(
        r'<td style="background:#e8f5e9;vertical-align:top;width:50%;font-size:0\.9em">'
        r"<strong>Raw rank-1 evidence</strong><br>"
        r'<pre style="[^"]*">(.*?)</pre></td>',
        re.DOTALL,
    )
    text = wiki_pre.sub(
        lambda m: _evidence_quote_cell(
            "Wiki rank-1 evidence",
            html.unescape(m.group(1)),
            "wiki",
        ),
        text,
    )
    text = raw_pre.sub(
        lambda m: _evidence_quote_cell(
            "Raw rank-1 evidence",
            html.unescape(m.group(1)),
            "raw",
        ),
        text,
    )
    case_pre = re.compile(
        r'<p style="margin:0\.6em 1em"><strong>Raw evidence snippet</strong> '
        r"\([^)]+\):</p>"
        r'<pre style="margin:0 1em 1em;font-size:0\.82em;background:#e8f5e9;padding:10px;'
        r'border-left:4px solid #2e7d32;max-height:200px;overflow:auto">(.*?)</pre>',
        re.DOTALL,
    )
    text = case_pre.sub(
        lambda m: _standalone_file_quote(
            "Quoted from raw/sources/…/ge_GNE27JYMFS/user-guide.md (rank-1 chunk)",
            html.unescape(m.group(1)),
            kind="raw",
        ),
        text,
    )
    # Already-upgraded cells: skip if no match left
    return text


def format_case_study_e02(block: str) -> str:
    """Turn E02 case study into tables (content preserved)."""
    gold = re.search(r"\*\*Gold:\*\* (.+)", block)
    wiki_line = re.search(r"\*\*Wiki:\*\* pass \*\*(\w+)\*\* · top paths: `(\[.*?\])`", block, re.DOTALL)
    raw_line = re.search(r"\*\*Raw:\*\* pass \*\*(\w+)\*\* · top paths: `(\[.*?\])`", block, re.DOTALL)
    raw_text_m = re.search(
        r"\*\*Raw base text \(GE user-guide\.md\):\*\*\s*```text\n(.*?)```",
        block,
        re.DOTALL,
    )
    wiki_issue = re.search(r"\*\*Wiki issue:\*\* (.+)", block, re.DOTALL)
    why_raw = re.search(r"\*\*Why raw wins:\*\* (.+)", block, re.DOTALL)

    wiki_paths = ast.literal_eval(wiki_line.group(2)) if wiki_line else []
    raw_paths = ast.literal_eval(raw_line.group(2)) if raw_line else []

    out = [
        f'<h3 id="test-wr-5-1-e02" {H3_CASE_STYLE}>'
        f"<code>ge_GNE27JYMFS-E02</code> (door alarm, 2 minutes)</h3>",
        f'<div {CARD}>',
        "<table>",
        f"<tr><td {ASP}>Gold answer</td>"
        f'<td style="background:#fff8e1">{_esc(gold.group(1) if gold else "")}</td></tr>',
        "</table>",
        "<table>",
        f"<tr {TH}><th>Arm</th><th>Judge</th><th>Rank-1 path (wiki hybrid vs raw chunk)</th></tr>",
        f"<tr><td {ASP}>Wiki</td>{_pass_badge(wiki_line.group(1) if wiki_line else 'False')}"
        f"<td><code>{_esc(_short_path(wiki_paths[0] if wiki_paths else ''))}</code></td></tr>",
        f"<tr><td {ASP}>Raw RAG</td>{_pass_badge(raw_line.group(1) if raw_line else 'True')}"
        f"<td><code>{_esc(_short_path(raw_paths[-1] if raw_paths else ''))}</code></td></tr>",
        "</table>",
        "<table>",
        f"<tr {TH}><th>Wiki top-3 (concept/entity heavy)</th><th>Raw top-2 (manual MD)</th></tr>",
        "<tr>",
        f'<td style="background:#ffebee;vertical-align:top"><ul style="margin:0.3em 0;padding-left:1.2em">'
        + "".join(f"<li><code>{_esc(_short_path(p, 56))}</code></li>" for p in wiki_paths[:3])
        + "</ul></td>",
        f'<td style="background:#e8f5e9;vertical-align:top"><ul style="margin:0.3em 0;padding-left:1.2em">'
        + "".join(f"<li><code>{_esc(_short_path(p, 56))}</code></li>" for p in raw_paths[:2])
        + "</ul></td>",
        "</tr></table>",
    ]
    if raw_text_m:
        out.append(
            _standalone_file_quote(
                "Quoted from raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md (Door Alarm)",
                raw_text_m.group(1).strip(),
                kind="raw",
            )
        )
    if wiki_issue:
        out.append(
            f'<p style="margin:0.5em 1em;background:#ffebee;padding:8px;border-left:4px solid #c62828">'
            f"<strong>Wiki miss:</strong> {_esc(wiki_issue.group(1).split(chr(10))[0])}</p>"
        )
    if why_raw:
        out.append(
            f'<p style="margin:0.5em 1em 1em;background:#e8f5e9;padding:8px;border-left:4px solid #2e7d32">'
            f"<strong>Why raw wins:</strong> {_esc(why_raw.group(1).split(chr(10))[0])}</p>"
        )
    out.append("</div>\n")
    return "\n".join(out)


def format_ticket_block(
    h3_line: str, body: str, *, ticket_label: str | None = None, h4_style: str | None = None
) -> str:
    """Convert one sample ticket into MRKD HTML card."""
    id_m = re.search(r"`([^`]+)`\s*\((\w+)\)", h3_line)
    ticket_id = id_m.group(1) if id_m else "ticket"
    diff = id_m.group(2) if id_m else ""
    slug_m = re.search(r'id="([^"]+)"', h3_line)
    slug = slug_m.group(1) if slug_m else f"test-wr-ticket-{ticket_id.lower()}"

    q_m = re.search(r"\*\*Question:\*\*\s*(.+?)(?=\n\n\*\*Gold)", body, re.DOTALL)
    g_m = re.search(r"\*\*Gold:\*\*\s*(.+?)(?=\n\n\| Arm)", body, re.DOTALL)
    wiki_row = re.search(r"\| Wiki \| (\w+) \| `([^`]+)` \|", body)
    raw_row = re.search(r"\| Raw \| (\w+) \| `([^`]+)` \|", body)
    wiki_top = (
        _parse_top5(body.split("Wiki top-5:", 1)[1].split("\n\n", 1)[0])
        if "Wiki top-5:" in body
        else []
    )
    raw_top = (
        _parse_top5(body.split("Raw top-5:", 1)[1].split("\n\n", 1)[0])
        if "Raw top-5:" in body
        else []
    )

    wiki_ex = re.search(
        r"\*\*Wiki rank-1 excerpt \(search evidence\):\*\*\s*```text\n(.*?)```",
        body,
        re.DOTALL,
    )
    raw_ex = re.search(
        r"\*\*Raw rank-1 excerpt \(search evidence\):\*\*\s*```text\n(.*?)```",
        body,
        re.DOTALL,
    )
    anal = re.search(r"_Analysis:_\s*(.+?)(?=\n\n<h3|\n\n<h2|\Z)", body, re.DOTALL)

    diff_badge = (
        f' <span style="background:#e3f2fd;padding:2px 6px;font-size:0.85em">{diff}</span>'
        if diff
        else ""
    )

    title = ticket_label if ticket_label else f"<code>{_esc(ticket_id)}</code>{diff_badge}"
    h4s = h4_style or H4_RAW_TICKET_STYLE
    parts = [
        f'<h4 id="{slug}" {h4s}>{title}</h4>\n',
        f'<div {CARD}>',
        "<table>",
        f"<tr><td {ASP}>Question</td><td>{_esc(q_m.group(1) if q_m else '')}</td></tr>",
        f"<tr><td {ASP}>Gold</td><td style=\"background:#fff8e1\">{_esc(g_m.group(1) if g_m else '')}</td></tr>",
        "</table>",
        "<table>",
        f"<tr {TH}><th>Arm</th><th>Judge</th><th>Rank-1 retrieved file</th></tr>",
    ]
    if wiki_row:
        parts.append(
            f"<tr><td {ASP}>Wiki hybrid</td>{_pass_badge(wiki_row.group(1))}"
            f"<td><code>{_esc(_short_path(wiki_row.group(2)))}</code></td></tr>"
        )
    if raw_row:
        parts.append(
            f"<tr><td {ASP}>Raw RAG</td>{_pass_badge(raw_row.group(1))}"
            f"<td><code>{_esc(_short_path(raw_row.group(2)))}</code></td></tr>"
        )
    parts.append("</table>")

    def path_list(paths: list[str]) -> str:
        if not paths:
            return "—"
        return (
            '<ol style="margin:0.2em 0;padding-left:1.3em;font-size:0.88em">'
            + "".join(f"<li><code>{_esc(_short_path(p, 64))}</code></li>" for p in paths[:5])
            + "</ol>"
        )

    parts.extend(
        [
            "<table>",
            f"<tr {TH}><th>Wiki top-5 paths</th><th>Raw top-5 paths</th></tr>",
            f"<tr><td style=\"vertical-align:top;background:#fff3e0\">{path_list(wiki_top)}</td>"
            f'<td style="vertical-align:top;background:#e8f5e9">{path_list(raw_top)}</td></tr>',
            "</table>",
            "<table><tr>",
            _excerpt_block("Wiki rank-1 evidence", wiki_ex.group(1) if wiki_ex else "—", "#fff3e0"),
            _excerpt_block("Raw rank-1 evidence", raw_ex.group(1) if raw_ex else "—", "#e8f5e9"),
            "</tr></table>",
        ]
    )
    if anal:
        parts.append(
            f'<p style="margin:0.8em 1em;background:#fff9c4;padding:8px">'
            f'<strong>Takeaway:</strong> {_esc(anal.group(1).strip())}</p>'
        )
    parts.append("</div>\n")
    return "\n".join(parts)


SECTION_4 = """
<h2 id="test-wr-4-path-mix" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. When raw RAG wins, what did wiki retrieve instead?</h2>

**Question this section answers:** On tickets where **wiki failed** and **raw RAG passed**, we inspect **only the wiki arm’s top-5 hit list** (not raw’s). We label each path by type, then count how often each type appears **across all slots**.

**How to read the counts:** Each ticket contributes up to **five** paths (top-k=5). Lane B has **24** raw-win tickets → up to **120** path slots. A count of **35** for `entity` means “entity pages occupied 35 of those 120 slots,” not “35 tickets.”

**Path kinds (wiki hybrid):**

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Kind</th><th>Path pattern</th><th>Typical content</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><code>wiki_source</code></td><td><code>wiki/sources/*</code></td><td>Compiled manual shard (often one PDF page)</td></tr>
<tr><td style="background:#e3f2fd"><code>concept</code></td><td><code>wiki/concepts/*</code></td><td>LLM-written topic page (may omit numeric gold)</td></tr>
<tr><td style="background:#e3f2fd"><code>entity</code></td><td><code>wiki/entities/*</code></td><td>Model/product summary card</td></tr>
<tr><td style="background:#e3f2fd"><code>other</code></td><td><code>wiki/index.md</code>, etc.</td><td>Index / misc wiki pages</td></tr>
</tbody>
</table>

**Slot mix on raw-win tickets (wiki top-5 only):**

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Lane</th><th>Raw-win tickets</th><th>Max slots</th><th><code>wiki_source</code></th><th><code>entity</code></th><th><code>concept</code></th><th><code>other</code></th><th>Pattern</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>B</strong></td><td>24</td><td>120</td><td>36 (30%)</td><td style="background:#fff3e0">35 (29%)</td><td style="background:#fff3e0">31 (26%)</td><td>18 (15%)</td><td>Concept + entity often <strong>crowd out</strong> the right source shard</td></tr>
<tr><td style="background:#e3f2fd"><strong>C</strong></td><td>26</td><td>130</td><td>50 (38%)</td><td style="background:#fff3e0">53 (41%)</td><td>1 (1%)</td><td>26 (20%)</td><td>Plain-text lane: wiki still pulls <strong>entity cards</strong> over full manual text</td></tr>
<tr><td style="background:#e3f2fd"><strong>D</strong></td><td>9</td><td>45</td><td style="background:#e8f5e9">28 (62%)</td><td>5 (11%)</td><td>3 (7%)</td><td>9 (20%)</td><td>Wiki often hits <strong>full-copy sources</strong>; raw wins are fewer and narrower</td></tr>
</tbody>
</table>

```mermaid
graph LR
  T[Raw-win ticket] --> W[Wiki hybrid top-5]
  W --> S[wiki_source shard]
  W --> E[entity card]
  W --> C[concept page]
  S --> OK[Sometimes enough]
  E --> MISS[Gold span missing in 8k window]
  C --> MISS
```

**Use in later sections:** Sample tickets in §5–§7 show **rank-1 file + excerpts** for the same questions; this table explains **why wiki’s top-k mix** correlates with those misses before you read each card.
"""

NUMBERING_LEGEND = """
<p style="font-size:0.88em;margin:0.35em 0 0.9em;line-height:1.5">
<strong>Numbering:</strong> <span style="color:#00695c;font-weight:650">N.1</span> case study ·
<span style="color:#1565c0;font-weight:650">N.2</span> raw-win sample group ·
<span style="color:#5e35b1;font-weight:650">N.2.x</span> raw-win ticket ·
<span style="color:#e65100;font-weight:650">N.3</span> wiki-win group ·
<span style="color:#2e7d32;font-weight:650">N.3.x</span> wiki-win ticket<br>
<strong>File quotes:</strong> amber panel = wiki rank-1 · green panel = raw rank-1 · monospace body with
<span style="color:#1565c0">## page</span> / <span style="color:#00695c">### section</span> / YAML frontmatter tinted inside the box.
</p>
"""

LANE_INTROS_BY_LETTER = {
    "b": """
<p style="background:#e3f2fd;padding:10px;border-left:4px solid #1976d2;margin:0.5em 0">
<strong>Lane B</strong> — compiled LLM Wiki on external Markdown (<code>brain/retail-md</code>).
Samples below: <strong>5</strong> raw-only wins (of 24) + <strong>5</strong> wiki-only wins (of 5). Each ticket is one HTML card: judge outcome, paths, side-by-side evidence.
</p>
"""
    + NUMBERING_LEGEND,
    "c": """
<p style="background:#e3f2fd;padding:10px;border-left:4px solid #1976d2;margin:0.5em 0">
<strong>Lane C</strong> — plain-text ingest (<code>brain/retail-txt</code>).
<strong>26</strong> raw-only wins, <strong>0</strong> wiki-only — only <strong>raw-win</strong> samples are shown (5 of 26).
</p>
"""
    + NUMBERING_LEGEND,
    "d": """
<p style="background:#e3f2fd;padding:10px;border-left:4px solid #1976d2;margin:0.5em 0">
<strong>Lane D</strong> — learned digest (<code>brain/retail-md-learned</code>); wiki uses <strong>full-copy</strong> <code>wiki/sources/</code>, raw uses <strong>split-less</strong> files under <code>raw/sources/</code>.
Samples: <strong>5</strong> raw-only (of 9) + <strong>5</strong> wiki-only (of 11).
</p>
"""
    + NUMBERING_LEGEND,
}

OUTLINE = """
1. [Headline quadrants](#test-wr-1-quadrants) — pass/fail matrix per lane.
2. [Performance](#test-wr-2-performance) — wall clock, per-stage latency, retrieval share.
3. [Why methods differ](#test-wr-3-mechanisms) — corpus, retrieval, win/loss patterns.
4. [Wiki top-k on raw wins](#test-wr-4-path-mix) — slot mix by path kind (counts explained).
5. [Lane B — external Markdown](#test-wr-5-lane-b) — `brain/retail-md` case studies + samples.
6. [Lane C — plain text](#test-wr-6-lane-c) — `brain/retail-txt` case studies + samples.
7. [Lane D — learned digest](#test-wr-7-lane-d) — wiki full-copy vs raw split-less.
8. [Appendix — ticket lists](#test-wr-8-appendix) — full raw-only / wiki-only ids.
"""

PERF_SECTION = """
<h2 id="test-wr-2-performance" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Performance (latency and wall clock)</h2>

**Sources:** per-row **`latency_ms`** in each run’s **`results.json`**; operator **`elapsed_sec`** in **`logs/ops/retail-lane-abcd-abcd-full-openai-v2.log`** and **`logs/ops/retail-lane-abcd-raw-abcd-raw-full-openai-v1.log`**; raw index in **`ops/runs/retail-lane-abcd-raw/abcd-raw-full-openai-v1-index/index_progress.jsonl`**. Lanes **B, C, D** only (**270** rows/arm). Same answer (**gpt-4o-mini**) and judge (**gemini-3.1-flash-lite**).

<h3 id="test-wr-2-1-wall" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.1 Wall clock (sequential benchmark)</h3>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Run</th><th>Rows</th><th>Wall time</th><th>≈ per row</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Wiki hybrid · <code>abcd-full-openai-v2</code></td><td>360 (A–D)</td><td><strong>2,936 s</strong> (~49.0 min)</td><td>~8.2 s</td></tr>
<tr><td style="background:#e3f2fd">Wiki hybrid · B/C/D (scaled)</td><td>270</td><td>~2,202 s (~36.7 min)</td><td>~8.2 s</td></tr>
<tr><td style="background:#e8f5e9">Raw vector RAG · <code>abcd-raw-full-openai-v1</code></td><td>270 (B–D)</td><td><strong>745 s</strong> (~12.4 min)</td><td>~2.8 s</td></tr>
<tr><td style="background:#fff3e0">Raw index preflight (B+C+D)</td><td>630 chunks</td><td><strong>20 s</strong> (13+4+3)</td><td>—</td></tr>
</tbody>
</table>

<h3 id="test-wr-2-2-latency" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.2 Per-row latency (ms) — B/C/D intersection</h3>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Stage</th><th>Wiki mean</th><th>Wiki p50</th><th>Wiki p95</th><th>Raw mean</th><th>Raw p50</th><th>Raw p95</th><th>Speedup (mean)</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>Retrieval</strong></td><td>4,393</td><td>4,422</td><td>8,877</td><td style="background:#e8f5e9">307</td><td style="background:#e8f5e9">262</td><td>620</td><td style="background:#e8f5e9"><strong>~14×</strong></td></tr>
<tr><td style="background:#e3f2fd">Answer LLM</td><td>1,281</td><td>1,133</td><td>2,362</td><td>1,126</td><td>1,031</td><td>1,768</td><td>~1.1×</td></tr>
<tr><td style="background:#e3f2fd">Judge LLM</td><td>887</td><td>1,155</td><td>1,719</td><td>869</td><td>1,108</td><td>1,660</td><td>~1.0×</td></tr>
<tr><td style="background:#e3f2fd"><strong>Row total</strong></td><td>6,561</td><td>6,302</td><td>11,234</td><td style="background:#e8f5e9">2,301</td><td style="background:#e8f5e9">2,507</td><td>3,549</td><td style="background:#e8f5e9"><strong>~2.9×</strong></td></tr>
</tbody>
</table>

**Retrieval share of row time:** wiki **67.0%** · raw **13.3%**.

<h3 id="test-wr-2-3-lane-p50" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.3 Lane-level row p50 (ms)</h3>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Lane</th><th>Wiki total p50</th><th>Wiki retrieval p50</th><th>Raw total p50</th><th>Raw retrieval p50</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>B</strong></td><td>6,224</td><td>4,085</td><td style="background:#e8f5e9">2,531</td><td style="background:#e8f5e9">252</td></tr>
<tr><td style="background:#e3f2fd"><strong>C</strong></td><td>5,288</td><td>3,179</td><td style="background:#e8f5e9">2,420</td><td style="background:#e8f5e9">250</td></tr>
<tr><td style="background:#e3f2fd"><strong>D</strong></td><td>7,505</td><td>4,830</td><td style="background:#e8f5e9">2,584</td><td style="background:#e8f5e9">292</td></tr>
</tbody>
</table>
"""


def preprocess(text: str) -> str:
    """Insert performance §2, renumber headings, replace old path-mix §."""
    outline_pat = re.compile(
        r"(<h2 id=\"test-wr-outline\"[^>]*>Document outline</h2>\s*)1\..*?7\..*?\n",
        re.DOTALL,
    )
    text = outline_pat.sub(lambda m: m.group(1) + OUTLINE.strip() + "\n\n", text)
    text = text.replace(
        'id="test-wr-2-mechanisms"',
        'id="test-wr-3-mechanisms"',
    )
    text = text.replace(
        ">2. Why methods differ</h2>",
        ">3. Why methods differ</h2>",
    )
    text = re.sub(
        r'<h2 id="test-wr-3-path-mix"[^>]*>3\. Retrieval path mix \(raw-only win tickets\)</h2>\s*'
        r"\*\*Lane B\*\*.*?"
        r"(?=<h2 id=\"test-wr-4-lane-b\")",
        SECTION_4.strip() + "\n\n",
        text,
        flags=re.DOTALL,
    )
    perf_pat = re.compile(
        r"(<h2 id=\"test-wr-1-quadrants\"[^>]*>1\. Headline quadrants</h2>.*?split-less digest\.\n)\n",
        re.DOTALL,
    )
    text = perf_pat.sub(lambda m: m.group(1) + "\n" + PERF_SECTION.strip() + "\n\n", text)
    # Renumber lane + appendix section titles and stable ids for outline links
    text = text.replace('id="test-wr-4-lane-b"', 'id="test-wr-5-lane-b"')
    text = text.replace(">4. Lane B —", ">5. Lane B —")
    text = text.replace('id="test-wr-5-lane-c"', 'id="test-wr-6-lane-c"')
    text = text.replace(">5. Lane C —", ">6. Lane C —")
    text = text.replace('id="test-wr-6-lane-d"', 'id="test-wr-7-lane-d"')
    text = text.replace(">6. Lane D —", ">7. Lane D —")
    text = text.replace('id="test-wr-7-appendix"', 'id="test-wr-8-appendix"')
    text = text.replace(">7. Appendix —", ">8. Appendix —")
    text = text.replace('id="test-wr-4-1-e02"', 'id="test-wr-5-1-e02"')
    text = text.replace(">4.1 Case study —", ">5.1 Case study —")
    text = text.replace(
        "**Last updated:** 2026-10-21.",
        "**Last updated:** 2026-10-21 (accuracy + performance + MRKD samples).",
    )
    return text

SECTION_DIV = {
    "raw": (
        '<h3 id="{id}" {h3}>{num} Raw wins (wiki failed) — sample tickets</h3>\n'
        '<p style="margin:0 0 0.8em"><span style="background:#c8e6c9;padding:2px 6px">'
        "Judge: wiki FAIL → raw PASS</span> — evidence cards below.</p>\n"
    ),
    "wiki": (
        '<h3 id="{id}" {h3}>{num} Wiki wins (raw failed) — sample tickets</h3>\n'
        '<p style="margin:0 0 0.8em"><span style="background:#fff3e0;padding:2px 6px">'
        "Judge: wiki PASS → raw FAIL</span> — often full-copy wiki source or entity with gold facts.</p>\n"
    ),
}


class _LaneSampleNumbering:
    """Assign N.M / N.M.K headings within one lane block (§5–§7)."""

    def __init__(self, lane_major: int) -> None:
        self.lane = lane_major
        self.has_case = False
        self.raw_group: int | None = None
        self.wiki_group: int | None = None
        self.raw_ticket = 0
        self.wiki_ticket = 0
        self.mode: str = "idle"  # idle | raw | wiki

    def _next_group_index(self) -> int:
        return 2 if self.has_case else 1

    def case_heading(self, slug: str, title_rest: str) -> str:
        self.has_case = True
        self.mode = "idle"
        return (
            f'<h3 id="{slug}" {H3_CASE_STYLE}>{self.lane}.1 {title_rest}</h3>\n'
        )

    def raw_group_heading(self, slug: str) -> str:
        self.raw_group = self._next_group_index()
        self.wiki_group = None
        self.raw_ticket = 0
        self.wiki_ticket = 0
        self.mode = "raw"
        num = f"{self.lane}.{self.raw_group}"
        return SECTION_DIV["raw"].format(id=slug, h3=H3_RAW_GROUP_STYLE, num=num)

    def wiki_group_heading(self, slug: str, *, none_lane_c: bool = False) -> str:
        if none_lane_c:
            self.wiki_group = self.raw_group + 1 if self.raw_group else 2
            num = f"{self.lane}.{self.wiki_group}"
            return (
                f'<h3 id="{slug}" {H3_WIKI_GROUP_STYLE}>{num} Wiki wins (raw failed)</h3>\n'
                '<p style="background:#e8f5e9;padding:8px"><strong>None</strong> — '
                "Lane C had <strong>0</strong> wiki-only wins on this run.</p>\n"
            )
        base = self.raw_group if self.raw_group is not None else self._next_group_index()
        self.wiki_group = base + 1
        self.mode = "wiki"
        self.wiki_ticket = 0
        num = f"{self.lane}.{self.wiki_group}"
        return SECTION_DIV["wiki"].format(id=slug, h3=H3_WIKI_GROUP_STYLE, num=num)

    def ticket_heading(self, h4_line: str) -> str:
        slug_m = re.search(r'id="([^"]+)"', h4_line)
        slug = slug_m.group(1) if slug_m else "test-wr-ticket"
        id_m = re.search(r"<code>([^<]+)</code>", h4_line)
        ticket_id = id_m.group(1) if id_m else "ticket"
        diff_m = re.search(r">(\w+)</span>\s*</h4>", h4_line)
        diff_badge = (
            f' <span style="background:#e3f2fd;padding:2px 6px;font-size:0.85em">{diff_m.group(1)}</span>'
            if diff_m
            else ""
        )
        if self.mode == "wiki" and self.wiki_group is not None:
            self.wiki_ticket += 1
            num = f"{self.lane}.{self.wiki_group}.{self.wiki_ticket}"
            style = H4_WIKI_TICKET_STYLE
        else:
            if self.raw_group is None:
                self.raw_group = self._next_group_index()
                self.mode = "raw"
            self.raw_ticket += 1
            num = f"{self.lane}.{self.raw_group}.{self.raw_ticket}"
            style = H4_RAW_TICKET_STYLE
        return (
            f'<h4 id="{slug}" {style}>{num} <code>{html.escape(ticket_id)}</code>{diff_badge}</h4>\n'
        )


def apply_sample_numbering_and_styles(text: str) -> str:
    """Post-pass: numbered N.M / N.M.K headings + level colors in §5–§7."""
    lane_h2 = list(
        re.finditer(r'<h2 id="test-wr-(\d+)-lane-[bcd]"', text)
    )
    appendix_m = re.search(r'<h2 id="test-wr-8-appendix"', text)
    appendix_pos = appendix_m.start() if appendix_m else len(text)
    if not lane_h2:
        return text

    parts: list[str] = []
    pos = 0
    for i, m in enumerate(lane_h2):
        parts.append(text[pos : m.start()])
        lane_major = int(m.group(1))
        end_h2 = text.find("</h2>", m.start())
        if end_h2 == -1:
            continue
        end_h2 += len("</h2>")
        parts.append(text[m.start():end_h2])
        num = _LaneSampleNumbering(lane_major)
        rest_start = end_h2
        rest_end = lane_h2[i + 1].start() if i + 1 < len(lane_h2) else appendix_pos
        block = text[rest_start:rest_end]
        pos = rest_end
        out: list[str] = []
        token_re = re.compile(
            r'(<h3 id="test-wr-5-1-e02"[^>]*>.*?</h3>|'
            r'<h3 id="test-wr-lane-[bcd]-raw-samples"[^>]*>.*?</h3>|'
            r'<h3 id="test-wr-lane-c-wiki-samples"[^>]*>.*?</h3>|'
            r'<h3 id="test-wr-lane-[bcd]-wiki-samples"[^>]*>.*?</h3>|'
            r'<h4 id="test-wr-ticket-[^"]+"[^>]*>.*?</h4>)',
            re.DOTALL,
        )
        bpos = 0
        banner_p = re.compile(
            r'\s*<p style="margin:0 0 0\.8em"><span style="background:#c8e6c9[^"]*">'
            r"[^<]*</span> — evidence cards below\.</p>",
            re.DOTALL,
        )
        wiki_banner_p = re.compile(
            r'\s*<p style="margin:0 0 0\.8em"><span style="background:#fff3e0[^"]*">'
            r"[^<]*</span> — often full-copy wiki source[^<]*</p>",
            re.DOTALL,
        )
        while True:
            tm = token_re.search(block, bpos)
            if not tm:
                out.append(block[bpos:])
                break
            out.append(block[bpos : tm.start()])
            tag = tm.group(1)
            bpos = tm.end()
            if "test-wr-5-1-e02" in tag or "Case study" in tag:
                title_m = re.search(r">(?:\d+\.\d+\s+)?(.+)</h3>", tag, re.DOTALL)
                title_rest = (title_m.group(1).strip() if title_m else "").strip()
                if title_rest and not title_rest.lower().startswith("case study"):
                    title_rest = f"Case study — {title_rest}"
                out.append(num.case_heading("test-wr-5-1-e02", title_rest))
            elif "raw-samples" in tag:
                slug_m = re.search(r'id="([^"]+)"', tag)
                out.append(num.raw_group_heading(slug_m.group(1) if slug_m else "raw-samples"))
                skip = banner_p.match(block, bpos)
                if skip:
                    bpos = skip.end()
            elif "lane-c-wiki-samples" in tag:
                out.append(num.wiki_group_heading("test-wr-lane-c-wiki-samples", none_lane_c=True))
                skip = re.match(
                    r'\s*<p style="background:#e8f5e9;padding:8px"><strong>None</strong> — '
                    r"Lane C had <strong>0</strong> wiki-only wins on this run\.</p>",
                    block[bpos:],
                )
                if skip:
                    bpos += skip.end()
            elif "wiki-samples" in tag:
                slug_m = re.search(r'id="([^"]+)"', tag)
                out.append(num.wiki_group_heading(slug_m.group(1) if slug_m else "wiki-samples"))
                skip = wiki_banner_p.match(block, bpos)
                if skip:
                    bpos = skip.end()
            elif "test-wr-ticket-" in tag:
                out.append(num.ticket_heading(tag))
            else:
                out.append(tag)
        parts.append("".join(out))
    parts.append(text[pos:])
    merged = "".join(parts)
    # Safety: if Lane D was duplicated by an older pass, keep the first block only.
    d_heads = [m.start() for m in re.finditer(r'<h2 id="test-wr-7-lane-d"', merged)]
    if len(d_heads) > 1:
        app = re.search(r'<h2 id="test-wr-8-appendix"', merged[d_heads[1] :])
        if app:
            merged = merged[: d_heads[1]] + merged[d_heads[1] + app.start() :]
    # Drop duplicate judge banner lines left from older glued markup.
    merged = re.sub(
        r'(<p style="margin:0 0 0\.8em"><span style="background:#c8e6c9[^"]*">'
        r"[^<]*</span> — evidence cards below\.</p>\s*){2,}",
        r"\1",
        merged,
    )
    merged = re.sub(
        r"(<p style=\"background:#e8f5e9;padding:8px\"><strong>None</strong> — Lane C had <strong>0</strong> wiki-only wins on this run\.</p>\n?){2,}",
        r"\1",
        merged,
    )
    if NUMBERING_LEGEND.strip() not in merged:
        merged = merged.replace(
            "Each ticket is one HTML card: judge outcome, paths, side-by-side evidence.\n</p>",
            "Each ticket is one HTML card: judge outcome, paths, side-by-side evidence.\n</p>"
            + NUMBERING_LEGEND,
            1,
        )
        merged = merged.replace(
            "only <strong>raw-win</strong> samples are shown (5 of 26).\n</p>",
            "only <strong>raw-win</strong> samples are shown (5 of 26).\n</p>" + NUMBERING_LEGEND,
            1,
        )
        merged = merged.replace(
            "<strong>5</strong> wiki-only (of 11).\n</p>",
            "<strong>5</strong> wiki-only (of 11).\n</p>" + NUMBERING_LEGEND,
            1,
        )
    return upgrade_file_quotes(merged)


def main() -> None:
    text = preprocess(DOC.read_text(encoding="utf-8"))

    # Split tail from lane B h2
    m5 = re.search(r'(<h2 id="test-wr-5-lane-b".*)', text, re.DOTALL)
    if not m5:
        raise SystemExit("section 5 (lane B) not found after preprocess")
    head = text[: m5.start()]
    tail = m5.group(1)

    m8 = re.search(r'<h2 id="test-wr-8-appendix"', tail)
    lane_body = tail[: m8.start()] if m8 else tail
    appendix = tail[m8.start() :] if m8 else ""

    # Process lane_body: split on h2/h3
    pieces: list[str] = []
    current_lane: str | None = None
    raw_div_count = 0
    wiki_div_count = 0

    chunks = re.split(r"(<h2 id=\"test-wr-\d+-lane-[bcd]\"[^>]*>.*?</h2>)", lane_body)
    # chunks[0] may be empty; then alternating h2, content
    i = 0
    while i < len(chunks):
        chunk = chunks[i]
        h2_m = re.match(r'<h2 id="(test-wr-\d+-lane-[bcd])"', chunk)
        if h2_m:
            lane_id = h2_m.group(1)
            pieces.append(chunk)
            letter_m = re.search(r"lane-([bcd])", lane_id)
            letter = letter_m.group(1) if letter_m else "b"
            pieces.append(LANE_INTROS_BY_LETTER.get(letter, ""))
            current_lane = lane_id
            i += 1
            if i < len(chunks):
                content = chunks[i]
                i += 1
            else:
                content = ""
            # split content by h3
            h3_parts = re.split(r"(<h3 id=\"[^\"]+\"[^>]*>.*?</h3>)", content)
            j = 0
            while j < len(h3_parts):
                part = h3_parts[j]
                if part.startswith("<h3"):
                    if "test-wr-5-1-e02" in part or "test-wr-4-1-e02" in part:
                        j += 1
                        body = h3_parts[j] if j + 1 < len(h3_parts) else ""
                        j += 1
                        pieces.append(format_case_study_e02(part + body))
                        continue
                    if "raw-wins-samples" in part:
                        raw_div_count += 1
                        letter_m = re.search(r"lane-([bcd])", current_lane or "")
                        sid = f"test-wr-lane-{letter_m.group(1) if letter_m else 'b'}-raw-samples"
                        pieces.append(
                            f'<h3 id="{sid}" {H3_RAW_GROUP_STYLE}>'
                            "Raw wins (wiki failed) — sample tickets</h3>\n"
                            '<p style="margin:0 0 0.8em"><span style="background:#c8e6c9;padding:2px 6px">'
                            "Judge: wiki FAIL → raw PASS</span> — evidence cards below.</p>\n"
                        )
                        j += 1
                        continue
                    if "wiki-wins-samples" in part:
                        wiki_div_count += 1
                        if current_lane == "test-wr-6-lane-c":
                            pieces.append(
                                f'<h3 id="test-wr-lane-c-wiki-samples" {H3_STYLE}>'
                                "Wiki wins (raw failed)</h3>"
                                '<p style="background:#e8f5e9;padding:8px">'
                                "<strong>None</strong> — Lane C had <strong>0</strong> wiki-only wins on this run.</p>"
                            )
                        else:
                            letter_m = re.search(r"lane-([bcd])", current_lane or "")
                            sid = f"test-wr-lane-{letter_m.group(1) if letter_m else 'b'}-wiki-samples"
                            pieces.append(
                                f'<h3 id="{sid}" {H3_WIKI_GROUP_STYLE}>'
                                "Wiki wins (raw failed) — sample tickets</h3>\n"
                                '<p style="margin:0 0 0.8em"><span style="background:#fff3e0;padding:2px 6px">'
                                "Judge: wiki PASS → raw FAIL</span> — often full-copy wiki source "
                                "or entity with gold facts.</p>\n"
                            )
                        j += 1
                        continue
                    if "test-wr-ticket-" in part:
                        j += 1
                        body = h3_parts[j] if j < len(h3_parts) else ""
                        j += 1
                        pieces.append(format_ticket_block(part, body))
                        continue
                    pieces.append(part)
                    j += 1
                else:
                    if part.strip():
                        pieces.append(part)
                    j += 1
        else:
            if chunk.strip():
                pieces.append(chunk)
            i += 1

    new_tail = "".join(pieces) + appendix
    # Format appendix with HTML table
    new_tail = format_appendix(new_tail)
    full = apply_sample_numbering_and_styles(head + new_tail)
    DOC.write_text(full, encoding="utf-8")
    print(f"Wrote {DOC} ({DOC.stat().st_size} bytes)")


def format_appendix(text: str) -> str:
    """Turn appendix bullet lists into a compact HTML table."""
    m = re.search(
        r'(<h2 id="test-wr-8-appendix"[^>]*>8\. Appendix[^<]*</h2>\s*)(.*)\Z',
        text,
        re.DOTALL,
    )
    if not m:
        return text
    body = m.group(2)
    rows = []
    for lane in ("B", "C", "D"):
        ro = re.search(rf"\*\*Lane {lane} raw-only \(\d+\):\*\* `(.+?)`", body, re.DOTALL)
        wo = re.search(rf"\*\*Lane {lane} wiki-only \(\d+\):\*\* `(.+?)`", body, re.DOTALL)
        raw_n = re.search(rf"\*\*Lane {lane} raw-only \((\d+)\)", body)
        wiki_n = re.search(rf"\*\*Lane {lane} wiki-only \((\d+)\)", body)
        raw_ids = (ro.group(1) if ro else "").replace("\n", " ").strip()
        wiki_ids = (wo.group(1) if wo else "—").replace("\n", " ").strip()
        rows.append(
            f"<tr><td style=\"background:#e3f2fd\"><strong>{lane}</strong></td>"
            f"<td>{raw_n.group(1) if raw_n else '?'}</td>"
            f'<td style="font-size:0.82em;max-width:420px">{html.escape(raw_ids)}</td>'
            f"<td>{wiki_n.group(1) if wiki_n else '?'}</td>"
            f'<td style="font-size:0.82em;max-width:420px">{html.escape(wiki_ids)}</td></tr>'
        )
    table = (
        m.group(1)
        + "<table><thead><tr "
        + TH
        + "><th>Lane</th><th>Raw-only count</th><th>Raw-only ids (truncated)</th>"
        + "<th>Wiki-only count</th><th>Wiki-only ids (truncated)</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>\n"
    )
    return text[: m.start()] + table


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--renumber-only":
        DOC.write_text(
            apply_sample_numbering_and_styles(DOC.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
        print(f"Renumbered {DOC}")
    elif len(sys.argv) > 1 and sys.argv[1] == "--upgrade-quotes-only":
        text = upgrade_file_quotes(DOC.read_text(encoding="utf-8"))
        DOC.write_text(text, encoding="utf-8")
        print(f"Upgraded quotes in {DOC}")
    else:
        main()
