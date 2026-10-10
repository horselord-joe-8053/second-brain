#!/usr/bin/env bash
# Copy 6 Samsung PDFs from Downloads into brain/retail/raw/sources/samsung-docs/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="${SAMSUNG_MANUALS_DIR:-/Users/jjw8053/Downloads/samsung_manuals}"
DEST="$ROOT/brain/retail/raw/sources/samsung-docs"

copy_pair() {
  local subdir="$1"
  local user_glob="$2"
  local repair_glob="$3"
  mkdir -p "$DEST/$subdir"
  shopt -s nullglob
  local u=( "$SRC"/$user_glob )
  local r=( "$SRC"/$repair_glob )
  if ((${#u[@]} == 0)) || ((${#r[@]} == 0)); then
    echo "01_copy_manuals: missing PDF in $SRC for $subdir (user=$user_glob repair=$repair_glob)" >&2
    exit 1
  fi
  cp -f "${u[0]}" "$DEST/$subdir/user-guide.pdf"
  cp -f "${r[0]}" "$DEST/$subdir/repair-guide.pdf"
  echo "copied -> $DEST/$subdir/"
}

test -d "$SRC" || { echo "Manuals dir not found: $SRC" >&2; exit 1; }

copy_pair a15 'A155G-User*.pdf' 'A155G_Repair*.pdf'
copy_pair a16 'A165G-User*.pdf' 'A165G-Repair*.pdf'
copy_pair a25 'A255G-User*.pdf' 'A255G-Repair*.pdf'

echo "01_copy_manuals: done. Next: Hermes rescan (HERMES_PREP_PROMPT.md) or continue 02_generate_corpus.sh"
