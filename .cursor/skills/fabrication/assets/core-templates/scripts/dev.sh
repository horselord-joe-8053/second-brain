#!/usr/bin/env bash
# Optional dev helper. Web stacks: extend with backend/frontend servers per modules/webapp/MODULE.md.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "dev.sh: general kit — no default server. Run ./scripts/verify.sh or project-specific commands."
echo "Docs: docs/PRODUCT.md, docs/plans/, AGENTS.md"
