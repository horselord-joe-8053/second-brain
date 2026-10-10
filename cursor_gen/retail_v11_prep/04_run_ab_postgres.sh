#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export RETAIL_DATABASE_URL="${RETAIL_DATABASE_URL:-postgresql://retail:retail@127.0.0.1:5433/retail}"
export PYTHONPATH="$ROOT/scripts/retail${PYTHONPATH:+:$PYTHONPATH}"
EVAL="$ROOT/scripts/retail/eval/ticket_retrieval.jsonl"
mkdir -p "$ROOT/scripts/retail/eval/reports"

RETAIL_TICKET_HYBRID_SEARCH=0 python3 "$ROOT/scripts/retail/eval/eval_ticket_search.py" \
  --postgres --eval "$EVAL" \
  --report "$ROOT/scripts/retail/eval/reports/pg_baseline_v1.json"

RETAIL_TICKET_HYBRID_SEARCH=1 python3 "$ROOT/scripts/retail/eval/eval_ticket_search.py" \
  --postgres --eval "$EVAL" \
  --report "$ROOT/scripts/retail/eval/reports/pg_ab_v1_v11.json"

echo "Compare:"
echo "  $ROOT/scripts/retail/eval/reports/pg_baseline_v1.json"
echo "  $ROOT/scripts/retail/eval/reports/pg_ab_v1_v11.json"
