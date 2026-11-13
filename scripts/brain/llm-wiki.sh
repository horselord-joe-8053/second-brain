#!/usr/bin/env bash
# Start, stop, or restart the local LLM Wiki desktop app.
#
# Settings stay in ~/Library/Application Support/com.llmwiki.app/app-state.json
# (the file the UI writes). This script never deletes that file and never
# generates a new API token. It copies the saved token into second_brain/.env
# and ~/.hermes/.env so Hermes matches the UI.
#
# The process launcher is the sibling repo script:
#   ../nu_llm_wiki/scripts/restart-dev.sh
#
# Usage (from anywhere):
#   ./scripts/brain/llm-wiki.sh status|start|stop|restart
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WIKI_ROOT="${NU_LLM_WIKI_ROOT:-$ROOT/../nu_llm_wiki}"
RESTART="${WIKI_ROOT}/scripts/restart-dev.sh"
APP_STATE="${LLM_WIKI_APP_STATE:-$HOME/Library/Application Support/com.llmwiki.app/app-state.json}"
HERMES_ENV="${HERMES_HOME:-$HOME/.hermes}/.env"
API_BASE="${LLM_WIKI_API_BASE_URL:-http://127.0.0.1:19828/api/v1}"
API_BASE="${API_BASE%/}"

usage() {
  cat <<EOF
Usage: $(basename "$0") status|start|stop|restart

  status    Print whether the local API is up, and copy the UI token into env files.
  start     If the API is already up, leave the app running. Otherwise start it.
  stop      Stop the dev app. UI settings are kept.
  restart   Stop, then start. UI settings are kept.

Exit codes:
  0  success (status: API is up)
  1  status: API is down; or start/restart: API did not come up
  2  API state is known, but the UI token could not be copied

The running Hermes llm_wiki tool process keeps whatever token it was started
with. If this script prints "token refreshed", start a new Hermes session
before wiki tools. Do not generate a new token in the UI to fix that.
EOF
}

# True when GET /health answers. No auth; the desktop app serves this on localhost.
api_up() {
  curl -fsS -m 2 -o /dev/null "${API_BASE}/health" 2>/dev/null
}

# Print unchanged, refreshed, or missing. Compares the UI token to ~/.hermes/.env.
# Does not print the token.
token_relation() {
  APP_STATE="$APP_STATE" HERMES_ENV="$HERMES_ENV" "$ROOT/scripts/py" - <<'PY'
import json
import os
from pathlib import Path

app = Path(os.environ["APP_STATE"])
hermes = Path(os.environ["HERMES_ENV"])
if not app.is_file():
    print("missing")
    raise SystemExit(0)
token = ((json.loads(app.read_text(encoding="utf-8")).get("apiConfig") or {}).get("token") or "").strip()
if not token:
    print("missing")
    raise SystemExit(0)
current = ""
if hermes.is_file():
    for line in hermes.read_text(encoding="utf-8").splitlines():
        if line.startswith("LLM_WIKI_API_TOKEN="):
            current = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
print("unchanged" if current == token else "refreshed")
PY
}

# Copy the UI token into repo .env and ~/.hermes/.env. Never mints a token.
sync_token() {
  local relation
  relation="$(token_relation)"
  case "$relation" in
    missing)
      echo "llm-wiki: no API token in app settings ($APP_STATE)." >&2
      echo "llm-wiki: open LLM Wiki, Settings → API + MCP, save once. Do not generate a token unless you mean to rotate it." >&2
      return 2
      ;;
    refreshed)
      bash "$ROOT/scripts/brain/sync-llm-wiki-token.sh"
      echo "llm-wiki: token refreshed in env files (value not printed)."
      echo "llm-wiki: the desktop app already uses the new token. Hermes wiki tools keep the old one until a new Hermes session starts the llm_wiki process again."
      ;;
    unchanged)
      bash "$ROOT/scripts/brain/sync-llm-wiki-token.sh"
      echo "llm-wiki: token unchanged."
      ;;
    *)
      echo "llm-wiki: unexpected token check: $relation" >&2
      return 2
      ;;
  esac
}

require_launcher() {
  if [[ ! -x "$RESTART" ]]; then
    echo "llm-wiki: launcher missing or not executable: $RESTART" >&2
    exit 1
  fi
}

# Block until the API answers, or fail with the dev log paths.
wait_until_up() {
  local seconds="$1"
  local i
  for ((i = 1; i <= seconds; i++)); do
    if api_up; then
      return 0
    fi
    sleep 1
  done
  echo "llm-wiki: API did not open at ${API_BASE}/health" >&2
  echo "llm-wiki: logs: ${WIKI_ROOT}/.local/vite-dev.log and ${WIKI_ROOT}/.local/llm-wiki.log" >&2
  return 1
}

# How long to wait. A missing debug binary means the launcher must compile first.
wait_budget() {
  local binary="${WIKI_ROOT}/src-tauri/target/debug/llm-wiki"
  if [[ -x "$binary" ]]; then
    echo 45
  else
    echo "llm-wiki: no debug binary yet; first start compiles and can take several minutes." >&2
    echo 300
  fi
}

start_app() {
  require_launcher
  if api_up; then
    echo "llm-wiki: already up ${API_BASE}/health"
    sync_token
    return
  fi
  local budget
  budget="$(wait_budget)"
  echo "llm-wiki: starting via ${RESTART} --detach"
  bash "$RESTART" --detach
  wait_until_up "$budget"
  echo "llm-wiki: up ${API_BASE}/health"
  sync_token
}

stop_app() {
  require_launcher
  bash "$RESTART" --stop-only
  if api_up; then
    echo "llm-wiki: API still up at ${API_BASE}/health" >&2
    exit 1
  fi
  echo "llm-wiki: stopped (UI settings kept)"
}

cmd="${1:-}"
case "$cmd" in
  -h|--help|help) usage; exit 0 ;;
  status)
    sync_rc=0
    sync_token || sync_rc=$?
    if api_up; then
      echo "llm-wiki: up ${API_BASE}/health"
      exit "$sync_rc"
    fi
    echo "llm-wiki: down"
    exit 1
    ;;
  start)
    start_app
    ;;
  stop)
    stop_app
    ;;
  restart)
    require_launcher
    local_budget="$(wait_budget)"
    echo "llm-wiki: restarting via ${RESTART} --detach"
    bash "$RESTART" --detach
    wait_until_up "$local_budget"
    echo "llm-wiki: up ${API_BASE}/health"
    sync_token
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
