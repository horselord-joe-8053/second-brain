#!/usr/bin/env bash
set -euo pipefail
PREP_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$PREP_DIR/../.." && pwd)"
export RETAIL_DATABASE_URL="${RETAIL_DATABASE_URL:-postgresql://retail:retail@127.0.0.1:5433/retail}"
export PYTHONPATH="$ROOT/scripts/retail${PYTHONPATH:+:$PYTHONPATH}"

# shellcheck source=cursor_gen/retail_v11_prep/lib/sim_data_profile_env.sh
source "$PREP_DIR/lib/sim_data_profile_env.sh"
retail_sim_data_profile_exports "$ROOT"
retail_sim_data_profile_banner "05_run_abcd_postgres (V1 / V1.1 / V1.2 / V1.3)"
mkdir -p "$RETAIL_SIM_REPORTS_DIR"

run_mode() {
  local mode="$1"
  local out="$2"
  echo "[sim_data_profile=${RETAIL_SIM_DATA_PROFILE}] search_mode=${mode} -> ${out}"
  RETAIL_TICKET_SEARCH_MODE="$mode" "$ROOT/scripts/py" "$ROOT/scripts/retail/eval/eval_ticket_search.py" \
    --postgres --eval "$RETAIL_SIM_EVAL" --report "$out"
}

run_mode vector_only "$RETAIL_SIM_REPORTS_DIR/pg_baseline_v1.json"
run_mode rrf_normal "$RETAIL_SIM_REPORTS_DIR/pg_ab_v1_1_normal.json"
run_mode rrf_weighted "$RETAIL_SIM_REPORTS_DIR/pg_ab_v1_2_weighted.json"
run_mode rrf_weighted_boosted "$RETAIL_SIM_REPORTS_DIR/pg_ab_v1_3_boosted.json"

echo "A/B/C/D reports [sim_data_profile=${RETAIL_SIM_DATA_PROFILE}] under $RETAIL_SIM_REPORTS_DIR"
