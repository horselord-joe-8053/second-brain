#!/usr/bin/env bash
# Run retail answer tests in leg order: ticket → manual → bundle+E2E. See RETAIL_ANSWER_LEGS.md.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
PY="$ROOT/scripts/py"
cd "$ROOT"
echo "=== retail_ticket_leg ==="
"$PY" -m pytest tests/test_retail_answer_tickets.py -q
echo "=== retail_manual_leg ==="
"$PY" -m pytest tests/test_retail_answer_manuals.py -q
echo "=== retail_answer_integration ==="
"$PY" -m pytest tests/test_retail_answer_bundle.py tests/test_retail_answer_e2e.py -q
echo "run_answer_ci_legs: OK"
