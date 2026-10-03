#!/usr/bin/env bash
# Phase 2: copy app_specific/specs/*.md and app_specific/plans/*.md into the app repo.

set -euo pipefail

REPO_ROOT="${1:-.}"
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
AGNOSTIC="$(cd "$(dirname "$0")/.." && pwd)"
KIT="$(cd "$AGNOSTIC/.." && pwd)"
APP_SPECIFIC="$KIT/app_specific"
BOOTSTRAP="$APP_SPECIFIC/bootstrap.md"

if [[ ! -d "$APP_SPECIFIC/specs" ]]; then
  echo "seed-product: missing $APP_SPECIFIC/specs" >&2
  exit 1
fi

echo "== seed-product: repo=$REPO_ROOT =="

mkdir -p "$REPO_ROOT/docs/specs" "$REPO_ROOT/docs/plans"
for f in "$APP_SPECIFIC/specs/"*.md; do
  [[ -f "$f" ]] || continue
  cp "$f" "$REPO_ROOT/docs/specs/"
  echo "seed-product: wrote docs/specs/$(basename "$f")"
done

if [[ -d "$APP_SPECIFIC/plans" ]]; then
  copied_plan=0
  for f in "$APP_SPECIFIC/plans/"*.md; do
    [[ -f "$f" ]] || continue
    cp "$f" "$REPO_ROOT/docs/plans/"
    echo "seed-product: wrote docs/plans/$(basename "$f")"
    copied_plan=1
  done
  if [[ "$copied_plan" -eq 0 ]]; then
    echo "seed-product: warning: $APP_SPECIFIC/plans has no .md files" >&2
  fi
else
  echo "seed-product: warning: missing $APP_SPECIFIC/plans (legacy kit; new ANALYZE runs must author plans)" >&2
fi

ENV_APPEND="backend.env.llm"
if [[ -f "$BOOTSTRAP" ]] && grep -q '^env_append:' "$BOOTSTRAP" 2>/dev/null; then
  ENV_APPEND="$(grep '^env_append:' "$BOOTSTRAP" | head -1 | sed 's/^env_append:[[:space:]]*//' | tr -d '\r')"
fi

if [[ -f "$REPO_ROOT/backend/.env" ]] && [[ "$ENV_APPEND" != "none" ]] && [[ "$ENV_APPEND" != "false" ]]; then
  SNIPPET="$AGNOSTIC/templates/$ENV_APPEND"
  if [[ -f "$SNIPPET" ]] && ! grep -q 'LLM_API_KEY' "$REPO_ROOT/backend/.env" 2>/dev/null; then
    echo "" >> "$REPO_ROOT/backend/.env"
    cat "$SNIPPET" >> "$REPO_ROOT/backend/.env"
    echo "seed-product: appended $ENV_APPEND to backend/.env"
  fi
fi

echo "seed-product: done."
