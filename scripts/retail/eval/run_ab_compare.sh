#!/usr/bin/env bash
# A/B ticket search: V1 vector vs V1.1 hybrid (same CSV fixture).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
TICKETS="${1:-$ROOT/scripts/retail/seed/generated/service_queries.csv}"
EVAL="${2:-$ROOT/scripts/retail/eval/ticket_retrieval.jsonl}"
mkdir -p scripts/retail/eval/reports
export PYTHONPATH="$ROOT/scripts/retail${PYTHONPATH:+:$PYTHONPATH}"
RETAIL_TICKET_HYBRID_SEARCH=0 python3 scripts/retail/eval/eval_ticket_search.py \
  --tickets "$TICKETS" --eval "$EVAL" --report scripts/retail/eval/reports/baseline_v1.json
RETAIL_TICKET_HYBRID_SEARCH=1 python3 scripts/retail/eval/eval_ticket_search.py \
  --tickets "$TICKETS" --eval "$EVAL" --report scripts/retail/eval/reports/ab_v1_v11.json
echo "reports: scripts/retail/eval/reports/baseline_v1.json and ab_v1_v11.json"
