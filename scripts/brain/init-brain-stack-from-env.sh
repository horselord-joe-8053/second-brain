#!/usr/bin/env bash
# One-time: create gitignored config/brain-stack.yaml from example + import repo .env into secrets:
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOCAL="$ROOT/config/brain-stack.yaml"
EXAMPLE="$ROOT/config/brain-stack.example.yaml"

if [[ ! -f "$EXAMPLE" ]]; then
  echo "init-brain-stack-from-env: missing $EXAMPLE"
  exit 1
fi

if [[ ! -f "$LOCAL" ]]; then
  cp "$EXAMPLE" "$LOCAL"
  echo "secrets:" >> "$LOCAL"
  echo "init-brain-stack-from-env: copied example (includes active_harness for agent.sh)"
fi

if [[ ! -f "$ROOT/.env" ]]; then
  echo "init-brain-stack-from-env: no .env to import"
  exit 0
fi

"$ROOT/scripts/py" - <<'PY' "$ROOT"
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]) / "scripts" / "brain"))
from brain_stack import _read_env_map, load_brain_stack, upsert_stack_secret

repo = Path(sys.argv[1])
stack = load_brain_stack(repo)
keys = stack.get("hermes", {}).get("sync_env_keys") or []
env = _read_env_map(repo / ".env")
for k in keys:
    if env.get(k):
        upsert_stack_secret(repo, k, env[k])
print(f"init-brain-stack-from-env: imported {sum(1 for k in keys if env.get(k))} key(s) into config/brain-stack.yaml")
PY

echo "init-brain-stack-from-env: edit $LOCAL as your single operator file; re-run apply-stack-config.sh"
