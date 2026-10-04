#!/usr/bin/env bash
# Idempotent P4: sync API token, merge MCP into ~/.hermes/config.yaml, smoke-test API.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PATH="${HOME}/.local/bin:${HOME}/.hermes/hermes-agent:${PATH}"

bash "$ROOT/scripts/brain/sync-llm-wiki-token.sh"

# shellcheck source=/dev/null
set -a
[[ -f "$HOME/.hermes/.env" ]] && source "$HOME/.hermes/.env"
[[ -f "$ROOT/.env" ]] && source "$ROOT/.env"
set +a

if [[ -z "${LLM_WIKI_API_TOKEN:-}" ]]; then
  echo "setup-hermes-mcp: LLM_WIKI_API_TOKEN missing after sync"
  exit 1
fi

MCP_JS="${NU_LLM_WIKI_MCP:-$ROOT/../nu_llm_wiki/mcp-server/dist/src/index.js}"
if [[ ! -f "$MCP_JS" ]]; then
  echo "setup-hermes-mcp: build MCP first: cd ../nu_llm_wiki/mcp-server && npm install && npm run build"
  exit 1
fi

python3 "$ROOT/scripts/brain/merge-hermes-mcp-config.py"

echo "--- LLM Wiki API health ---"
if curl -fsS -H "Authorization: Bearer ${LLM_WIKI_API_TOKEN}" \
  "http://127.0.0.1:19828/api/v1/health" >/dev/null; then
  echo "setup-hermes-mcp: API health OK"
else
  echo "setup-hermes-mcp: API health failed (start LLM Wiki desktop app + enable API)"
  exit 1
fi

if command -v hermes >/dev/null 2>&1; then
  if hermes mcp list 2>/dev/null | grep -q llm_wiki; then
    echo "--- hermes mcp test llm_wiki ---"
    hermes mcp test llm_wiki || echo "setup-hermes-mcp: hermes mcp test skipped/failed (config merged; retry when app is up)"
  else
    echo "setup-hermes-mcp: config merged; run 'hermes mcp list' after restarting Hermes CLI session"
  fi
fi

echo "setup-hermes-mcp: OK"
