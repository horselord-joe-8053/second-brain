#!/usr/bin/env bash
# Start Hermes Desktop (default) or terminal TUI — internal; use scripts/brain/agent.sh start.
#
# Usage (via agent.sh start):
#   --provider gemini -m gemini-3.0-flash
#   --tui          # terminal UI instead of Desktop
#   --install      # run setup-hermes-desktop.sh if Hermes.app missing
set -euo pipefail
# shellcheck source=scripts/brain/adapters/hermes/hermes-env.sh
source "$(dirname "$0")/hermes-env.sh"
# shellcheck source=scripts/brain/adapters/hermes/hermes-runtime.sh
source "$(dirname "$0")/hermes-runtime.sh"

UI="${HERMES_BRINGUP_UI:-desktop}"
PROVIDER=""
MODEL=""
INSTALL_DESKTOP=0
EXTRA=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tui|--terminal)
      UI="tui"
      export HERMES_BRINGUP_UI="tui"
      shift
      ;;
    --desktop)
      UI="desktop"
      export HERMES_BRINGUP_UI="desktop"
      shift
      ;;
    --provider)
      PROVIDER="${2:-}"
      shift 2
      ;;
    -m|--model)
      MODEL="${2:-}"
      shift 2
      ;;
    --install)
      INSTALL_DESKTOP=1
      shift
      ;;
    --detach)
      echo "start-hermes: --detach applies to --tui only; Desktop runs as its own app." >&2
      shift
      ;;
    --)
      shift
      EXTRA+=("$@")
      break
      ;;
    -h|--help)
      sed -n '2,8p' "$0"
      echo "  --desktop (default)  Hermes Desktop (Electron)"
      echo "  --tui                hermes chat --tui"
      exit 0
      ;;
    *)
      EXTRA+=("$1")
      shift
      ;;
  esac
done

read_defaults() {
  "$ROOT/scripts/py" - <<'PY' "$ROOT" "$PROVIDER" "$MODEL"
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / "scripts" / "brain"))
from brain_stack import load_brain_stack
prov, model = sys.argv[2], sys.argv[3]
try:
    h = load_brain_stack(Path(sys.argv[1])).get("hermes") or {}
except FileNotFoundError:
    h = {}
if not prov and h.get("chat_provider"):
    print(f"provider={h['chat_provider']}")
if not model and h.get("chat_model"):
    print(f"model={h['chat_model']}")
PY
}

while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  case "$line" in
    provider=*) PROVIDER="${line#provider=}" ;;
    model=*) MODEL="${line#model=}" ;;
  esac
done < <(read_defaults || true)

if [[ -n "$PROVIDER" || -n "$MODEL" ]]; then
  export APPLY_STACK_SKIP_MODEL=1
fi
if [[ "${AGENT_SH_APPLIED_STACK:-0}" != "1" ]]; then
  bash "$ROOT/scripts/brain/apply-stack-config.sh" >/dev/null
fi

if [[ -n "$PROVIDER" ]]; then
  hermes config set model.provider "$PROVIDER"
fi
if [[ -n "$MODEL" ]]; then
  hermes config set model.default "$MODEL"
fi

hermes_desktop_app_paths() {
  printf '%s\n' \
    "/Applications/Hermes.app" \
    "$HOME/Applications/Hermes.app" \
    "$HOME/.hermes/hermes-agent/apps/desktop/release/mac-arm64/Hermes.app" \
    "$HOME/.hermes/hermes-agent/apps/desktop/release/mac/Hermes.app"
}

hermes_app_installed() {
  local app
  while IFS= read -r app; do
    [[ -d "$app" ]] && return 0
  done < <(hermes_desktop_app_paths)
  return 1
}

launch_desktop_app() {
  local app
  while IFS= read -r app; do
    if [[ -d "$app" ]]; then
      echo "start-hermes: opening $app (cwd $ROOT)"
      open -a "$app" --args --cwd "$ROOT" 2>/dev/null && return 0
      open -a "$app" "$ROOT" 2>/dev/null && return 0
      open -a "$app" && return 0
    fi
  done < <(hermes_desktop_app_paths)
  return 1
}

if hermes_gateway_supervised; then
  hermes_bringup_log_skip "gateway" "$(hermes_gateway_supervisor_pid)"
else
  hermes_bringup_log_start "gateway"
  hermes gateway start
  hermes_bringup_log_done "gateway"
fi

if [[ "$UI" == "desktop" ]]; then
  export HERMES_DESKTOP_CWD="$ROOT"
  if hermes_desktop_running; then
    hermes_bringup_log_skip "desktop" "$(hermes_desktop_pid)"
    echo "hermes bring-up: target state satisfied for desktop mode." >&2
    exit 0
  fi
  if [[ "$INSTALL_DESKTOP" -eq 1 ]] && ! hermes_app_installed; then
    bash "$(dirname "$0")/setup-hermes-desktop.sh" --no-open-download-page 2>/dev/null || \
      bash "$(dirname "$0")/setup-hermes-desktop.sh"
  fi
  if [[ -n "$PROVIDER" || -n "$MODEL" ]]; then
    echo "start-hermes: config model → provider=${PROVIDER:-config} default=${MODEL:-config}"
    echo "start-hermes: in Desktop use **New session**; pick the same model in the dropdown (UI overrides per session)."
  fi
  # Prefer hermes desktop when model flags set so config is read on launch (open -a reuses old app/session).
  if [[ -n "$PROVIDER" || -n "$MODEL" ]]; then
    bash "$(dirname "$0")/stop-hermes.sh" >/dev/null 2>&1 || true
    exec hermes desktop --cwd "$ROOT"
  fi
  hermes_bringup_log_start "desktop"
  if launch_desktop_app; then
    hermes_bringup_log_done "desktop"
    exit 0
  fi
  echo "start-hermes: Hermes.app not found — building/launching via CLI (first run can take several minutes)…"
  echo "  Install DMG: ./scripts/brain/setup-hermes-desktop.sh"
  hermes desktop --cwd "$ROOT"
  hermes_bringup_log_done "desktop"
  exit 0
fi

if hermes_tui_running; then
  hermes_bringup_log_skip "tui" "$(hermes_tui_pid)"
  hermes_bringup_log_all_satisfied
  exit 0
fi

PIDFILE="${HERMES_PIDFILE:-$ROOT/.cache/hermes/hermes-chat.pid}"
ARGS=(chat --tui --accept-hooks)
[[ -n "$PROVIDER" ]] && ARGS+=(--provider "$PROVIDER")
[[ -n "$MODEL" ]] && ARGS+=(-m "$MODEL")
if ((${#EXTRA[@]} > 0)); then
  ARGS+=("${EXTRA[@]}")
fi

if [[ ! -t 1 ]]; then
  echo "start-hermes: no TTY for --tui — use default Desktop or run from Terminal." >&2
  exit 1
fi

hermes_bringup_log_start "tui"
exec hermes "${ARGS[@]}"
