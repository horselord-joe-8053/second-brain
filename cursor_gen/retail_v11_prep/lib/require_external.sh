#!/usr/bin/env bash
# Shared guard: external binaries must exist on PATH before prep continues.
# Pattern: source this file, call require_cmd / require_python_module — never auto-install.
set -euo pipefail

_sb_repo_py() {
  # This file lives at cursor_gen/retail_v11_prep/lib/.
  local here repo
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  repo="$(cd "$here/../../.." && pwd)"
  printf '%s\n' "$repo/scripts/py"
}


# require_cmd <name> — prints install_hint (remaining args or stdin) and exits 1 if missing.
require_cmd() {
  local name="$1"
  shift
  if command -v "$name" >/dev/null 2>&1; then
    return 0
  fi
  echo "" >&2
  echo "STOP: required command '$name' is not on PATH (check: which $name)." >&2
  if (("$#" > 0)); then
    echo "" >&2
    echo "$*" >&2
  fi
  echo "" >&2
  echo "Install the package above, then re-run this prep script." >&2
  exit 1
}

# require_python_module <import_name> [pip_install_hint]
require_python_module() {
  local mod="$1"
  local hint="${2:-pip install $mod}"
  if "$(_sb_repo_py)" -c "import ${mod}" >/dev/null 2>&1; then
    return 0
  fi
  echo "" >&2
  echo "STOP: Python module '$mod' is not available for the repo interpreter." >&2
  echo "" >&2
  echo "$hint" >&2
  echo "" >&2
  echo "Install it, then re-run this prep script." >&2
  exit 1
}
