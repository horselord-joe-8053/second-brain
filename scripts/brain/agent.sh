#!/usr/bin/env bash
# Single operator entry for Second Brain harness lifecycle (Hermes / OpenClaw).
#
# Usage:
#   ./scripts/brain/agent.sh setup|start|stop|restart|status|help
#   ./scripts/brain/agent.sh start [--ensure-setup] [--install] [passthrough args…]
set -euo pipefail

BRAIN="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$BRAIN/../.." && pwd)"
cd "$ROOT"

resolve_harness() {
  "$ROOT/scripts/py" -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('${ROOT}') / 'scripts' / 'brain'))
from brain_stack import active_harness, load_brain_stack
print(active_harness(load_brain_stack(Path('${ROOT}'))))
"
}

usage() {
  sed -n '2,7p' "$0"
  cat <<'EOF'
Subcommands:
  setup     Full idempotent bootstrap (setup-local.sh: stack, harness adapter, corpus checks)
  start     Apply stack config, then adapters/<harness>/start.sh
  stop      adapters/<harness>/stop.sh
  restart   stop then start
  status    Print active harness, Hermes bring-up table, process hints

Start / restart / status options:
  --ensure-setup   If harness probe fails, run adapters/<harness>/setup-harness.sh only
  --install        (Hermes) install Desktop app if missing before launch

Do not call adapters/*/start-hermes.sh directly — use this script.
LLM Wiki process: ./scripts/brain/llm-wiki.sh (separate entry).
EOF
}

ensure_harness_light() {
  local harness="$1"
  case "$harness" in
    hermes)
      if command -v hermes >/dev/null 2>&1 && hermes doctor >/dev/null 2>&1; then
        return 0
      fi
      echo "agent.sh: light ensure — running adapters/hermes/setup-harness.sh"
      bash "$BRAIN/adapters/hermes/setup-harness.sh"
      ;;
    openclaw)
      echo "agent.sh: light ensure — running adapters/openclaw/setup-harness.sh"
      bash "$BRAIN/adapters/openclaw/setup-harness.sh" || true
      ;;
    *)
      echo "agent.sh: unknown harness '$harness' — skip ensure-setup" >&2
      ;;
  esac
}

delegate_start() {
  local harness="$1"
  shift
  local start="$BRAIN/adapters/$harness/start.sh"
  if [[ ! -f "$start" ]]; then
    echo "agent.sh: missing delegate $start" >&2
    exit 1
  fi
  exec bash "$start" "$@"
}

delegate_stop() {
  local harness="$1"
  local stop="$BRAIN/adapters/$harness/stop.sh"
  if [[ ! -f "$stop" ]]; then
    echo "agent.sh: missing delegate $stop" >&2
    exit 1
  fi
  bash "$stop"
}

# Parse start/restart flags into ENSURE and START_ARGS (mutates globals).
parse_start_flags() {
  ENSURE=0
  START_ARGS=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --ensure-setup) ENSURE=1; shift ;;
      --install) START_ARGS+=("--install"); shift ;;
      *) START_ARGS+=("$1"); shift ;;
    esac
  done
}

# Hermes only: desktop unless --tui / --terminal in START_ARGS.
export_hermes_bringup_ui_from_args() {
  HERMES_BRINGUP_UI="desktop"
  for arg in "${START_ARGS[@]+"${START_ARGS[@]}"}"; do
    if [[ "$arg" == "--tui" || "$arg" == "--terminal" ]]; then
      HERMES_BRINGUP_UI="tui"
      break
    fi
  done
  export HERMES_BRINGUP_UI
}

# Print D15 bring-up table when active harness is Hermes.
hermes_emit_bringup_plan() {
  local harness="$1"
  [[ "$harness" == "hermes" ]] || return 0
  # shellcheck source=scripts/brain/adapters/hermes/hermes-runtime.sh
  source "$BRAIN/adapters/hermes/hermes-runtime.sh"
  export_hermes_bringup_ui_from_args
  hermes_print_bringup_plan "$HERMES_BRINGUP_UI"
}

run_apply_stack_and_start() {
  local harness="$1"
  export AGENT_SH_APPLIED_STACK=1
  bash "$BRAIN/apply-stack-config.sh"
  if [[ "$ENSURE" -eq 1 ]]; then
    ensure_harness_light "$harness"
  fi
  if ((${#START_ARGS[@]} > 0)); then
    delegate_start "$harness" "${START_ARGS[@]}"
  else
    delegate_start "$harness"
  fi
}

CMD="${1:-help}"
if [[ "$CMD" == "-h" || "$CMD" == "--help" ]]; then
  usage
  exit 0
fi
shift || true

case "$CMD" in
  help)
    usage
    ;;
  setup)
    exec bash "$BRAIN/setup-local.sh" "$@"
    ;;
  start)
    parse_start_flags "$@"
    HARNESS="$(resolve_harness)"
    hermes_emit_bringup_plan "$HARNESS"
    run_apply_stack_and_start "$HARNESS"
    ;;
  stop)
    HARNESS="$(resolve_harness)"
    delegate_stop "$HARNESS" "$@"
    ;;
  restart)
    parse_start_flags "$@"
    HARNESS="$(resolve_harness)"
    delegate_stop "$HARNESS"
    hermes_emit_bringup_plan "$HARNESS"
    run_apply_stack_and_start "$HARNESS"
    ;;
  status)
    parse_start_flags "$@"
    HARNESS="$(resolve_harness)"
    echo "agent.sh status: active_harness=$HARNESS (from config/brain-stack.yaml)"
    case "$HARNESS" in
      hermes)
        if command -v hermes >/dev/null 2>&1; then
          echo "  hermes CLI: $(command -v hermes)"
        else
          echo "  hermes CLI: not on PATH (run: agent.sh setup)"
        fi
        hermes_emit_bringup_plan "$HARNESS"
        # shellcheck source=scripts/brain/adapters/hermes/hermes-runtime.sh
        source "$BRAIN/adapters/hermes/hermes-runtime.sh"
        if hermes_agent_running; then
          echo "  agent running: yes"
          hermes_gateway_status_text 2>/dev/null | sed 's/^/    /' || true
        else
          echo "  agent running: no (safe to agent.sh start)"
        fi
        ;;
      openclaw)
        echo "  OpenClaw start not wired — see docs_manual_gen/RUNBOOK_HARNESS_OPENCLAW.md"
        ;;
    esac
    echo "  Commands: agent.sh help | setup | start | stop | restart"
    ;;
  *)
    echo "agent.sh: unknown subcommand '$CMD' (try help)" >&2
    exit 1
    ;;
esac
