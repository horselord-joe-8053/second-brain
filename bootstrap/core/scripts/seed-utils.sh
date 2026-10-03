#!/usr/bin/env bash
# Copy bootstrap/utils/ to <repo-root>/utils when absent.

set -euo pipefail

REPO_ROOT="${1:-.}"
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
CORE="$(cd "$(dirname "$0")/.." && pwd)"
KIT="$(cd "$CORE/.." && pwd)"
DEST="$REPO_ROOT/utils"
SRC="$KIT/utils"

if [[ ! -d "$SRC" ]]; then
  echo "seed-utils: missing $SRC" >&2
  exit 1
fi

if [[ "$DEST" == "$SRC" ]]; then
  echo "seed-utils: repo root is the kit utils tree; skip."
  exit 0
fi

if [[ -e "$DEST" ]]; then
  echo "seed-utils: $DEST exists; leaving in place."
  exit 0
fi

mkdir -p "$DEST"
cp -R "$SRC/." "$DEST/"
echo "seed-utils: copied $SRC -> $DEST"
