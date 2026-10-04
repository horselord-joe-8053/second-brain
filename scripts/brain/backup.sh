#!/usr/bin/env bash
# AC-SB7: rsync brain/ corpus to a timestamped directory (local backup stub).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="${1:-$ROOT/backups/brain-$(date +%Y%m%d-%H%M%S)}"
mkdir -p "$DEST"
rsync -a --exclude '.llm-wiki/' "$ROOT/brain/" "$DEST/"
echo "backup.sh: copied brain/ → $DEST (excluded .llm-wiki/)"
