#!/usr/bin/env bash
# General-project verify gate (copy to repo scripts/verify.sh).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python_can_run() {
  "$ROOT/scripts/py" -c "pass" >/dev/null 2>&1
}

echo "== ac-test mapping =="
if [[ -f "$ROOT/scripts/check-ac-tests.py" ]] && python_can_run; then
  "$ROOT/scripts/py" "$ROOT/scripts/check-ac-tests.py"
elif [[ -f "$ROOT/scripts/check-ac-tests.py" ]]; then
  echo "verify: skip check-ac-tests (Python 3.12 unavailable — install it so scripts/py can find it)"
else
  echo "verify: skip check-ac-tests (not seeded)"
fi

echo "== tdd pairing (optional PR gate) =="
if [[ -f "$ROOT/scripts/check-tdd-pairing.sh" ]]; then
  bash "$ROOT/scripts/check-tdd-pairing.sh"
fi

if [[ -d "$ROOT/backend" ]] && [[ -f "$ROOT/backend/pyproject.toml" || -f "$ROOT/backend/setup.py" ]]; then
  echo "== backend: ruff + pytest (optional stack) =="
  cd "$ROOT/backend"
  if [[ ! -d .venv ]]; then
    "$ROOT/scripts/py" -m venv .venv
  fi
  # shellcheck source=/dev/null
  source .venv/bin/activate
  pip install -q -e ".[dev]" 2>/dev/null || pip install -q -e .
  if command -v ruff >/dev/null 2>&1; then
    ruff check app tests 2>/dev/null || ruff check .
  fi
  export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"
  pytest -q
  cd "$ROOT"
fi

if [[ -d "$ROOT/frontend" ]] && [[ -f "$ROOT/frontend/package.json" ]]; then
  echo "== frontend: typecheck + vitest (optional stack) =="
  cd "$ROOT/frontend"
  if [[ ! -d node_modules ]]; then
    npm ci
  fi
  npm run typecheck
  npm run test
  cd "$ROOT"
fi

if [[ -d "$ROOT/tests" ]] && [[ ! -d "$ROOT/backend" ]] && python_can_run; then
  echo "== repo tests/ pytest =="
  export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"
  "$ROOT/scripts/py" -m pytest -q tests
elif [[ -d "$ROOT/tests" ]] && [[ ! -d "$ROOT/backend" ]]; then
  echo "verify: skip pytest (Python 3.12 unavailable)"
fi

if [[ -x "$ROOT/scripts/verify-local.sh" ]]; then
  echo "== project verify-local.sh =="
  bash "$ROOT/scripts/verify-local.sh"
fi

echo "verify.sh: all checks passed"
