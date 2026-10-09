#!/usr/bin/env bash
# Merge skills.disabled + external_dirs for Second Brain contract skills.
set -euo pipefail

HERMES_AD="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERMES_AD/../../../.." && pwd)"

python3 "$HERMES_AD/merge-hermes-skills-config.py"

echo "setup-hermes-skills: OK (see merge-hermes-skills-config output)"
