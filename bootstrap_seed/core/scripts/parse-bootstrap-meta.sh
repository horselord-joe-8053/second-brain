#!/usr/bin/env bash
# Source from other kit scripts: read specific/bootstrap.md meta lines.
# Usage: eval "$(bash parse-bootstrap-meta.sh "$KIT/specific/bootstrap.md")"

set -euo pipefail

BOOT="${1:-}"
PROFILE="general"
ENV_APPEND="none"
PHASE1_MODULES=""
PHASE2_MODULES=""

if [[ -f "$BOOT" ]]; then
  while IFS= read -r line; do
    case "$line" in
      profile:*)
        PROFILE="$(echo "$line" | sed 's/^profile:[[:space:]]*//' | tr -d '\r')"
        ;;
      env_append:*)
        ENV_APPEND="$(echo "$line" | sed 's/^env_append:[[:space:]]*//' | tr -d '\r')"
        ;;
      phase1_modules:*)
        PHASE1_MODULES="$(echo "$line" | sed 's/^phase1_modules:[[:space:]]*//' | tr -d '\r')"
        ;;
      phase2_modules:*)
        PHASE2_MODULES="$(echo "$line" | sed 's/^phase2_modules:[[:space:]]*//' | tr -d '\r')"
        ;;
    esac
  done < <(grep -E '^(profile|env_append|phase1_modules|phase2_modules):' "$BOOT" 2>/dev/null || true)
fi

printf 'export BOOTSTRAP_PROFILE=%q\n' "$PROFILE"
printf 'export BOOTSTRAP_ENV_APPEND=%q\n' "$ENV_APPEND"
printf 'export BOOTSTRAP_PHASE1_MODULES=%q\n' "$PHASE1_MODULES"
printf 'export BOOTSTRAP_PHASE2_MODULES=%q\n' "$PHASE2_MODULES"
