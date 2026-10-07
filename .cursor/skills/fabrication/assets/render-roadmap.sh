#!/usr/bin/env bash
# Build seed_grow/roadmap.html from references/checkpoints.json and seed_grow/progress.jsonl.

set -euo pipefail

# shellcheck source=../scripts/fabrication-paths.sh
source "$(dirname "$0")/../scripts/fabrication-paths.sh"
fab_load_paths "${BASH_SOURCE[0]}"

REPO_ROOT="${1:-.}"
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"

CATALOG="$FAB_REF/checkpoints.json"
LOG="$REPO_ROOT/seed_grow/progress.jsonl"
OUT="$REPO_ROOT/seed_grow/roadmap.html"

mkdir -p "$REPO_ROOT/seed_grow"
python3 - "$CATALOG" "$LOG" "$OUT" <<'PY'
import json
import html
import sys
from pathlib import Path

catalog_path, log_path, out_path = map(Path, sys.argv[1:4])
catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
entries = []
if log_path.is_file():
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))

last_by_id = {}
for e in entries:
    cid = e.get("checkpoint")
    if cid:
        last_by_id[cid] = e

latest = entries[-1] if entries else None
current_id = latest.get("checkpoint") if latest else None

nodes = []
for cp in catalog.get("checkpoints", []):
    cid = cp["id"]
    last = last_by_id.get(cid)
    done = last is not None and last.get("status") == "done"
    current = cid == current_id
    label = cp.get("label", cid)
    cls = "node"
    if done:
        cls += " done"
    if current:
        cls += " current"
    nodes.append(f'<li class="{cls}"><span class="label">{html.escape(label)}</span><code>{html.escape(cid)}</code></li>')

doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Bootstrap roadmap</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #fafafa; }}
ol {{ list-style: none; padding: 0; max-width: 28rem; }}
.node {{ padding: 0.75rem 1rem; margin: 0.5rem 0; border-radius: 8px; background: #fff; border: 1px solid #ddd; }}
.node.done {{ border-color: #2e7d32; background: #e8f5e9; }}
.node.current {{ box-shadow: 0 0 0 2px #1976d2; animation: pulse 1.2s ease-in-out infinite; }}
@keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.85; }} }}
.label {{ font-weight: 600; display: block; }}
code {{ font-size: 0.85em; color: #555; }}
</style>
</head>
<body>
<h1>Bootstrap progress</h1>
<ol>
{"".join(nodes)}
</ol>
</body>
</html>
"""
out_path.write_text(doc, encoding="utf-8")
PY

echo "render-roadmap: wrote $OUT"
