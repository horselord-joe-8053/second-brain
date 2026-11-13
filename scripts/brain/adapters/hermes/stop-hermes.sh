#!/usr/bin/env bash
# Stop Hermes agent stack — internal; use scripts/brain/agent.sh stop.
set -euo pipefail
# shellcheck source=scripts/brain/adapters/hermes/hermes-env.sh
source "$(dirname "$0")/hermes-env.sh"
# shellcheck source=scripts/brain/adapters/hermes/hermes-runtime.sh
source "$(dirname "$0")/hermes-runtime.sh"

PIDFILE="${HERMES_PIDFILE:-$ROOT/.cache/hermes/hermes-chat.pid}"

stopped=0

if [[ -f "$PIDFILE" ]]; then
  pid="$(tr -d ' \n' <"$PIDFILE")"
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    echo "stop-hermes: stopped TUI pid $pid"
    stopped=1
  fi
  rm -f "$PIDFILE"
fi

if hermes_desktop_running; then
  osascript -e 'tell application "Hermes" to quit' 2>/dev/null || true
  echo "stop-hermes: quit Hermes Desktop"
  stopped=1
fi

if hermes_gateway_supervised; then
  echo "stop-hermes: stopping messaging gateway…"
  if hermes gateway stop; then
    echo "stop-hermes: gateway stop requested"
    stopped=1
  else
    echo "stop-hermes: warning — hermes gateway stop failed (see hermes gateway status)" >&2
  fi
fi

if [[ "$stopped" -eq 0 ]]; then
  echo "stop-hermes: no running Hermes gateway, Desktop, or detach TUI found"
fi
