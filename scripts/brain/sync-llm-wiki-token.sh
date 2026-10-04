#!/usr/bin/env bash
# Idempotent: read LLM Wiki API bearer from app-state.json → second_brain/.env + ~/.hermes/.env
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
APP_STATE="${LLM_WIKI_APP_STATE:-$HOME/Library/Application Support/com.llmwiki.app/app-state.json}"
ENV_FILE="$ROOT/.env"
HERMES_ENV="${HERMES_HOME:-$HOME/.hermes}/.env"

if [[ ! -f "$APP_STATE" ]]; then
  echo "sync-llm-wiki-token: no app-state at $APP_STATE (open LLM Wiki and save API + MCP settings)"
  exit 1
fi

export APP_STATE
TOKEN="$(python3 - <<'PY'
import json, os, sys
path = os.environ["APP_STATE"]
with open(path, encoding="utf-8") as f:
    data = json.load(f)
token = (data.get("apiConfig") or {}).get("token") or ""
token = token.strip()
if not token:
    sys.exit(1)
print(token)
PY
)"

upsert_env() {
  local file="$1"
  local key="LLM_WIKI_API_TOKEN"
  mkdir -p "$(dirname "$file")"
  touch "$file"
  if grep -q "^${key}=" "$file" 2>/dev/null; then
    TOKEN="$TOKEN" KEY="$key" FILE="$file" python3 - <<'PY'
import os
from pathlib import Path
p = Path(os.environ["FILE"])
key = os.environ["KEY"]
token = os.environ["TOKEN"]
lines = p.read_text(encoding="utf-8").splitlines()
out = []
done = False
for line in lines:
    if line.startswith(f"{key}="):
        out.append(f"{key}={token}")
        done = True
    else:
        out.append(line)
if not done:
    out.append(f"{key}={token}")
p.write_text("\n".join(out) + "\n", encoding="utf-8")
PY
  else
    echo "${key}=${TOKEN}" >> "$file"
  fi
}

upsert_env "$ENV_FILE"
upsert_env "$HERMES_ENV"
echo "sync-llm-wiki-token: updated LLM_WIKI_API_TOKEN in .env and ~/.hermes/.env (token not printed)"
