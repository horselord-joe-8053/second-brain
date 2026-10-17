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
  status    Print active harness and best-effort process hints

Start options:
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
    ENSURE=0
    START_ARGS=()
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --ensure-setup) ENSURE=1; shift ;;
        --install) START_ARGS+=("--install"); shift ;;
        *) START_ARGS+=("$1"); shift ;;
      esac
    done
    HARNESS="$(resolve_harness)"
    export AGENT_SH_APPLIED_STACK=1
    bash "$BRAIN/apply-stack-config.sh"
    if [[ "$ENSURE" -eq 1 ]]; then
      ensure_harness_light "$HARNESS"
    fi
    delegate_start "$HARNESS" "${START_ARGS[@]}"
    ;;
  stop)
    HARNESS="$(resolve_harness)"
    delegate_stop "$HARNESS" "$@"
    ;;
  restart)
    HARNESS="$(resolve_harness)"
    delegate_stop "$HARNESS"
    export AGENT_SH_APPLIED_STACK=1
    bash "$BRAIN/apply-stack-config.sh"
    delegate_start "$HARNESS" "$@"
    ;;
  status)
    HARNESS="$(resolve_harness)"
    echo "agent.sh status: active_harness=$HARNESS (from config/brain-stack.yaml)"
    case "$HARNESS" in
      hermes)
        if command -v hermes >/dev/null 2>&1; then
          echo "  hermes CLI: $(command -v hermes)"
        else
          echo "  hermes CLI: not on PATH (run: agent.sh setup)"
        fi
        PIDFILE="${HERMES_PIDFILE:-$ROOT/.cache/hermes/hermes-chat.pid}"
        if [[ -f "$PIDFILE" ]]; then
          echo "  detach TUI pidfile: $PIDFILE"
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
