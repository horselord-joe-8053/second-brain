#!/usr/bin/env bash
# Copy core/harness into repo. Optional 4th arg: profile general|webapp (webapp = also apply webapp module).

set -euo pipefail

REPO_ROOT="${1:-.}"
PROJECT_NAME="${2:-Project}"
PROJECT_DESC="${3:-A software or systems project.}"
PROFILE="${4:-general}"

REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
CORE="$(cd "$(dirname "$0")/.." && pwd)"
HARNESS="$CORE/harness"
KIT="$(cd "$CORE/.." && pwd)"

if [[ ! -d "$HARNESS" ]]; then
  echo "seed-harness: missing $HARNESS" >&2
  exit 1
fi

echo "== seed-harness: repo=$REPO_ROOT profile=$PROFILE =="

for f in AGENTS.md GLOSSARY.md; do
  sed -e "s/{{PROJECT_NAME}}/$PROJECT_NAME/g" -e "s/{{APP_NAME}}/$PROJECT_NAME/g" \
      -e "s/{{PROJECT_DESCRIPTION}}/$PROJECT_DESC/g" -e "s/{{APP_DESCRIPTION}}/$PROJECT_DESC/g" \
    "$HARNESS/$f" > "$REPO_ROOT/$f"
done

mkdir -p "$REPO_ROOT/docs/specs" "$REPO_ROOT/docs/templates" "$REPO_ROOT/docs/plans"
for f in PROJECT-TDD.md PRODUCT.md ARCHITECTURE.md SECURITY.md; do
  sed -e "s/{{PROJECT_NAME}}/$PROJECT_NAME/g" -e "s/{{APP_NAME}}/$PROJECT_NAME/g" \
    "$HARNESS/docs/$f" > "$REPO_ROOT/docs/$f"
done
cp "$HARNESS/docs/templates/"*.md "$REPO_ROOT/docs/templates/"

mkdir -p "$REPO_ROOT/.agents/skills"
for skill in specify-feature align-requirements implement-feature debug; do
  mkdir -p "$REPO_ROOT/.agents/skills/$skill"
  cp "$HARNESS/dot-agents-skills/$skill/SKILL.md" "$REPO_ROOT/.agents/skills/$skill/"
done

if [[ -d "$HARNESS/cursor/rules" ]]; then
  mkdir -p "$REPO_ROOT/.cursor/rules"
  cp "$HARNESS/cursor/rules/"*.mdc "$REPO_ROOT/.cursor/rules/"
fi

if [[ "$PROFILE" == "webapp" ]]; then
  bash "$CORE/scripts/apply-module.sh" "$REPO_ROOT" webapp
fi

echo "seed-harness: done."
