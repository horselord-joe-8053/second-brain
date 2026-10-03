#!/usr/bin/env bash
# Install Matt Pocock + ui-ux-pro-max skills into the target repo (.agents/skills/).
# Global install: ui-ux-pro-max-cli only (uipro). Human pre-approves via bootstrap_webapp_factory.md §2.

set -euo pipefail

REPO_ROOT="${1:-.}"
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"

echo "== install-agent-skills: repo=$REPO_ROOT =="

if ! command -v npm >/dev/null 2>&1; then
  echo "install-agent-skills: npm not found; ask the human to install Node.js." >&2
  exit 1
fi

if ! command -v uipro >/dev/null 2>&1; then
  echo "install-agent-skills: installing ui-ux-pro-max-cli globally (bootstrap pre-approved)..."
  npm install -g ui-ux-pro-max-cli
fi

cd "$REPO_ROOT"
echo "install-agent-skills: ui-ux-pro-max (universal → .agents/skills/)..."
uipro init --ai universal

echo "install-agent-skills: mattpocock/skills..."
npx skills add mattpocock/skills

echo "install-agent-skills: done. Restart Cursor or reload skills if slash menu is stale."
