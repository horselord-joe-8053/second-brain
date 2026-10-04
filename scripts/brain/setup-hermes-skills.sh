#!/usr/bin/env bash
# P4: disable bundled Hermes llm-wiki compiler skill; load repo harness skills via external_dirs.
# Nashsu hub install may be blocked by skills-guard (localhost API refs) — repo skills substitute.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PATH="${HOME}/.local/bin:${PATH}"

python3 "$ROOT/scripts/brain/merge-hermes-skills-config.py"

if command -v hermes >/dev/null 2>&1; then
  if hermes skills list 2>/dev/null | grep -q "llm-wiki"; then
    echo "setup-hermes-skills: verify 'llm-wiki' disabled in config (bundled may still list; agent should skip disabled)"
  fi
fi

echo "setup-hermes-skills: repo skills under harness/second-brain/skills (ingest-to-brain, query-brain, nashsu-mcp-read)"
echo "setup-hermes-skills: optional hub install when guard allows:"
echo "  hermes skills install skills-sh/nashsu/llm_wiki_skill/llm-wiki --yes"
