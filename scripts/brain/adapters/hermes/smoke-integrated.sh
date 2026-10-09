#!/usr/bin/env bash
# Automated preflight + copy-paste prompts for Hermes Desktop integrated smoke.
set -euo pipefail

HERMES_AD="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERMES_AD/../../../.." && pwd)"
# shellcheck source=scripts/brain/adapters/hermes/hermes-env.sh
source "$HERMES_AD/hermes-env.sh"

BRAIN="$(python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('$ROOT') / 'scripts' / 'brain'))
from brain_stack import load_brain_stack
print(load_brain_stack(Path('$ROOT'))['paths']['brain_root'])
")"

echo "== smoke-integrated: automated preflight =="
bash "$HERMES_AD/acceptance-automated.sh"

cat <<EOF

== smoke-integrated: Hermes Desktop (manual) ==

Preflight: LLM Wiki on ${BRAIN}; Hermes Desktop Gateway ready; MCP llm_wiki + second_brain_fs.

See RUNBOOK_HARNESS_HERMES.md §4 for copy-paste prompts.

EOF
