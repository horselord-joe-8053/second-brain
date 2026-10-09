#!/usr/bin/env bash
# Hermes Desktop: ensure CLI, stack env, then install or build the native app (macOS).
set -euo pipefail
HERMES_AD="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=scripts/brain/adapters/hermes/hermes-env.sh
source "$HERMES_AD/hermes-env.sh"
ROOT="$SECOND_BRAIN_ROOT"

DESKTOP_PAGE="${HERMES_DESKTOP_URL:-https://hermes-agent.nousresearch.com/desktop}"
CACHE_DIR="$ROOT/brain/.cache"
DMG_PATH="$CACHE_DIR/Hermes-Setup.dmg"

find_hermes_app() {
  local p
  for p in \
    "/Applications/Hermes.app" \
    "$HOME/Applications/Hermes.app" \
    "$HOME/.hermes/hermes-agent/apps/desktop/release/mac-arm64/Hermes.app" \
    "$HOME/.hermes/hermes-agent/apps/desktop/release/mac/Hermes.app"; do
    if [[ -d "$p" ]]; then
      echo "$p"
      return 0
    fi
  done
  return 1
}

bash "$HERMES_AD/setup-hermes.sh"
bash "$ROOT/scripts/brain/apply-stack-config.sh"

OPEN_DOWNLOAD_PAGE=1
BUILD_FROM_SOURCE=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-open-download-page|--no-browser)
      OPEN_DOWNLOAD_PAGE=0
      shift
      ;;
    --build) BUILD_FROM_SOURCE=1; shift ;;
    -h|--help)
      echo "Usage: setup-hermes-desktop.sh [--build] [--no-open-download-page]"
      echo "  --build                  Build Hermes.app from CLI checkout (no DMG)"
      echo "  --no-open-download-page  Skip 'open' on the DMG marketing/download URL in Safari"
      echo "  (--no-browser is deprecated alias for --no-open-download-page; not Hermes web UI)"
      exit 0
      ;;
    *) echo "unknown: $1" >&2; exit 1 ;;
  esac
done

if app="$(find_hermes_app)"; then
  echo "setup-hermes-desktop: found $app"
  echo "Start with: ./scripts/brain/start-hermes.sh"
  exit 0
fi

echo "setup-hermes-desktop: Hermes.app not in Applications or CLI release folder."
echo "  Official installer (Apple Silicon DMG): $DESKTOP_PAGE"
echo "  After install, drag Hermes.app to /Applications and run ./scripts/brain/start-hermes.sh"

if [[ "$OPEN_DOWNLOAD_PAGE" -eq 1 ]] && command -v open >/dev/null 2>&1; then
  open "$DESKTOP_PAGE" || true
fi

if [[ "$BUILD_FROM_SOURCE" -eq 1 ]]; then
  echo "setup-hermes-desktop: building Desktop from ~/.hermes/hermes-agent (may take several minutes)…"
  hermes desktop --build-only --cwd "$ROOT"
  if app="$(find_hermes_app)"; then
    echo "setup-hermes-desktop: built $app"
  else
    echo "setup-hermes-desktop: build finished; if launch fails, retry: hermes desktop --cwd $ROOT"
  fi
else
  echo "setup-hermes-desktop: or build from CLI without DMG:"
  echo "  ./scripts/brain/setup-hermes-desktop.sh --build --no-open-download-page"
  echo "  ./scripts/brain/start-hermes.sh   # runs hermes desktop --cwd …"
fi
