#!/usr/bin/env bash
# Start retail_pg (5433), apply schema, TRUNCATE+load RETAIL_SIM_DATA_PROFILE CSV, embed, rebuild lexical.
# Canonical ops entry — cursor_gen/retail_v11_prep/03_pg_up_and_load.sh delegates here.
set -euo pipefail
OPS_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$OPS_DIR/../../.." && pwd)"
# shellcheck source=scripts/retail/ops/lib/require_external.sh
source "$OPS_DIR/lib/require_external.sh"
# shellcheck source=scripts/retail/ops/lib/load_repo_env.sh
source "$OPS_DIR/lib/load_repo_env.sh"
load_repo_env "$ROOT"

require_python_module psycopg2 "pip install psycopg2-binary"

cd "$ROOT/scripts/retail"
if [[ -z "${RETAIL_DATABASE_URL:-}" ]]; then
  echo "pg_up_and_load: set RETAIL_DATABASE_URL in repo .env (see .env.example)" >&2
  exit 1
fi

bash "$OPS_DIR/docker_ensure.sh"
echo "pg_up_and_load: starting docker compose (retail_pg on 5433)..."
docker compose up -d
echo "pg_up_and_load: waiting for postgres..."
for _ in $(seq 1 30); do
  if docker compose exec -T retail_pg pg_isready -U retail -d retail >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

# shellcheck source=scripts/retail/ops/lib/sim_data_profile_env.sh
source "$OPS_DIR/lib/sim_data_profile_env.sh"
retail_sim_data_profile_exports "$ROOT"
retail_sim_data_profile_banner "pg_up_and_load (schema + profile reload)"
test -f "$RETAIL_SIM_CSV" || {
  echo "Corpus CSV missing: $RETAIL_SIM_CSV (check RETAIL_SIM_DATA_PROFILE in .env)" >&2
  exit 1
}

export RETAIL_MARKET="${RETAIL_MARKET:-US}"
export RETAIL_FAULT_CODE_PREFIX="${RETAIL_FAULT_CODE_PREFIX:-FRU-E}"
echo "pg_up_and_load: apply schema migrations (idempotent)..."
docker compose exec -T retail_pg psql -U retail -d retail -f - < "$ROOT/scripts/retail/schema/002_search_text.sql"
docker compose exec -T retail_pg psql -U retail -d retail -f - < "$ROOT/scripts/retail/schema/004_customer_id.sql"
docker compose exec -T retail_pg psql -U retail -d retail -f - < "$ROOT/scripts/retail/schema/005_manual_chunks.sql"

export PYTHONPATH="$ROOT:$ROOT/scripts/retail${PYTHONPATH:+:$PYTHONPATH}"
"$ROOT/scripts/py" "$ROOT/scripts/retail/reload_postgres_corpus.py"
echo "pg_up_and_load: row count:"
docker compose exec -T retail_pg psql -U retail -d retail -c "SELECT status, count(*) FROM service_queries GROUP BY 1;"
