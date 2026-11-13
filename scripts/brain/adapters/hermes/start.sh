#!/usr/bin/env bash
# Internal delegate — start Hermes. Operators: ../../agent.sh start
set -euo pipefail
HERMES_AD="$(cd "$(dirname "$0")" && pwd)"
exec bash "$HERMES_AD/start-hermes.sh" "$@"
