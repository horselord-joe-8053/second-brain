#!/usr/bin/env bash
# Start OpenSearch only; stop ParadeDB sidecar first (low-RAM hosts).
set -euo pipefail
PREP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=cursor_gen/retail_v11_prep/lib/require_external.sh
source "$PREP_DIR/lib/require_external.sh"
require_cmd docker "Install Docker Desktop and re-run."

if docker ps -a --format '{{.Names}}' | grep -qx retail_lexical_parade; then
  docker stop retail_lexical_parade >/dev/null 2>&1 || true
  docker rm retail_lexical_parade >/dev/null 2>&1 || true
fi

IMAGE="${RETAIL_OPENSEARCH_DOCKER_IMAGE:-opensearchproject/opensearch:2}"
PORT="${RETAIL_OPENSEARCH_PORT:-9200}"
NAME=retail_lexical_opensearch

if docker ps --format '{{.Names}}' | grep -qx "$NAME"; then
  echo "lexical_docker: ${NAME} already running."
else
  echo "lexical_docker: starting ${NAME} (${IMAGE}) on port ${PORT}..."
  docker run -d --name "$NAME" \
    -p "${PORT}:9200" \
    -e discovery.type=single-node \
    -e DISABLE_SECURITY_PLUGIN=true \
    -e OPENSEARCH_JAVA_OPTS="${RETAIL_OPENSEARCH_JAVA_OPTS:--Xms512m -Xmx512m}" \
    "$IMAGE"
fi

echo "lexical_docker: waiting for OpenSearch HTTP..."
for _ in $(seq 1 90); do
  if curl -sf "http://127.0.0.1:${PORT}/" >/dev/null 2>&1; then
    echo "export RETAIL_OPENSEARCH_URL=\"http://127.0.0.1:${PORT}\""
    echo "lexical_docker: OpenSearch ready at http://127.0.0.1:${PORT}"
    exit 0
  fi
  sleep 2
done

echo "STOP: OpenSearch did not become ready on port ${PORT} within timeout." >&2
exit 1
