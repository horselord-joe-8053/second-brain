#!/usr/bin/env bash
set -euo pipefail
PREP_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$PREP_DIR/../.." && pwd)"
export RETAIL_DATABASE_URL="${RETAIL_DATABASE_URL:-postgresql://retail:retail@127.0.0.1:5433/retail}"
export PYTHONPATH="$ROOT/scripts/retail${PYTHONPATH:+:$PYTHONPATH}"

# shellcheck source=cursor_gen/retail_v11_prep/lib/sim_data_profile_env.sh
source "$PREP_DIR/lib/sim_data_profile_env.sh"
retail_sim_data_profile_exports "$ROOT"
retail_sim_data_profile_banner "04_run_ab_postgres (legacy V1 vs hybrid flag)"
mkdir -p "$RETAIL_SIM_REPORTS_DIR"

RETAIL_TICKET_HYBRID_SEARCH=0 "$ROOT/scripts/py" "$ROOT/scripts/retail/eval/eval_ticket_search.py" \
  --postgres --eval "$RETAIL_SIM_EVAL" \
  --report "$RETAIL_SIM_REPORTS_DIR/pg_baseline_v1.json"

RETAIL_TICKET_HYBRID_SEARCH=1 "$ROOT/scripts/py" "$ROOT/scripts/retail/eval/eval_ticket_search.py" \
  --postgres --eval "$RETAIL_SIM_EVAL" \
  --report "$RETAIL_SIM_REPORTS_DIR/pg_ab_v1_v11.json"

echo "Compare [sim_data_profile=${RETAIL_SIM_DATA_PROFILE}]:"
echo "  $RETAIL_SIM_REPORTS_DIR/pg_baseline_v1.json"
echo "  $RETAIL_SIM_REPORTS_DIR/pg_ab_v1_v11.json"
