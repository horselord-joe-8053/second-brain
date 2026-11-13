#!/usr/bin/env bash
# Copy staged fridge PDFs into brain/retail/raw/sources/fridge-docs/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="${FRU_FRIDGE_DOCS_DIR:-$ROOT/docs_manual_gen/assets/raw/fridge-docs}"
DEST="$ROOT/brain/retail/raw/sources/fridge-docs"

copy_sku() {
  local folder="$1"
  mkdir -p "$DEST/$folder"
  for name in user-guide.pdf repair-guide.pdf; do
    if [[ ! -f "$SRC/$folder/$name" ]]; then
      echo "01_copy_manuals: missing $SRC/$folder/$name" >&2
      exit 1
    fi
    cp -f "$SRC/$folder/$name" "$DEST/$folder/$name"
  done
  echo "copied -> $DEST/$folder/"
}

test -d "$SRC" || { echo "Fridge docs dir not found: $SRC" >&2; exit 1; }

copy_sku samsung_RF28K9070SG
copy_sku ge_GNE27JYMFS
copy_sku kitchenaid_KRFF507HPS

echo "01_copy_manuals: done. Next: Hermes rescan or continue 02_generate_corpus.sh"
