#!/usr/bin/env bash
set -euo pipefail
HERMES_AD="$(cd "$(dirname "$0")" && pwd)"
exec bash "$HERMES_AD/setup-hermes.sh"
