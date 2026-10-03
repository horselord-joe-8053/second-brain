#!/usr/bin/env bash
# Corpus + harness smoke (Second Brain). Invoked from scripts/verify.sh when present.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "== second-brain: brain/ layout =="
test -d "$ROOT/brain/raw/sources"
test -d "$ROOT/brain/wiki"
test -d "$ROOT/brain/manifests"
test -f "$ROOT/brain/purpose.md"

echo "== second-brain: harness stub =="
test -f "$ROOT/harness/second-brain/README.md"

if [[ -d "$ROOT/tests" ]] && python3 -c "pass" >/dev/null 2>&1; then
  echo "== second-brain: pytest =="
  export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"
  python3 -m pytest -q tests/test_second_brain_corpus.py 2>/dev/null || python3 -m pytest -q tests/
elif [[ -d "$ROOT/tests" ]]; then
  echo "verify-local: skip pytest (python3 unavailable)"
fi

echo "verify-local.sh: passed"
