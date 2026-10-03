#!/usr/bin/env bash
# General-project dev helper (optional). Web stacks: use bootstrap_webapp dev.sh instead.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "dev.sh: general kit — no default server. Run ./scripts/verify.sh or project-specific commands."
echo "Docs: docs/PRODUCT.md, docs/plans/, AGENTS.md"
