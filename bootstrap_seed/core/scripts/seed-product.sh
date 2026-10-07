#!/usr/bin/env bash
# Phase 2: read ledger from seed_grow/; apply phase2_modules only (no copy into docs/).

set -euo pipefail

REPO_ROOT="${1:-.}"
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
CORE="$(cd "$(dirname "$0")/.." && pwd)"
KIT="$(cd "$CORE/.." && pwd)"
GROW="$REPO_ROOT/seed_grow"
BOOTSTRAP="$GROW/bootstrap.md"

if [[ ! -f "$BOOTSTRAP" ]]; then
  echo "seed-product: missing $BOOTSTRAP" >&2
  exit 1
fi

echo "== seed-product: repo=$REPO_ROOT (seed_grow) =="

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

echo "seed-product: done"
