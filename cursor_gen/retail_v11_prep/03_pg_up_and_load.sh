#!/usr/bin/env bash
set -euo pipefail
PREP_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$PREP_DIR/../.." && pwd)"
# shellcheck source=cursor_gen/retail_v11_prep/lib/require_external.sh
source "$PREP_DIR/lib/require_external.sh"

require_python_module psycopg2 "pip install psycopg2-binary"

cd "$ROOT/scripts/retail"
export RETAIL_DATABASE_URL="${RETAIL_DATABASE_URL:-postgresql://retail:retail@127.0.0.1:5433/retail}"

bash "$PREP_DIR/00_docker_ensure.sh"
echo "03: starting docker compose (retail_pg on 5433)..."
docker compose up -d
echo "03: waiting for postgres..."
for i in $(seq 1 30); do
  if docker compose exec -T retail_pg pg_isready -U retail -d retail >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

# shellcheck source=cursor_gen/retail_v11_prep/lib/sim_data_profile_env.sh
source "$PREP_DIR/lib/sim_data_profile_env.sh"
retail_sim_data_profile_exports "$ROOT"
retail_sim_data_profile_banner "03_pg_up_and_load (schema + profile reload)"
test -f "$RETAIL_SIM_CSV" || {
  if [[ "$RETAIL_SIM_DATA_PROFILE" == "rrf_data_prag_gen" ]]; then
    echo "Run 02_generate_corpus.sh first (prag_gen CSV missing)" >&2
  else
    echo "LLM corpus missing: $RETAIL_SIM_CSV (see tmp/simulated_data/prompt.txt)" >&2
  fi
  exit 1
}

export RETAIL_MARKET="${RETAIL_MARKET:-AU}"
echo "03: apply schema migrations (idempotent)..."
docker compose exec -T retail_pg psql -U retail -d retail -f - < "$ROOT/scripts/retail/schema/002_search_text.sql"

export PYTHONPATH="$ROOT/scripts/retail${PYTHONPATH:+:$PYTHONPATH}"
python3 "$ROOT/scripts/retail/reload_postgres_corpus.py"
echo "03: row count:"
docker compose exec -T retail_pg psql -U retail -d retail -c "SELECT status, count(*) FROM service_queries GROUP BY 1;"
