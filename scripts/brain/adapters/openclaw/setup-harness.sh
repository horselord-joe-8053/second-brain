#!/usr/bin/env bash
# OpenClaw adapter skeleton (invoked from setup-local.sh when active_harness=openclaw).
set -euo pipefail

OPENCLAW_AD="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$OPENCLAW_AD/../../../.." && pwd)"

if [[ -x "$OPENCLAW_AD/merge-openclaw-wiring.py" ]]; then
  python3 "$OPENCLAW_AD/merge-openclaw-wiring.py"
fi

echo "setup-harness (openclaw): skeleton only — see docs_manual_gen/RUNBOOK_HARNESS_OPENCLAW.md"
