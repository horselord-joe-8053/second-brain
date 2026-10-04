#!/usr/bin/env bash
# P4 smoke: read wiki page content via search API (same backend as llm_wiki_read_file corpus).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
set -a
# shellcheck source=/dev/null
[[ -f "$ROOT/.env" ]] && source "$ROOT/.env"
set +a
: "${LLM_WIKI_API_TOKEN:?set via sync-llm-wiki-token.sh}"

PAGE="${1:-wiki/sources/7-uploads--10-smoke-test--1dwb8eh.md}"
STEM="$(basename "$PAGE" .md)"
BASE="${LLM_WIKI_API_BASE_URL:-http://127.0.0.1:19828/api/v1}"
export TARGET="$PAGE"

curl -fsS -H "Authorization: Bearer ${LLM_WIKI_API_TOKEN}" -H "Content-Type: application/json" \
  -d "{\"query\":\"${STEM}\",\"topK\":5,\"includeContent\":true}" \
  "${BASE}/projects/current/search" | python3 -c "
import json,sys,os
target=os.environ['TARGET']
d=json.load(sys.stdin)
for r in d.get('results',[]):
    if r.get('path')==target and (r.get('content') or ''):
        print('mcp-smoke-read: OK', target, 'bytes', len(r['content']))
        sys.exit(0)
print('mcp-smoke-read: no content for', target, file=sys.stderr)
sys.exit(1)
"
