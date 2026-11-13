#!/usr/bin/env bash
# Stop ParadeDB and OpenSearch sidecars so only one RAM-heavy lexical container runs at a time.
set -euo pipefail

stop_one() {
  local name="$1"
  if docker ps -a --format '{{.Names}}' | grep -qx "$name"; then
    echo "lexical_docker: stopping ${name}..."
    docker stop "$name" >/dev/null 2>&1 || true
    docker rm "$name" >/dev/null 2>&1 || true
  fi
}

stop_one retail_lexical_parade
stop_one retail_lexical_opensearch
echo "lexical_docker: sidecars stopped (retail_pg on 5433 is untouched)."
