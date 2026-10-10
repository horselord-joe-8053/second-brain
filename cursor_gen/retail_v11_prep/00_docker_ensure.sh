#!/usr/bin/env bash
# Ensure Docker CLI exists on PATH and daemon is running before retail_pg compose.
# Does NOT install Docker Desktop by default. Optional idempotent brew cask upgrade
# when RETAIL_DOCKER_BREW_UPGRADE=1. Fails fast with HG-DOCKER / HG-DOCKER-UPDATE hints.
set -euo pipefail

PREP_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=cursor_gen/retail_v11_prep/lib/require_external.sh
source "$PREP_DIR/lib/require_external.sh"

MAX_WAIT="${DOCKER_START_WAIT_SEC:-120}"

DOCKER_INSTALL_HINT="Install Docker Desktop (includes docker CLI), then re-run:
  macOS:  brew install --cask docker
          — or — https://www.docker.com/products/docker-desktop/
  Linux:  your distro docker engine + compose plugin (docker compose version)

We do not auto-download or auto-install Docker unless RETAIL_DOCKER_BREW_UPGRADE=1 (Homebrew cask only)."

DOCKER_UPDATE_HINT="HG-DOCKER-UPDATE: Docker Desktop may need an update or must finish updating before the daemon accepts connections.

Human steps (pick what matches your install):
  1. Open Docker Desktop from Applications — complete any **Update** / **Restart** prompt and wait until the whale icon is steady (Running).
  2. If you installed via Homebrew, you may re-run once with:
       RETAIL_DOCKER_BREW_UPGRADE=1 bash cursor_gen/retail_v11_prep/00_docker_ensure.sh
     (runs \`brew upgrade --cask docker\` idempotently, then starts the app — needs network).
  3. When \`docker info\` works in Terminal, re-run Phase 6 from step 6.2.

We do not click through Docker Desktop update UI from this script."

log() { echo "00_docker_ensure: $*"; }

docker_daemon_ok() {
  docker info >/dev/null 2>&1
}

# Last docker info failure (combined stderr+stdout), for classification.
docker_info_failure_log() {
  docker info 2>&1 || true
}

classify_docker_failure() {
  local blob="$1"
  if echo "$blob" | grep -qiE 'update|upgrade|new version|please update|restart docker desktop'; then
    echo "update"
  elif echo "$blob" | grep -qiE 'starting|initializing|loading|is starting'; then
    echo "starting"
  else
    echo "down"
  fi
}

maybe_brew_upgrade_docker_cask() {
  if [[ "${RETAIL_DOCKER_BREW_UPGRADE:-0}" != "1" ]]; then
    return 0
  fi
  if [[ "$(uname -s)" != "Darwin" ]]; then
    log "RETAIL_DOCKER_BREW_UPGRADE=1 ignored (not macOS)."
    return 0
  fi
  if ! command -v brew >/dev/null 2>&1; then
    log "RETAIL_DOCKER_BREW_UPGRADE=1 set but brew not on PATH — skip cask upgrade."
    return 0
  fi
  if ! brew list --cask docker >/dev/null 2>&1; then
    log "RETAIL_DOCKER_BREW_UPGRADE=1 set but 'brew list --cask docker' failed — skip (install via brew or use .dmg)."
    return 0
  fi
  log "RETAIL_DOCKER_BREW_UPGRADE=1 — running idempotent: brew upgrade --cask docker"
  if ! brew upgrade --cask docker; then
    log "brew upgrade --cask docker failed — complete update in Docker Desktop manually."
  fi
}

start_docker_desktop_macos() {
  if [[ -d "/Applications/Docker.app" ]]; then
    log "Starting Docker Desktop (open -a Docker)..."
    open -a Docker || true
    return 0
  fi
  echo "" >&2
  echo "STOP (HG-DOCKER): 'docker' is on PATH but /Applications/Docker.app is missing." >&2
  echo "" >&2
  echo "$DOCKER_INSTALL_HINT" >&2
  exit 1
}

fail_docker_not_ready() {
  local reason="$1"
  local err_log="$2"
  echo "" >&2
  echo "STOP (HG-DOCKER): Docker daemon not ready after ${MAX_WAIT}s (reason: ${reason})." >&2
  if [[ -n "$err_log" ]]; then
    echo "" >&2
    echo "Last \`docker info\` output:" >&2
    echo "$err_log" | tail -8 >&2
  fi
  echo "" >&2
  if [[ "$reason" == "update" ]]; then
    echo "$DOCKER_UPDATE_HINT" >&2
  else
    echo "Open Docker Desktop manually, wait until Running, then re-run:" >&2
    echo "  bash cursor_gen/retail_v11_prep/00_docker_ensure.sh" >&2
    echo "" >&2
    echo "If Docker asked you to update, use HG-DOCKER-UPDATE steps in cursor_gen/retail_v11_prep/README.md" >&2
  fi
  exit 1
}

require_cmd docker "$DOCKER_INSTALL_HINT"

if docker_daemon_ok; then
  log "Docker CLI found ($(command -v docker)); daemon already running."
  exit 0
fi

ERR_LOG="$(docker_info_failure_log)"
REASON="$(classify_docker_failure "$ERR_LOG")"
log "Daemon not ready (class=${REASON})."

maybe_brew_upgrade_docker_cask

if [[ "$(uname -s)" == "Darwin" ]]; then
  start_docker_desktop_macos
else
  log "Docker CLI found but daemon is down — start Docker on this host (e.g. sudo systemctl start docker), then re-run."
  exit 1
fi

log "Waiting up to ${MAX_WAIT}s for daemon (docker info)..."
for ((i = 0; i < MAX_WAIT; i++)); do
  if docker_daemon_ok; then
    log "Docker daemon ready."
    exit 0
  fi
  if (( i > 0 && i % 30 == 0 )); then
    REASON="$(classify_docker_failure "$(docker_info_failure_log)")"
    log "Still waiting (${i}s, class=${REASON})..."
    if [[ "$REASON" == "update" && "${RETAIL_DOCKER_BREW_UPGRADE:-0}" != "1" ]]; then
      log "Hint: if Docker Desktop is waiting on an update, finish it in the UI or re-run with RETAIL_DOCKER_BREW_UPGRADE=1 (Homebrew cask)."
    fi
  fi
  sleep 1
done

fail_docker_not_ready "$(classify_docker_failure "$(docker_info_failure_log)")" "$(docker_info_failure_log)"
