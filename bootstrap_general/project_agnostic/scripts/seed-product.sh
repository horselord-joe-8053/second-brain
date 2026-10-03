#!/usr/bin/env bash
# Phase 2: copy project_specific/specs and plans into docs/.

set -euo pipefail

REPO_ROOT="${1:-.}"
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
AGNOSTIC="$(cd "$(dirname "$0")/.." && pwd)"
KIT="$(cd "$AGNOSTIC/.." && pwd)"
PROJECT_SPECIFIC="$KIT/project_specific"
BOOTSTRAP="$PROJECT_SPECIFIC/bootstrap.md"

if [[ ! -d "$PROJECT_SPECIFIC/specs" ]]; then
  echo "seed-product: missing $PROJECT_SPECIFIC/specs" >&2
  exit 1
fi

echo "== seed-product: repo=$REPO_ROOT =="

mkdir -p "$REPO_ROOT/docs/specs" "$REPO_ROOT/docs/plans"
for f in "$PROJECT_SPECIFIC/specs/"*.md; do
  [[ -f "$f" ]] || continue
  cp "$f" "$REPO_ROOT/docs/specs/"
  echo "seed-product: wrote docs/specs/$(basename "$f")"
done

if [[ -d "$PROJECT_SPECIFIC/plans" ]]; then
  copied_plan=0
  for f in "$PROJECT_SPECIFIC/plans/"*.md; do
    [[ -f "$f" ]] || continue
    cp "$f" "$REPO_ROOT/docs/plans/"
    echo "seed-product: wrote docs/plans/$(basename "$f")"
    copied_plan=1
  done
  if [[ "$copied_plan" -eq 0 ]]; then
    echo "seed-product: warning: $PROJECT_SPECIFIC/plans has no .md files" >&2
  fi
else
  echo "seed-product: warning: missing $PROJECT_SPECIFIC/plans" >&2
fi

echo "seed-product: done."
