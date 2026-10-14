#!/usr/bin/env bash
# Four lexical backends × A/B/C (V1…V1.2) on rrf_data_llm_gen. One PG embed load; rebuild keyword index per backend.
set -euo pipefail
PREP_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$PREP_DIR/../.." && pwd)"
LEX_DOCKER="$PREP_DIR/lexical_docker"

# shellcheck source=cursor_gen/retail_v11_prep/lib/require_external.sh
source "$PREP_DIR/lib/require_external.sh"
require_python_module psycopg2 "pip install psycopg2-binary"

export RETAIL_DATABASE_URL="${RETAIL_DATABASE_URL:-postgresql://retail:retail@127.0.0.1:5433/retail}"
export RETAIL_SIM_DATA_PROFILE="${RETAIL_SIM_DATA_PROFILE:-rrf_data_llm_gen}"
export PYTHONPATH="$ROOT:$ROOT/scripts/retail${PYTHONPATH:+:$PYTHONPATH}"

# shellcheck source=cursor_gen/retail_v11_prep/lib/sim_data_profile_env.sh
source "$PREP_DIR/lib/sim_data_profile_env.sh"
retail_sim_data_profile_exports "$ROOT"

if [[ "$RETAIL_SIM_DATA_PROFILE" != "rrf_data_llm_gen" ]]; then
  echo "06_lexical_matrix: set RETAIL_SIM_DATA_PROFILE=rrf_data_llm_gen (this matrix is llm_gen only)." >&2
  exit 1
fi

MATRIX_ROOT="${RETAIL_LEXICAL_MATRIX_REPORTS:-$RETAIL_SIM_REPORTS_DIR/lexical_matrix}"
SUMMARY="${MATRIX_ROOT}/lexical_matrix_summary.md"
mkdir -p "$MATRIX_ROOT"

run_abcd_for_backend() {
  local backend="$1"
  local out_dir="${MATRIX_ROOT}/${backend}"
  mkdir -p "$out_dir"
  echo ""
  echo "=== lexical_matrix backend=${backend} reports -> ${out_dir} ==="

  run_mode() {
    local mode="$1"
    local out="$2"
    echo "[backend=${backend}] search_mode=${mode} -> ${out}"
    RETAIL_TICKET_SEARCH_MODE="$mode" RETAIL_LEXICAL_BACKEND="$backend" \
      "$ROOT/scripts/py" "$ROOT/scripts/retail/eval/eval_ticket_search.py" \
      --postgres --eval "$RETAIL_SIM_EVAL" --report "$out"
  }

  run_mode vector_only "$out_dir/pg_baseline_v1.json"
  run_mode rrf_normal "$out_dir/pg_ab_v1_1_normal.json"
  run_mode rrf_term_boosted "$out_dir/pg_ab_v1_2_term_boosted.json"
}

prepare_backend_env() {
  local backend="$1"
  export RETAIL_LEXICAL_BACKEND="$backend"
  case "$backend" in
    tantivy | bm25x)
      bash "$LEX_DOCKER/stop_sidecars.sh"
      unset RETAIL_PARADEDB_URL RETAIL_OPENSEARCH_URL || true
      ;;
    parade_db)
      bash "$LEX_DOCKER/parade_up.sh"
      export RETAIL_PARADEDB_URL="${RETAIL_PARADEDB_URL:-postgresql://postgres:retail@127.0.0.1:5434/postgres}"
      ;;
    open_search)
      bash "$LEX_DOCKER/opensearch_up.sh"
      export RETAIL_OPENSEARCH_URL="${RETAIL_OPENSEARCH_URL:-http://127.0.0.1:9200}"
      ;;
    *)
      echo "unknown backend: $backend" >&2
      exit 1
      ;;
  esac
}

if [[ "${RETAIL_LEXICAL_MATRIX_SKIP_PG_LOAD:-0}" != "1" ]]; then
  echo "06_lexical_matrix: full Postgres load + embed (set RETAIL_LEXICAL_MATRIX_SKIP_PG_LOAD=1 to reuse PG)..."
  bash "$PREP_DIR/03_pg_up_and_load.sh"
else
  echo "06_lexical_matrix: skipping 03 (RETAIL_LEXICAL_MATRIX_SKIP_PG_LOAD=1); ensure PG is loaded."
  bash "$PREP_DIR/00_docker_ensure.sh"
  cd "$ROOT/scripts/retail"
  docker compose up -d
fi

{
  echo "# Lexical backend × A/B/C matrix (rrf_data_llm_gen)"
  echo ""
  echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo ""
  echo "| Backend | Reports dir |"
  echo "|---------|-------------|"
} >"$SUMMARY"

if [[ -n "${RETAIL_LEXICAL_MATRIX_ONLY:-}" ]]; then
  IFS=',' read -r -a BACKENDS <<< "${RETAIL_LEXICAL_MATRIX_ONLY}"
else
  BACKENDS=(tantivy bm25x parade_db open_search)
fi
for backend in "${BACKENDS[@]}"; do
  prepare_backend_env "$backend"
  echo "06_lexical_matrix: rebuild lexical index (backend=${backend})..."
  RETAIL_LEXICAL_BACKEND="$backend" "$ROOT/scripts/py" "$ROOT/scripts/retail/rebuild_lexical_index.py"
  run_abcd_for_backend "$backend"
  echo "| \`${backend}\` | \`${MATRIX_ROOT}/${backend}/\` |" >>"$SUMMARY"
done

bash "$LEX_DOCKER/stop_sidecars.sh"

echo ""
echo "06_lexical_matrix: done. Summary: ${SUMMARY}"
echo "Append highlights to scripts/retail/eval/reports/phase6_operator_log.md and ABOUT §13 as needed."
