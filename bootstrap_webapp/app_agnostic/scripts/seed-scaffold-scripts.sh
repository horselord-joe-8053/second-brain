#!/usr/bin/env bash
# Copy canonical verify.sh + dev.sh from kit templates into target repo.

set -euo pipefail

REPO_ROOT="${1:-.}"
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
KIT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPL="$KIT/templates/scripts"

AGNOSTIC="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p "$REPO_ROOT/scripts"
cp "$TEMPL/verify.sh" "$TEMPL/dev.sh" "$REPO_ROOT/scripts/"
cp "$AGNOSTIC/scripts/check-ac-tests.py" "$AGNOSTIC/scripts/check-tdd-pairing.sh" "$REPO_ROOT/scripts/"
chmod +x "$REPO_ROOT/scripts/verify.sh" "$REPO_ROOT/scripts/dev.sh" \
  "$REPO_ROOT/scripts/check-ac-tests.py" "$REPO_ROOT/scripts/check-tdd-pairing.sh"
echo "seed-scaffold-scripts: copied verify.sh, dev.sh, check-ac-tests.py, check-tdd-pairing.sh"
