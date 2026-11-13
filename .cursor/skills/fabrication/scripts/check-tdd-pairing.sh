#!/usr/bin/env bash
# Tier 2: PR diff must include test changes when production code changes.
# Requires TDD_PAIRING_BASE and TDD_PAIRING_HEAD (commit SHAs). Skips when unset.
#
# Optional (not implemented — document only):
#   scripts/check-tdd-commits.sh — per-commit test-first (Tier 3); weak with squash merges.
#   Skill tdd-red-first — thin AC loop wrapper for agents; procedure lives in implement-feature.

set -euo pipefail

# Expect to run from repository root (verify.sh and CI cd there first).
REPO_ROOT="$(pwd)"
cd "$REPO_ROOT"

BASE="${TDD_PAIRING_BASE:-}"
HEAD="${TDD_PAIRING_HEAD:-}"

if [[ -z "$BASE" || -z "$HEAD" ]]; then
  echo "check-tdd-pairing: skip (set TDD_PAIRING_BASE and TDD_PAIRING_HEAD for PR gate)"
  exit 0
fi

if [[ "$BASE" == "$HEAD" ]]; then
  echo "check-tdd-pairing: skip (BASE equals HEAD)"
  exit 0
fi

if git log --format=%B "$BASE..$HEAD" 2>/dev/null | grep -qE '^Skip-Gates:[[:space:]]*tdd-pairing'; then
  echo "check-tdd-pairing: skip (Skip-Gates: tdd-pairing)"
  exit 0
fi

is_prod=0
is_test=0
prod_files=()

while IFS= read -r path; do
  [[ -z "$path" ]] && continue
  case "$path" in
    backend/app/*)
      is_prod=1
      prod_files+=("$path")
      ;;
    frontend/src/*)
      case "$path" in
        *.test.ts | *.test.tsx | *.spec.ts | *.spec.tsx) is_test=1 ;;
        *)
          is_prod=1
          prod_files+=("$path")
          ;;
      esac
      ;;
    backend/tests/*)
      is_test=1
      ;;
  esac
done < <(git diff --name-only "$BASE" "$HEAD" || true)

if [[ "$is_prod" -eq 0 ]]; then
  echo "check-tdd-pairing: OK (no backend/app or frontend/src production changes)"
  exit 0
fi

if [[ "$is_test" -eq 0 ]]; then
  echo "::error::Production changes without test changes in diff (Tier 2 TDD pairing)."
  printf 'Production files:\n'
  printf '  %s\n' "${prod_files[@]}"
  echo ""
  echo "Add or update tests under backend/tests/ or frontend/src/**/*.test.*"
  echo "Or add commit message trailer: Skip-Gates: tdd-pairing"
  exit 1
fi

echo "check-tdd-pairing: OK (production and test files both changed)"
