#!/usr/bin/env bash
# Stop retail Postgres container only (idempotent). Optional: quit Docker Desktop.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/scripts/retail"

if docker info >/dev/null 2>&1; then
  docker compose down --remove-orphans
  echo "05_teardown: retail_pg compose stopped."
else
  echo "05_teardown: Docker daemon not running — nothing to stop."
fi

if [[ "${QUIT_DOCKER_DESKTOP:-0}" == "1" ]] && [[ "$(uname -s)" == "Darwin" ]]; then
  osascript -e 'quit app "Docker"' 2>/dev/null || true
  echo "05_teardown: requested Docker Desktop quit."
fi
