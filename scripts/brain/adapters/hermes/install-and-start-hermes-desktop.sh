#!/usr/bin/env bash
# One command: wire Second Brain → Hermes config, ensure Desktop app, launch Desktop (not TUI).
set -euo pipefail
HERMES_AD="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERMES_AD/../../../.." && pwd)"
cd "$ROOT"

PROVIDER=""
MODEL=""
SKIP_INSTALL=0
OPEN_DL=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --provider) PROVIDER="${2:-}"; shift 2 ;;
    -m|--model) MODEL="${2:-}"; shift 2 ;;
    --skip-install) SKIP_INSTALL=1; shift ;;
    --no-open-download-page|--no-browser) OPEN_DL=0; shift ;;
    -h|--help)
      echo "Usage: install-and-start-hermes-desktop.sh [--provider P] [-m MODEL] [--skip-install]"
      echo "  Installs/builds Hermes Desktop if needed, applies stack env, starts Desktop UI."
      exit 0
      ;;
    *) echo "unknown: $1" >&2; exit 1 ;;
  esac
done

if [[ "$SKIP_INSTALL" -eq 0 ]]; then
  extra=()
  [[ "$OPEN_DL" -eq 0 ]] && extra+=(--no-open-download-page)
  bash "$HERMES_AD/setup-hermes-desktop.sh" "${extra[@]}"
fi

bash "$ROOT/scripts/brain/apply-stack-config.sh"

start_args=()
[[ -n "$PROVIDER" ]] && start_args+=(--provider "$PROVIDER")
[[ -n "$MODEL" ]] && start_args+=(-m "$MODEL")

exec bash "$HERMES_AD/start-hermes.sh" "${start_args[@]}"
