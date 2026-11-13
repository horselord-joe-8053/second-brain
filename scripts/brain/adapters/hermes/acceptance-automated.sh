#!/usr/bin/env bash
# HG-8 automated seams (P8): wiki corpus, MCP smoke, Hermes MCP list + skills config.
set -euo pipefail

HERMES_AD="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERMES_AD/../../../.." && pwd)"
export PATH="${HOME}/.local/bin:${HOME}/.hermes/hermes-agent:${PATH}"

fail() {
  echo "acceptance-automated: FAIL — $*" >&2
  exit 1
}

# shellcheck source=scripts/brain/brain-profile-env.sh
source "$ROOT/scripts/brain/brain-profile-env.sh"
echo "== acceptance-automated (HG-8 automated items; profile ${BRAIN_PROFILE}) =="

wiki_count="$(find "$SECOND_BRAIN_WIKI_VAULT" -name '*.md' ! -path '*/.obsidian/*' 2>/dev/null | wc -l | tr -d ' ')"
if [[ "$wiki_count" -lt 2 ]]; then
  fail "${SECOND_BRAIN_WIKI_VAULT} needs compiled pages beyond index.md (found ${wiki_count} *.md)"
fi
echo "acceptance-automated: [1/4] wiki pages OK (${wiki_count} *.md under ${SECOND_BRAIN_WIKI_VAULT})"

bash "$HERMES_AD/setup-hermes-mcp.sh"
echo "acceptance-automated: [2/4] setup-hermes-mcp + mcp-smoke-read OK"

command -v hermes >/dev/null 2>&1 || fail "hermes not on PATH — run $HERMES_AD/setup-hermes.sh"

mcp_list="$(hermes mcp list 2>&1)" || fail "hermes mcp list failed: ${mcp_list}"
echo "$mcp_list" | grep -q llm_wiki || fail "hermes mcp list missing llm_wiki"
echo "$mcp_list" | grep -q second_brain_fs || fail "hermes mcp list missing second_brain_fs"
echo "acceptance-automated: [3/4] hermes mcp list shows llm_wiki + second_brain_fs"

HERMES_CFG="${HOME}/.hermes/config.yaml"
[[ -f "$HERMES_CFG" ]] || fail "missing ${HERMES_CFG}"
grep -q '    - llm-wiki' "$HERMES_CFG" || fail "skills.disabled must include llm-wiki (run setup-hermes-skills.sh)"
echo "acceptance-automated: llm-wiki in skills.disabled OK"

if hermes mcp test llm_wiki >/dev/null 2>&1; then
  echo "acceptance-automated: hermes mcp test llm_wiki OK"
else
  echo "acceptance-automated: hermes mcp test llm_wiki skipped or failed (MCP merged; retry with LLM Wiki running)"
fi

echo "acceptance-automated: [4/4] Hermes config + MCP OK"

if [[ "$BRAIN_PROFILE" == "personal" ]]; then
  bash "$ROOT/scripts/brain/nb-sb1-probe.sh"
  echo "acceptance-automated: [5/5] NB-SB1 search API cites L3 james source"
else
  echo "acceptance-automated: [5/5] NB-SB1 probe skipped (personal-profile corpus; BRAIN_PROFILE=${BRAIN_PROFILE})"
fi

echo ""
echo "Manual P8 (see docs/ACCEPTANCE-second-brain-hermes-v1.md):"
echo "  • Obsidian vault on ${SECOND_BRAIN_WIKI_VAULT} (HG-5)"
echo "  • Hermes Desktop smoke — RUNBOOK_HARNESS_HERMES.md §4"
echo "acceptance-automated: OK"
