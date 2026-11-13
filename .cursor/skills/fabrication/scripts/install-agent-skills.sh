#!/usr/bin/env bash
# Optional: npm global skills installer (same as legacy kits).
set -euo pipefail
REPO_ROOT="${1:-.}"
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
echo "install-agent-skills: project skills live in $REPO_ROOT/.agents/skills (seed-harness)."
if command -v npx >/dev/null 2>&1; then
  echo "install-agent-skills: run project-specific npm skill installs when a spec requires them."
fi
