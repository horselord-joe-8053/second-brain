#!/usr/bin/env bash
# Legacy name — runs three-mode ABC (V1 / V1.1 / V1.2).
set -euo pipefail
PREP_DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$PREP_DIR/05_run_abc_postgres.sh"
