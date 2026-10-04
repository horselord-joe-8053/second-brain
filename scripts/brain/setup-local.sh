#!/usr/bin/env bash
# Idempotent Topology A setup driver (Mac): Hermes CLI, corpus checks, pointers for LLM Wiki GUI gates.
# Extend here as automation grows; GUI-only LLM Wiki steps remain human until upstream supports config merge.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "== second-brain setup-local (idempotent) =="

bash "$ROOT/scripts/brain/setup-hermes.sh"

echo "== second-brain: corpus layout =="
test -d "$ROOT/brain/raw/sources"
test -d "$ROOT/brain/wiki"
test -d "$ROOT/brain/manifests"
test -f "$ROOT/brain/purpose.md"
test -f "$ROOT/harness/second-brain/README.md"

echo ""
echo "Next (human gates — not automated here):"
echo "  • LLM Wiki: open project at ${ROOT}/brain — runbook docs_manual_gen/SECOND_BRAIN_RUNBOOK.md §5–§8"
echo "  • Hermes P4: docs/harness/hermes-mcp.example.yaml → ~/.hermes/config.yaml"
echo "  • Verify: ./scripts/verify-local.sh && ./scripts/verify.sh"
echo ""
echo "setup-local.sh: done"
