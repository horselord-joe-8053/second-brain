#!/usr/bin/env bash
# P3 preflight: confirm Hermes CLI is on PATH and run `hermes doctor`.
# Does not install Hermes; see docs_manual_gen/SECOND_BRAIN_RUNBOOK.md §10.
set -euo pipefail

if ! command -v hermes >/dev/null 2>&1; then
  echo "hermes: not found on PATH"
  echo "Install: curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash"
  echo "Then reload shell and re-run: ./scripts/brain/hermes-preflight.sh"
  exit 1
fi

echo "hermes: $(command -v hermes)"
hermes --version 2>/dev/null || true
echo "--- hermes doctor ---"
hermes doctor
