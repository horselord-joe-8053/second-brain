#!/usr/bin/env bash
# Fail if bootstrap_seed/ contains product-specific paths or forbidden strings (kit purity gate).
set -euo pipefail

KIT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$KIT"

fail() { echo "check-seed-kit: $1" >&2; exit 1; }

for d in specific modules/second-brain utils/pglpl_cert utils/chatgpt/transcripts; do
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
  if rg -q --fixed-strings "$s" . --glob '!core/scripts/check-seed-kit.sh' 2>/dev/null; then
    fail "forbidden string in kit: $s"
  fi
done

rg -q 'seed_grow/' EXECUTE_GEN.md ANALYZE_SPECIFIC.md || fail 'EXECUTE_GEN or ANALYZE_SPECIFIC must name seed_grow/'
rg -q 'must not create or edit' EXECUTE_GEN.md || rg -q 'read-only' EXECUTE_GEN.md || fail 'EXECUTE_GEN must forbid kit edits'

echo "check-seed-kit: OK ($KIT)"
