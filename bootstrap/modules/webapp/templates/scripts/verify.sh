#!/usr/bin/env bash
# Canonical verify gate for factory-scaffolded apps (copy to repo scripts/verify.sh).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== ac-test mapping =="
python3 "$ROOT/scripts/check-ac-tests.py"

echo "== tdd pairing (optional PR gate) =="
bash "$ROOT/scripts/check-tdd-pairing.sh"

echo "== backend: ruff =="
cd backend
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -e ".[dev]"
ruff check app tests
echo "== backend: pytest =="
# Repo root on PYTHONPATH so tests can import utils.neat_logger.
export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"
pytest -q
cd "$ROOT"

echo "== frontend: typecheck =="
cd frontend
if [[ ! -d node_modules ]]; then
  npm ci
fi
npm run typecheck
echo "== frontend: vitest =="
npm run test
cd "$ROOT"

echo "verify.sh: all checks passed"
