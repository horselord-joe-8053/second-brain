#!/usr/bin/env bash
# Idempotent Topology A setup: shared stack + active harness adapter (Hermes, OpenClaw, …).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "== second-brain setup-local (idempotent) =="

bash "$ROOT/scripts/brain/apply-stack-config.sh" || echo "setup-local: apply-stack-config skipped or partial"

HARNESS="$(python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('$ROOT') / 'scripts' / 'brain'))
from brain_stack import active_harness, load_brain_stack
print(active_harness(load_brain_stack(Path('$ROOT'))))
")"
ADAPTER="$ROOT/scripts/brain/adapters/$HARNESS/setup-harness.sh"
if [[ -f "$ADAPTER" ]]; then
  bash "$ADAPTER"
else
  echo "setup-local: no adapter at scripts/brain/adapters/$HARNESS/setup-harness.sh — skip harness steps"
fi

echo "== second-brain: corpus layout =="
test -d "$ROOT/brain/raw/sources"
test -d "$ROOT/brain/wiki"
test -d "$ROOT/brain/manifests"
test -f "$ROOT/brain/purpose.md"
test -f "$ROOT/harness/second-brain/README.md"

bash "$ROOT/scripts/brain/setup-obsidian.sh"

if [[ "${RUN_BRAIN_ACCEPTANCE:-0}" == "1" && "$HARNESS" == "hermes" && -f "$ROOT/scripts/brain/adapters/hermes/acceptance-automated.sh" ]]; then
  bash "$ROOT/scripts/brain/adapters/hermes/acceptance-automated.sh"
fi

echo ""
echo "After reboot (order): LLM Wiki app → Obsidian vault → this script."
echo "Next (human gates):"
echo "  • Hub runbook: docs_manual_gen/SECOND_BRAIN_RUNBOOK.md"
case "$HARNESS" in
  hermes) echo "  • Hermes runbook: docs_manual_gen/RUNBOOK_HARNESS_HERMES.md" ;;
  openclaw) echo "  • OpenClaw runbook: docs_manual_gen/RUNBOOK_HARNESS_OPENCLAW.md" ;;
  *) echo "  • Harness adapter: scripts/brain/adapters/$HARNESS/" ;;
esac
echo "  • P8 automated: RUN_BRAIN_ACCEPTANCE=1 ./scripts/brain/setup-local.sh (Hermes only today)"
echo "  • Verify: ./scripts/verify-local.sh && ./scripts/verify.sh"
echo ""
echo "setup-local.sh: done"
