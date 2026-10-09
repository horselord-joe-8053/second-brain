#!/usr/bin/env bash
# Shared PATH and repo root for Hermes wrapper scripts.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
export PATH="${HOME}/.local/bin:${HOME}/.hermes/hermes-agent:${PATH}"
export SECOND_BRAIN_ROOT="$ROOT"

if ! command -v hermes >/dev/null 2>&1; then
  echo "hermes-env: hermes not on PATH — run ./scripts/brain/adapters/hermes/setup-hermes.sh" >&2
  exit 1
fi
