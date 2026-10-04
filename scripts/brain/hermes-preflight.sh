#!/usr/bin/env bash
# P3 gate: idempotent Hermes install + doctor (wrapper for setup-hermes.sh).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
exec bash "$ROOT/scripts/brain/setup-hermes.sh"
