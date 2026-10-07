#!/usr/bin/env bash
# Automated preflight + copy-paste prompts for Hermes Desktop integrated smoke (Second Brain).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
# shellcheck source=scripts/brain/hermes-env.sh
source "$(dirname "$0")/hermes-env.sh"

BRAIN="$(python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('$ROOT') / 'scripts' / 'brain'))
from brain_stack import load_brain_stack
print(load_brain_stack(Path('$ROOT'))['paths']['brain_root'])
")"

echo "== smoke-integrated: automated preflight =="
bash "$ROOT/scripts/brain/acceptance-automated.sh"

cat <<EOF

== smoke-integrated: Hermes Desktop (manual — you have Desktop open) ==

Preflight (you):
  • LLM Wiki running — project folder: ${BRAIN}
  • Hermes Desktop — Gateway ready (green, sidebar footer)
  • Capabilities → MCP: llm_wiki + second_brain_fs listed (reload MCP if needed)

Prompt 1 — wiki smoke (Pattern A):
  Use LLM Wiki MCP only. llm_wiki_set_project for ${BRAIN}.
  llm_wiki_search for "smoke test", read the top wiki/ path, summarize with citations.
  Do not use web search.

Pass: tool calls include llm_wiki_*; answer cites wiki/sources/7-uploads--10-smoke-test--1dwb8eh.md or similar.

Prompt 2 — NB-SB1 table corpus:
  Same project. Search for James conjugation verb table, read wiki page, answer with wiki/ path citation.

Pass: cites wiki/sources/7-uploads--46-james-homemade-conjugation-notes-o-2026-verb-a--e9m6g0 or abstains.

Prompt 3 — compiler boundary:
  Where should new uploads go for Second Brain ingest? Confirm you will not edit brain/wiki/ directly as compiler.

Pass: mentions raw/sources/uploads and LLM Wiki ingest, not Hermes rewriting wiki.

Optional: enable skill query-brain in session and repeat Prompt 1.

EOF
