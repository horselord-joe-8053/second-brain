#!/usr/bin/env bash
# Start backend + frontend for manual UI testing. Merge gate: ./scripts/verify.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Repo root on PYTHONPATH so backend code can import utils.neat_logger.
export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"
BACKEND_PORT="${APP_BACKEND_PORT:-8900}"
FRONTEND_PORT="${APP_FRONTEND_PORT:-5973}"
BACKEND_HOST="127.0.0.1"

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  local code=$?
  if [[ -n "$BACKEND_PID" ]]; then kill "$BACKEND_PID" 2>/dev/null || true; fi
  if [[ -n "$FRONTEND_PID" ]]; then kill "$FRONTEND_PID" 2>/dev/null || true; fi
  wait 2>/dev/null || true
  exit "$code"
}

trap cleanup EXIT INT TERM

require_free_port() {
  local port=$1 name=$2
  if lsof -iTCP:"$port" -sTCP:LISTEN -P -n >/dev/null 2>&1; then
    echo "dev.sh: port $port in use ($name). Stop it or set APP_${name}_PORT." >&2
    exit 1
  fi
}

echo "== dev (API :$BACKEND_PORT, UI :$FRONTEND_PORT) =="
require_free_port "$BACKEND_PORT" "BACKEND"

cd "$ROOT/backend"
if [[ ! -d .venv ]]; then python3 -m venv .venv; fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -e ".[dev]"
[[ -f .env ]] || echo "dev.sh: warning: backend/.env missing (see README)" >&2

require_free_port "$FRONTEND_PORT" "FRONTEND"
cd "$ROOT/frontend"
[[ -d node_modules ]] || npm ci
[[ -f .env ]] || echo "dev.sh: warning: frontend/.env missing" >&2

cd "$ROOT/backend"
# shellcheck source=/dev/null
source .venv/bin/activate
uvicorn app.main:app --reload --host "$BACKEND_HOST" --port "$BACKEND_PORT" &
BACKEND_PID=$!

cd "$ROOT/frontend"
npm run dev -- --port "$FRONTEND_PORT" --strictPort &
FRONTEND_PID=$!

echo ""
echo "  API:  http://${BACKEND_HOST}:${BACKEND_PORT}/health"
echo "  UI:   http://localhost:${FRONTEND_PORT}/"
echo "  Ctrl+C stops both."
echo ""
wait "$BACKEND_PID" "$FRONTEND_PID"
