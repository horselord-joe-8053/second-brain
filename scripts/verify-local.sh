#!/usr/bin/env bash
# Corpus + harness smoke (Second Brain). Invoked from scripts/verify.sh when present.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [[ "${RUN_BRAIN_SETUP:-0}" == "1" ]] && [[ -x "$ROOT/scripts/brain/setup-local.sh" ]]; then
  bash "$ROOT/scripts/brain/setup-local.sh"
elif [[ "${RUN_BRAIN_ACCEPTANCE:-0}" == "1" ]] && [[ -x "$ROOT/scripts/brain/adapters/hermes/acceptance-automated.sh" ]]; then
  bash "$ROOT/scripts/brain/adapters/hermes/acceptance-automated.sh"
fi

echo "== second-brain: brain/ layout =="
test -d "$ROOT/brain/raw/sources"
test -d "$ROOT/brain/wiki"
test -d "$ROOT/brain/manifests"
test -f "$ROOT/brain/purpose.md"

echo "== second-brain: harness stub =="
test -f "$ROOT/harness/second-brain/README.md"

if "$ROOT/scripts/py" -c "pass" >/dev/null 2>&1; then
  export PYTHONPATH="${ROOT}/scripts/retail${PYTHONPATH:+:$PYTHONPATH}"
  for _prof in data_60_10 data_1000_100; do
    _dir="$ROOT/scripts/retail/sim_data/profiles/$_prof"
    if [[ -f "$_dir/service_queries.csv" ]]; then
      echo "== retail: validate llm_gen corpus ($_prof) =="
      "$ROOT/scripts/py" "$ROOT/scripts/retail/seed/validate_llm_corpus.py" --corpus-dir "$_dir"
    fi
  done
fi

if [[ -d "$ROOT/tests" ]] && "$ROOT/scripts/py" -c "pass" >/dev/null 2>&1; then
  echo "== second-brain: pytest =="
  export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"
  "$ROOT/scripts/py" -m pytest -q tests/test_second_brain_corpus.py 2>/dev/null || "$ROOT/scripts/py" -m pytest -q tests/
elif [[ -d "$ROOT/tests" ]]; then
  echo "verify-local: skip pytest (Python 3.12 unavailable)"
fi

if ! command -v hermes >/dev/null 2>&1; then
  echo "verify-local: hint — RUN_BRAIN_SETUP=1 ./scripts/verify-local.sh or ./scripts/brain/setup-local.sh"
fi

echo "verify-local.sh: passed"
