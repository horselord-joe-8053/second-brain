#!/usr/bin/env bash
# Validate config/brain-stack.yaml + .env vs hermes.sync_env_keys (no secret values printed).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PATH="${HOME}/.local/bin:${HOME}/.hermes/hermes-agent:${PATH}"

python3 - <<'PY' "$ROOT"
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]) / "scripts" / "brain"))
from brain_stack import load_brain_stack, verify_stack_config

repo = Path(sys.argv[1])
issues = verify_stack_config(repo)
stack = load_brain_stack(repo)
h = stack.get("hermes") or {}
print("== verify-stack-config ==")
print(f"brain-stack: {repo / 'config' / 'brain-stack.yaml'}")
print(f"chat_provider: {h.get('chat_provider')}")
print(f"chat_model: {h.get('chat_model')}")
print(f"mcp_server_js: {h.get('mcp_server_js')}")
if issues:
    print("ISSUES:")
    for i in issues:
        print(f"  - {i}")
    sys.exit(1)
print("verify-stack-config: OK")
PY

if command -v hermes >/dev/null 2>&1; then
  echo "--- hermes config (model) ---"
  hermes config get model 2>/dev/null || true
fi
