#!/usr/bin/env bash
# Delegates to canonical ops script (see scripts/retail/ops/README.md).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
exec bash "$ROOT/scripts/retail/ops/pg_up_and_load.sh" "$@"
