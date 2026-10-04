#!/usr/bin/env bash
# Optional helper: copy file into brain/raw/sources/<channel>/ with optional manifest hint.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CHANNEL="${1:?usage: ingest.sh <channel> <file>}"
FILE="${2:?usage: ingest.sh <channel> <file>}"
DEST="$ROOT/brain/raw/sources/$CHANNEL/$(basename "$FILE")"
mkdir -p "$(dirname "$DEST")"
cp -f "$FILE" "$DEST"
echo "ingest.sh: copied → $DEST (trigger Nashsu Source Watch / rescan)"
