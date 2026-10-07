#!/usr/bin/env bash
# Append one bootstrap progress line to seed_grow/progress.jsonl (zone 2). Never writes under the skill tree.

set -euo pipefail

# shellcheck source=fabrication-paths.sh
source "$(dirname "$0")/fabrication-paths.sh"
fab_load_paths "${BASH_SOURCE[0]}"

REPO_ROOT="${1:-}"
CHECKPOINT="${2:-}"
STATUS="${3:-done}"
PHASE="${4:-}"

if [[ -z "$REPO_ROOT" || -z "$CHECKPOINT" ]]; then
  echo "append-checkpoint: usage: append-checkpoint.sh <repo-root> <checkpoint-id> [done|failed] [phase]" >&2
  exit 1
fi

REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"

case "$REPO_ROOT" in
  "$FAB_ROOT"|"$FAB_ROOT"/*)
    echo "append-checkpoint: refuse to write progress inside skill directory" >&2
    exit 1
    ;;
esac

LOG="$REPO_ROOT/seed_grow/progress.jsonl"
mkdir -p "$REPO_ROOT/seed_grow"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
python3 - "$LOG" "$TS" "$PHASE" "$CHECKPOINT" "$STATUS" <<'PY'
import json, sys
path, ts, phase, checkpoint, status = sys.argv[1:6]
line = {"ts": ts, "phase": phase, "checkpoint": checkpoint, "status": status}
with open(path, "a", encoding="utf-8") as f:
    f.write(json.dumps(line, separators=(",", ":")) + "\n")
PY

if [[ -f "$FAB_ASSETS/render-roadmap.sh" ]]; then
  bash "$FAB_ASSETS/render-roadmap.sh" "$REPO_ROOT" || true
fi

echo "append-checkpoint: $CHECKPOINT ($STATUS) -> $LOG"
