# Acceptance checklist — second-brain-hermes-v1 (HG-8)

Manual run with LLM Wiki + Hermes up. Tick in **Decisions** or plan P8.

1. [ ] `brain/wiki/` has compiled pages beyond `index.md` only.
2. [ ] `./scripts/brain/setup-local.sh` exits 0 (Hermes + MCP + token sync when app-state present).
3. [ ] `./scripts/brain/mcp-smoke-read.sh` returns content for smoke-test source page.
4. [ ] Hermes `mcp list` or config shows `llm_wiki` + `second_brain_fs`; bundled **`llm-wiki`** skill disabled.
5. [ ] Obsidian vault opened on **`…/second_brain/brain/wiki`** (HG-5).
6. [ ] **NB-SB1:** Table lookup cites L2 or L3 path (or waiver with reason).

Automated seams: `./scripts/verify.sh`, `./scripts/verify-local.sh`, pytest `tests/test_second_brain_corpus.py`.
