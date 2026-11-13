#!/usr/bin/env bash
# Start ParadeDB only; stop OpenSearch sidecar first (low-RAM hosts).
set -euo pipefail
PREP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="$(cd "$PREP_DIR/../.." && pwd)"
# shellcheck source=cursor_gen/retail_v11_prep/lib/require_external.sh
source "$PREP_DIR/lib/require_external.sh"
require_cmd docker "Install Docker Desktop and re-run."

# Stop OpenSearch only — do not recycle Parade while applying schema (avoids connect races).
if docker ps -a --format '{{.Names}}' | grep -qx retail_lexical_opensearch; then
  docker stop retail_lexical_opensearch >/dev/null 2>&1 || true
  docker rm retail_lexical_opensearch >/dev/null 2>&1 || true
fi

IMAGE="${RETAIL_PARADE_DOCKER_IMAGE:-paradedb/paradedb:latest}"
PORT="${RETAIL_PARADE_PORT:-5434}"
NAME=retail_lexical_parade
PASS="${RETAIL_PARADE_PG_PASSWORD:-retail}"

if docker ps --format '{{.Names}}' | grep -qx "$NAME"; then
  echo "lexical_docker: ${NAME} already running."
else
  echo "lexical_docker: starting ${NAME} (${IMAGE}) on port ${PORT}..."
  docker run -d --name "$NAME" \
    -e POSTGRES_PASSWORD="$PASS" \
    -p "${PORT}:5432" \
    "$IMAGE"
fi

echo "lexical_docker: waiting for ParadeDB postgres..."
for _ in $(seq 1 60); do
  if docker exec "$NAME" pg_isready -U postgres >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

export RETAIL_PARADEDB_URL="${RETAIL_PARADEDB_URL:-postgresql://postgres:${PASS}@127.0.0.1:${PORT}/postgres}"
echo "lexical_docker: applying schema 003_lexical_parade_tickets.sql..."
if ! docker exec -i "$NAME" psql -U postgres -d postgres -v ON_ERROR_STOP=1 \
  < "$ROOT/scripts/retail/schema/003_lexical_parade_tickets.sql"; then
  echo "lexical_docker: schema apply failed — check ParadeDB image supports pg_search + bm25." >&2
  exit 1
fi

for _ in $(seq 1 30); do
  if docker exec "$NAME" pg_isready -U postgres >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo "export RETAIL_PARADEDB_URL=\"${RETAIL_PARADEDB_URL}\""
echo "lexical_docker: ParadeDB ready at ${RETAIL_PARADEDB_URL}"
