#!/usr/bin/env bash
# Shared path variables for the fabrication skill tree (source from sibling scripts).

fab_load_paths() {
  local caller="${1:-}"
  FAB_SCRIPTS="$(cd "$(dirname "$caller")" && pwd)"
  FAB_ROOT="$(cd "$FAB_SCRIPTS/.." && pwd)"
  FAB_REF="$FAB_ROOT/references"
  FAB_ASSETS="$FAB_ROOT/assets"
  FAB_HARNESS="$FAB_REF/harness"
  # Names used in references/bootstrap-core.md and agent docs:
  CORE="$FAB_SCRIPTS"
  KIT="$FAB_ROOT"
}
