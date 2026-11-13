#!/usr/bin/env bash
# Hermes adapter: install, messaging, MCP wire (invoked from setup-local.sh).
set -euo pipefail

HERMES_AD="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERMES_AD/../../../.." && pwd)"

bash "$HERMES_AD/setup-hermes.sh"
bash "$HERMES_AD/setup-hermes-messaging.sh" || echo "setup-harness (hermes): messaging skipped or partial"

if [[ -f "${HOME}/Library/Application Support/com.llmwiki.app/app-state.json" ]]; then
  bash "$HERMES_AD/setup-hermes-mcp.sh" || {
    echo "setup-harness (hermes): MCP wiring skipped or failed (LLM Wiki app must be running for mcp test)"
  }
else
  echo "setup-harness (hermes): skip MCP auto-wire (no LLM Wiki app-state yet)"
fi

echo "setup-harness (hermes): OK — see docs_manual_gen/RUNBOOK_HARNESS_HERMES.md"
