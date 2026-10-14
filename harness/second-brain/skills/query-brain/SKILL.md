---
name: query-brain
description: Query compiled brain via Nashsu MCP (wiki-first, L2 escalation, cite or abstain).
---

# query-brain (HERMES-3)

## Preflight

1. **`local-llm-wiki`**: `./scripts/brain/llm-wiki.sh status`. If it prints `llm-wiki: down`, run `start`. If it prints `token refreshed`, ask for a new Hermes session before searching.
2. Project **`…/second_brain/brain`** current, or `llm_wiki_set_project`.
3. MCP: `llm_wiki_status`, then `llm_wiki_set_project` with the absolute brain path if needed.

## Pattern A (default — auditable)

1. `llm_wiki_search` with user question (hybrid over **`wiki/`**).
2. `llm_wiki_read_file` on top **`wiki/…`** paths.
3. Synthesize answer with **citations** (`wiki/…` paths).
4. **Evidence-critical** (tables, dates, legal): if wiki summary insufficient, read L2 extract  
   `raw/sources/**/.cache/*.txt` via `second_brain_fs` MCP or allowed file read — see MORE §9.
5. **Cite or abstain** — do not answer from parametric knowledge when corpus lacks evidence (MORE §10 G6).

## Pattern B (quick)

- `llm_wiki_chat` — Nashsu Agent may call internal `source.search`; fewer intermediate steps.

## Do not

- Reimplement BM25/LanceDB in this repo.
- Use bundled Hermes **`llm-wiki`** compiler skill (disabled in Hermes config for Second Brain).

Reference: [`docs_manual_gen/MORE_SECOND_BRAIN_QUERY_HERMES_MCP.md`](../../../../docs_manual_gen/MORE_SECOND_BRAIN_QUERY_HERMES_MCP.md).
