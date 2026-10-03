#!/usr/bin/env bash
# Phase 2: copy specific/specs and plans into docs/.

set -euo pipefail

REPO_ROOT="${1:-.}"
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
CORE="$(cd "$(dirname "$0")/.." && pwd)"
KIT="$(cd "$CORE/.." && pwd)"
SPECIFIC="$KIT/specific"
BOOTSTRAP="$SPECIFIC/bootstrap.md"

if [[ ! -d "$SPECIFIC/specs" ]]; then
  echo "seed-product: missing $SPECIFIC/specs" >&2
  exit 1
fi

echo "== seed-product: repo=$REPO_ROOT =="

mkdir -p "$REPO_ROOT/docs/specs" "$REPO_ROOT/docs/plans"
for f in "$SPECIFIC/specs/"*.md; do
  [[ -f "$f" ]] || continue
  cp "$f" "$REPO_ROOT/docs/specs/"
  echo "seed-product: docs/specs/$(basename "$f")"
done

if [[ -d "$SPECIFIC/plans" ]]; then
  for f in "$SPECIFIC/plans/"*.md; do
    [[ -f "$f" ]] || continue
    cp "$f" "$REPO_ROOT/docs/plans/"
    echo "seed-product: docs/plans/$(basename "$f")"
  done
fi

eval "$(bash "$CORE/scripts/parse-bootstrap-meta.sh" "$BOOTSTRAP")"
IFS=',' read -ra MODS <<< "${BOOTSTRAP_PHASE2_MODULES// /}"
for m in "${MODS[@]}"; do
  [[ -n "$m" ]] || continue
  bash "$CORE/scripts/apply-module.sh" "$REPO_ROOT" "$m"
done

ENV_APPEND="$BOOTSTRAP_ENV_APPEND"
if [[ -f "$REPO_ROOT/backend/.env" ]] && [[ "$ENV_APPEND" != "none" ]] && [[ "$ENV_APPEND" != "false" ]]; then
  SNIPPET="$KIT/modules/webapp/templates/$ENV_APPEND"
  if [[ -f "$SNIPPET" ]] && ! grep -q 'LLM_API_KEY' "$REPO_ROOT/backend/.env" 2>/dev/null; then
    echo "" >> "$REPO_ROOT/backend/.env"
    cat "$SNIPPET" >> "$REPO_ROOT/backend/.env"
    echo "seed-product: appended $ENV_APPEND"
  fi
fi

echo "seed-product: done."
