# Acceptance checklist — second-brain-hermes-v1 (HG-8)

Manual run with **LLM Wiki** + **Hermes** up. Tick in **Decisions** or plan P8.

**Automated batch (items 1–4, NB-SB1 API seam):**

```bash
cd /Users/jjw8053/projects/second_brain
export PATH="${HOME}/.local/bin:${HOME}/.hermes/hermes-agent:${PATH}"
./scripts/brain/acceptance-automated.sh
# or:
RUN_BRAIN_ACCEPTANCE=1 ./scripts/brain/setup-local.sh
```

**After reboot:** start LLM Wiki and Obsidian first, then run the script above. Runbook §14.

1. [X] `brain/wiki/` has compiled pages beyond `index.md` only. *(automated — 2026-10-05)*
2. [X] `./scripts/brain/setup-local.sh` exits 0 (Hermes + MCP + token sync when app-state present). *(2026-10-05)*
3. [X] `./scripts/brain/mcp-smoke-read.sh` returns content for smoke-test source page. *(acceptance-automated)*
4. [X] Hermes `mcp list` or config shows `llm_wiki` + `second_brain_fs`; bundled **`llm-wiki`** skill disabled. *(acceptance-automated; `hermes mcp test llm_wiki` OK)*
5. [X] Obsidian vault opened on **`…/second_brain/brain/wiki`** (HG-5).
6. [X] **NB-SB1:** Table lookup cites L2 or L3 path — **`nb-sb1-probe.sh`** → `wiki/sources/7-uploads--46-james-homemade-conjugation-notes-o-2026-verb-a--e9m6g0.md` *(2026-10-05 API search seam)*

**Hermes integration (PLAN §8.4 — optional manual):** start `hermes`, run one MCP search+read prompt — runbook §10.1. Automated substitute: **`hermes mcp test llm_wiki`** (12 tools, connected).

Automated seams: `./scripts/verify.sh`, `./scripts/verify-local.sh`, pytest `tests/test_second_brain_corpus.py`.
