#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export RETAIL_DATABASE_URL="${RETAIL_DATABASE_URL:-postgresql://retail:retail@127.0.0.1:5433/retail}"
export PYTHONPATH="$ROOT/scripts/retail${PYTHONPATH:+:$PYTHONPATH}"
EVAL="$ROOT/scripts/retail/eval/ticket_retrieval.jsonl"
REPORTS="$ROOT/scripts/retail/eval/reports"
mkdir -p "$REPORTS"

run_mode() {
  local mode="$1"
  local out="$2"
  RETAIL_TICKET_SEARCH_MODE="$mode" python3 "$ROOT/scripts/retail/eval/eval_ticket_search.py" \
    --postgres --eval "$EVAL" --report "$out"
}

run_mode vector_only "$REPORTS/pg_baseline_v1.json"
run_mode rrf_normal "$REPORTS/pg_ab_v1_1_normal.json"
run_mode rrf_weighted "$REPORTS/pg_ab_v1_2_weighted.json"
run_mode rrf_weighted_boosted "$REPORTS/pg_ab_v1_3_boosted.json"

echo "A/B/C/D reports under $REPORTS"
