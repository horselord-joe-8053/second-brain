#!/usr/bin/env bash
# Stop Hermes Desktop app and/or detached TUI from start-hermes.sh --tui --detach.
set -euo pipefail
# shellcheck source=scripts/brain/hermes-env.sh
source "$(dirname "$0")/hermes-env.sh"

PIDFILE="${HERMES_PIDFILE:-$ROOT/brain/.cache/hermes-chat.pid}"

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

if command -v osascript >/dev/null 2>&1; then
  if osascript -e 'tell application "System Events" to (name of processes) contains "Hermes"' 2>/dev/null | grep -q true; then
    osascript -e 'tell application "Hermes" to quit' 2>/dev/null || true
    echo "stop-hermes: quit Hermes Desktop"
    stopped=1
  fi
fi

if [[ "$stopped" -eq 0 ]]; then
  echo "stop-hermes: no running Hermes Desktop or detach TUI found"
fi
