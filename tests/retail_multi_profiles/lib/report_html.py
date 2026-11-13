"""HTML scoreboard from results.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def render_scoreboard_html(results: dict[str, Any]) -> str:
    """Colored comparison table (extesttab-friendly subset)."""
    rows_html = []
    for row in results.get("rows") or []:
        bg = "#e8f5e9" if row.get("pass") else "#ffebee"
        top = (row.get("top_paths") or ["—"])[0]
        rows_html.append(
            f"<tr style='background:{bg}'>"
            f"<td>{row.get('lane')}</td>"
            f"<td><code>{row.get('question_id')}</code></td>"
            f"<td>{row.get('difficulty')}</td>"
            f"<td>{'PASS' if row.get('pass') else 'FAIL'}</td>"
            f"<td><code>{top}</code></td>"
            f"</tr>"
        )
    body = "\n".join(rows_html)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/><title>Lane benchmark {results.get('run_id','')}</title></head>
<body>
<h1>Retail lane benchmark — {results.get('run_id','')}</h1>
<p>Kind: <strong>{results.get('kind','')}</strong></p>
<table border="1" cellpadding="6" cellspacing="0">
<thead><tr style="background:#1565c0;color:white">
<th>Lane</th><th>Question</th><th>Diff</th><th>Pass</th><th>Top path</th>
</tr></thead>
<tbody>
{body}
</tbody></table>
</body></html>
"""


def write_scoreboard_html(results_path: Path) -> Path:
    """Write sibling scoreboard.html."""
    data = json.loads(results_path.read_text(encoding="utf-8"))
    out = results_path.parent / "scoreboard.html"
    out.write_text(render_scoreboard_html(data), encoding="utf-8")
    return out
