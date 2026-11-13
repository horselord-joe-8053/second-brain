#!/usr/bin/env bash
# Internal delegate — stop Hermes. Operators: ../../agent.sh stop
set -euo pipefail
HERMES_AD="$(cd "$(dirname "$0")" && pwd)"
exec bash "$HERMES_AD/stop-hermes.sh" "$@"
