#!/usr/bin/env bash
# P5 / HG-5: install Obsidian (Homebrew cask) and optionally open the active profile's wiki vault.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
# shellcheck source=scripts/brain/brain-profile-env.sh
source "$ROOT/scripts/brain/brain-profile-env.sh"
VAULT="${SECOND_BRAIN_OBSIDIAN_VAULT:-$SECOND_BRAIN_WIKI_VAULT}"

if ! command -v brew >/dev/null 2>&1; then
  echo "setup-obsidian: Homebrew not found — install from https://brew.sh then re-run"
  exit 1
fi

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "setup-obsidian: skip (Obsidian cask step is macOS-only)"
  exit 0
fi

if brew list --cask obsidian >/dev/null 2>&1; then
  echo "setup-obsidian: Obsidian cask already installed"
else
  echo "setup-obsidian: installing Obsidian (brew install --cask obsidian)"
  brew install --cask obsidian
fi

if [[ ! -d "$VAULT" ]]; then
  echo "setup-obsidian: vault path missing: $VAULT"
  exit 1
fi

if [[ "${OPEN_OBSIDIAN_VAULT:-0}" == "1" ]]; then
  echo "setup-obsidian: opening vault in Obsidian"
  open -a Obsidian "$VAULT"
else
  echo "setup-obsidian: vault ready at $VAULT (set OPEN_OBSIDIAN_VAULT=1 to launch Obsidian)"
fi

echo "setup-obsidian: OK"
