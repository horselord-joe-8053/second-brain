#!/usr/bin/env bash
# Copy bootstrap_general/utils/ (or kit-adjacent utils) to <repo-root>/utils when absent.
# Never overwrites an existing repo-root utils/, and never treats the kit copy as the destination.

set -euo pipefail

REPO_ROOT="${1:-.}"
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
AGNOSTIC="$(cd "$(dirname "$0")/.." && pwd)"
KIT="$(cd "$AGNOSTIC/.." && pwd)"
SRC="$KIT/utils"
if [[ ! -d "$SRC" ]] && [[ -d "$KIT/../utils" ]]; then
  SRC="$KIT/../utils"
fi
DEST="$REPO_ROOT/utils"

if [[ ! -d "$SRC" ]]; then
  echo "seed-utils: missing kit utils/ and ../utils; skip or add bootstrap_general/utils" >&2
  exit 1
fi

# Running the kit from inside itself: destination would be the source tree.
if [[ "$DEST" == "$SRC" ]]; then
  echo "seed-utils: repo root is the kit; nothing to copy."
  exit 0
fi

if [[ -e "$DEST" ]]; then
  echo "seed-utils: $DEST already exists; leaving it in place."
  exit 0
fi

mkdir -p "$DEST"
cp -R "$SRC/." "$DEST/"
echo "seed-utils: copied $SRC -> $DEST"
