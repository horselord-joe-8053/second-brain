#!/usr/bin/env bash
# NB-SB1 automated seam: search API returns L3 path for James conjugation corpus (table ingest).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
set -a
# shellcheck source=/dev/null
[[ -f "$ROOT/.env" ]] && source "$ROOT/.env"
set +a
: "${LLM_WIKI_API_TOKEN:?set via sync-llm-wiki-token.sh}"

BASE="${LLM_WIKI_API_BASE_URL:-http://127.0.0.1:19828/api/v1}"
curl -fsS -H "Authorization: Bearer ${LLM_WIKI_API_TOKEN}" -H "Content-Type: application/json" \
  -d '{"query":"james conjugation verb table","topK":8,"includeContent":false}' \
  "${BASE}/projects/current/search" | "$ROOT/scripts/py" -c "
import json, sys
d = json.load(sys.stdin)
paths = [r.get('path', '') for r in d.get('results', [])]
l3 = [p for p in paths if p.startswith('wiki/') and 'james' in p.lower()]
if not l3:
    print('nb-sb1-probe: no L3 james path in search results', file=sys.stderr)
    sys.exit(1)
print('nb-sb1-probe: OK L3', l3[0])
"
