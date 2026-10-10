#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
# Phases: COUNT=50 (implement/wire), COUNT=90 (pre-A/B superset, same SEED keeps first 50 stable).
COUNT="${COUNT:-50}"
SEED="${SEED:-42}"
export RETAIL_MARKET="${RETAIL_MARKET:-AU}"
export PYTHONPATH="$ROOT/scripts/retail${PYTHONPATH:+:$PYTHONPATH}"
python3 "$ROOT/scripts/retail/seed/generate_tickets.py" \
  --count "$COUNT" --seed "$SEED" \
  --out-dir "$ROOT/scripts/retail/seed/generated"
python3 "$ROOT/scripts/retail/seed/generate_eval_from_manifest.py" \
  --manifest "$ROOT/scripts/retail/seed/generated/ticket_manifest.jsonl" \
  --out "$ROOT/scripts/retail/eval/ticket_retrieval.jsonl" \
  --max-rows "${EVAL_MAX:-200}"
echo "02_generate_corpus: $COUNT tickets, eval cap ${EVAL_MAX:-200}"
