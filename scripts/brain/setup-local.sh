#!/usr/bin/env bash
# Idempotent Topology A setup driver (Mac): Hermes CLI, corpus checks, pointers for LLM Wiki GUI gates.
# Extend here as automation grows; GUI-only LLM Wiki steps remain human until upstream supports config merge.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "== second-brain setup-local (idempotent) =="

bash "$ROOT/scripts/brain/setup-hermes.sh"

if [[ -f "${HOME}/Library/Application Support/com.llmwiki.app/app-state.json" ]]; then
  bash "$ROOT/scripts/brain/setup-hermes-mcp.sh" || {
    echo "setup-local: MCP wiring skipped or failed (LLM Wiki app must be running for mcp test)"
  }
else
  echo "setup-local: skip MCP auto-wire (no LLM Wiki app-state yet)"
fi

echo "== second-brain: corpus layout =="
test -d "$ROOT/brain/raw/sources"
test -d "$ROOT/brain/wiki"
test -d "$ROOT/brain/manifests"
test -f "$ROOT/brain/purpose.md"
test -f "$ROOT/harness/second-brain/README.md"

bash "$ROOT/scripts/brain/setup-obsidian.sh"

if [[ "${RUN_BRAIN_ACCEPTANCE:-0}" == "1" ]]; then
  bash "$ROOT/scripts/brain/acceptance-automated.sh"
fi

echo ""
echo "After reboot (order): LLM Wiki app → Obsidian vault → this script."
echo "Next (human gates — may remain):"
echo "  • LLM Wiki: open project at ${ROOT}/brain — runbook docs_manual_gen/SECOND_BRAIN_RUNBOOK.md §5–§8"
echo "  • Obsidian: OPEN_OBSIDIAN_VAULT=1 ./scripts/brain/setup-obsidian.sh (or Open folder → ${ROOT}/brain/wiki)"
echo "  • P8 automated: RUN_BRAIN_ACCEPTANCE=1 ./scripts/brain/setup-local.sh  (or ./scripts/brain/acceptance-automated.sh)"
echo "  • P8 manual: Hermes chat MCP smoke (runbook §10.1) + NB-SB1 — docs/ACCEPTANCE-second-brain-hermes-v1.md"
echo "  • Verify: ./scripts/verify-local.sh && ./scripts/verify.sh"
echo ""
echo "setup-local.sh: done"
