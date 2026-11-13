#!/usr/bin/env bash
# Fail if the fabrication skill tree contains product-specific paths or forbidden strings.
set -euo pipefail

# shellcheck source=fabrication-paths.sh
source "$(dirname "$0")/fabrication-paths.sh"
fab_load_paths "${BASH_SOURCE[0]}"

cd "$FAB_ROOT"

fail() { echo "check-seed-kit: $1" >&2; exit 1; }

for d in specific assets/modules/second-brain assets/utils/pglpl_cert assets/utils/chatgpt/transcripts; do
  [[ -e "$d" ]] && fail "forbidden path exists: $d"
done

FORBIDDEN=(
  'Second Brain'
  'second-brain'
  'docs_manual_gen'
  'PLAN_SECOND_BRAIN'
  'portuguese-learn'
  'gcp_pmle'
)
for s in "${FORBIDDEN[@]}"; do
  if rg -q --fixed-strings "$s" references assets --glob '!scripts/check-seed-kit.sh' 2>/dev/null; then
    fail "forbidden string in kit: $s"
  fi
done

rg -q 'seed_grow/' references/EXECUTE_GEN.md references/ANALYZE_SPECIFIC.md || fail 'EXECUTE_GEN or ANALYZE_SPECIFIC must name seed_grow/'
rg -q 'must not create or edit' references/EXECUTE_GEN.md || rg -q 'read-only' references/EXECUTE_GEN.md || fail 'EXECUTE_GEN must forbid kit edits'
rg -q 'seed_grow/' SKILL.md || fail 'SKILL.md must name seed_grow/'
rg -q 'Do not' SKILL.md || rg -q 'read-only' SKILL.md || fail 'SKILL.md must forbid skill tree edits'

echo "check-seed-kit: OK ($FAB_ROOT)"
