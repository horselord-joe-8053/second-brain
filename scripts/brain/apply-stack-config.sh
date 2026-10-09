#!/usr/bin/env bash
# Apply config/brain-stack.yaml: secrets → ~/.hermes/.env (.env fallback only), harness wiring, token sync.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
HERMES_AD="$ROOT/scripts/brain/adapters/hermes"
OPENCLAW_AD="$ROOT/scripts/brain/adapters/openclaw"

if [[ ! -f "$ROOT/config/brain-stack.yaml" ]] && [[ ! -f "$ROOT/config/brain-stack.example.yaml" ]]; then
  echo "apply-stack-config: no stack config under config/ — skip"
  exit 0
fi

echo "== apply-stack-config =="

python3 - <<'PY' "$ROOT"
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / "scripts" / "brain"))
from brain_stack import active_harness, apply_hermes_env, apply_hermes_model_config, load_brain_stack

repo = Path(sys.argv[1])
stack = load_brain_stack(repo)
harness = active_harness(stack)
print(f"apply-stack-config: active_harness={harness}")
if harness == "hermes":
    n = apply_hermes_env(stack, repo)
    if n:
        print(f"apply-stack-config: synced {n} key(s) from stack → ~/.hermes/.env")
    else:
        print("apply-stack-config: no secrets synced (check .env vs sync_env_keys)")
    if os.environ.get("APPLY_STACK_SKIP_MODEL") != "1":
        apply_hermes_model_config(stack)
        h = stack.get("hermes") or {}
        if h.get("chat_provider") or h.get("chat_model"):
            print(
                f"apply-stack-config: hermes model → provider={h.get('chat_provider')} default={h.get('chat_model')}"
            )
    else:
        print("apply-stack-config: skipped hermes model (CLI override via start-hermes.sh)")
elif harness == "openclaw":
    print("apply-stack-config: openclaw harness — Hermes env sync skipped")
PY

if [[ -f "${HOME}/Library/Application Support/com.llmwiki.app/app-state.json" ]]; then
  bash "$ROOT/scripts/brain/sync-llm-wiki-token.sh" || true
fi

export NU_LLM_WIKI_MCP="${NU_LLM_WIKI_MCP:-$ROOT/../nu_llm_wiki/mcp-server/dist/src/index.js}"
if [[ -f "$ROOT/config/brain-stack.yaml" ]] || [[ -f "$ROOT/config/brain-stack.example.yaml" ]]; then
  export NU_LLM_WIKI_MCP="$(python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('$ROOT') / 'scripts' / 'brain'))
from brain_stack import load_brain_stack
print(load_brain_stack(Path('$ROOT'))['hermes']['mcp_server_js'])
")"
fi

# shellcheck source=/dev/null
set -a
[[ -f "$HOME/.hermes/.env" ]] && source "$HOME/.hermes/.env"
[[ -f "$ROOT/.env" ]] && source "$ROOT/.env"
set +a

HARNESS="$(python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('$ROOT') / 'scripts' / 'brain'))
from brain_stack import active_harness, load_brain_stack
print(active_harness(load_brain_stack(Path('$ROOT'))))
")"

case "$HARNESS" in
  hermes)
    python3 "$HERMES_AD/merge-hermes-wiring.py"
    python3 "$HERMES_AD/merge-hermes-skills-config.py"
    ;;
  openclaw)
    if [[ -x "$OPENCLAW_AD/merge-openclaw-wiring.py" ]]; then
      python3 "$OPENCLAW_AD/merge-openclaw-wiring.py"
    else
      echo "apply-stack-config: openclaw merge stub not executable — skip"
    fi
    ;;
  *)
    echo "apply-stack-config: unknown harness '$HARNESS' — skip wiring merge"
    ;;
esac

VAULT="$(python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('$ROOT') / 'scripts' / 'brain'))
from brain_stack import load_brain_stack
print(load_brain_stack(Path('$ROOT')).get('obsidian', {}).get('vault_path', ''))
")"
echo "apply-stack-config: Obsidian vault → ${VAULT}"
echo "apply-stack-config: OK"
