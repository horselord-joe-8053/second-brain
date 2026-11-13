#!/usr/bin/env bash
# Hermes process detection and bring-up planning for agent.sh (source only).
set -euo pipefail

# shellcheck source=scripts/brain/adapters/hermes/hermes-env.sh
source "$(dirname "${BASH_SOURCE[0]}")/hermes-env.sh"

# desktop | tui — set by agent.sh / start-hermes before bring-up table.
HERMES_BRINGUP_UI="${HERMES_BRINGUP_UI:-desktop}"

hermes_gateway_status_text() {
  hermes gateway status 2>&1
}

hermes_gateway_supervised() {
  local text
  text="$(hermes_gateway_status_text)" || return 1
  grep -qE 'Gateway is supervised|✓ Gateway is running' <<< "$text"
}

hermes_gateway_supervisor_pid() {
  local text="${1:-}"
  if [[ -z "$text" ]]; then
    text="$(hermes_gateway_status_text 2>/dev/null)" || true
  fi
  grep -oE 'PID [0-9]+' <<< "$text" 2>/dev/null | head -1 | awk '{print $2}' || echo "-"
}

hermes_desktop_running() {
  command -v osascript >/dev/null 2>&1 || return 1
  osascript -e 'tell application "System Events" to (name of processes) contains "Hermes"' 2>/dev/null | grep -q true
}

hermes_desktop_pid() {
  if ! hermes_desktop_running; then
    echo "-"
    return
  fi
  pgrep -x Hermes 2>/dev/null | head -1 || echo "-"
}

hermes_tui_running() {
  local pidfile="${HERMES_PIDFILE:-$ROOT/.cache/hermes/hermes-chat.pid}"
  [[ -f "$pidfile" ]] || return 1
  local pid
  pid="$(tr -d ' \n' <"$pidfile")"
  [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

hermes_tui_pid() {
  local pidfile="${HERMES_PIDFILE:-$ROOT/.cache/hermes/hermes-chat.pid}"
  if hermes_tui_running; then
    tr -d ' \n' <"$pidfile"
  else
    echo "-"
  fi
}

hermes_agent_running() {
  hermes_gateway_supervised || hermes_desktop_running || hermes_tui_running
}

hermes_layer_row() {
  local name="$1" running="$2" pid="$3" notes="$4"
  printf "| %-9s | %-8s | %-5s | %-25s |\n" "$name" "$running" "$pid" "$notes"
}

# Loud bring-up plan: ASCII table on stdout, action summary on stdout.
hermes_print_bringup_plan() {
  local ui="${1:-$HERMES_BRINGUP_UI}"
  local gw_run="no" gw_pid="-" gw_note=""
  local desk_run="n/a" desk_pid="-" desk_note=""
  local tui_run="n/a" tui_pid="-" tui_note=""
  local gw_text=""
  local -a will_start=()

  if hermes_gateway_supervised; then
    gw_run="yes"
    gw_text="$(hermes_gateway_status_text 2>/dev/null)" || gw_text=""
    gw_pid="$(hermes_gateway_supervisor_pid "$gw_text")"
    gw_note="launchd supervised"
  else
    gw_run="no"
    gw_note="will start"
    will_start+=("gateway")
  fi

  if [[ "$ui" == "desktop" ]]; then
    tui_run="n/a"
    tui_note="not requested"
    if hermes_desktop_running; then
      desk_run="yes"
      desk_pid="$(hermes_desktop_pid)"
      desk_note="Electron"
    else
      desk_run="no"
      desk_note="will start"
      will_start+=("desktop")
    fi
  else
    desk_run="n/a"
    desk_note="not requested"
    if hermes_tui_running; then
      tui_run="yes"
      tui_pid="$(hermes_tui_pid)"
      tui_note="detach pidfile"
    else
      tui_run="no"
      tui_note="will start"
      will_start+=("tui")
    fi
  fi

  echo ""
  echo "=== Hermes agent bring-up (mode: ${ui}) ==="
  echo "+-----------+----------+-------+---------------------------+"
  echo "| Component | Running? | PID   | Notes                     |"
  echo "+-----------+----------+-------+---------------------------+"
  hermes_layer_row "gateway" "$gw_run" "$gw_pid" "$gw_note"
  hermes_layer_row "desktop" "$desk_run" "$desk_pid" "$desk_note"
  hermes_layer_row "tui" "$tui_run" "$tui_pid" "$tui_note"
  echo "+-----------+----------+-------+---------------------------+"
  if ((${#will_start[@]} == 0)); then
    echo "Will start: (none — target state already satisfied)"
  else
    echo "Will start: ${will_start[*]}"
  fi
  echo ""
}

hermes_bringup_log_skip() {
  local component="$1" pid="${2:--}" detail="${3:-}"
  echo "hermes bring-up: SKIP ${component} — already running (PID ${pid}) ${detail}" >&2
}

hermes_bringup_log_start() {
  local component="$1"
  echo "hermes bring-up: START ${component} …" >&2
}

hermes_bringup_log_done() {
  local component="$1"
  echo "hermes bring-up: DONE ${component}" >&2
}

hermes_bringup_log_all_satisfied() {
  echo "hermes bring-up: all requested components already up — no process launches." >&2
}
