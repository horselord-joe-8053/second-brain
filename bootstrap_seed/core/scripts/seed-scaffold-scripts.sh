#!/usr/bin/env bash
# Copy verify/dev/check scripts. Optional 2nd arg: webapp → factory scripts from modules/webapp.

set -euo pipefail

REPO_ROOT="${1:-.}"
PROFILE="${2:-general}"
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
CORE="$(cd "$(dirname "$0")/.." && pwd)"
KIT="$(cd "$CORE/.." && pwd)"

SCRIPT_SRC="$CORE/templates/scripts"
CHECK_AC="$CORE/scripts/check-ac-tests.py"
if [[ "$PROFILE" == "webapp" ]]; then
  SCRIPT_SRC="$KIT/modules/webapp/templates/scripts"
  CHECK_AC="$KIT/modules/webapp/scripts/check-ac-tests.py"
fi

mkdir -p "$REPO_ROOT/scripts"
cp "$SCRIPT_SRC/verify.sh" "$SCRIPT_SRC/dev.sh" "$REPO_ROOT/scripts/"
cp "$CHECK_AC" "$CORE/scripts/check-tdd-pairing.sh" "$REPO_ROOT/scripts/"
chmod +x "$REPO_ROOT/scripts/verify.sh" "$REPO_ROOT/scripts/dev.sh" "$REPO_ROOT/scripts/check-tdd-pairing.sh"
echo "seed-scaffold-scripts: profile=$PROFILE done."
