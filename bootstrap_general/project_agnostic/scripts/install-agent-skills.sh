#!/usr/bin/env bash
# Install Matt Pocock skills into .agents/skills/ (no ui-ux-pro-max — webapp-only).

set -euo pipefail

REPO_ROOT="${1:-.}"
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"

echo "== install-agent-skills (general): repo=$REPO_ROOT =="

if ! command -v npm >/dev/null 2>&1; then
  echo "install-agent-skills: npm not found; skip npx skills (harness skills already seeded)." >&2
  exit 0
fi

cd "$REPO_ROOT"
echo "install-agent-skills: mattpocock/skills (optional extras)..."
npx skills add mattpocock/skills || echo "install-agent-skills: npx skills add failed; continue with harness skills only."

echo "install-agent-skills: done."
