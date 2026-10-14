<h1 id="hermes-wiki-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Hermes operator — FRU fridge manuals (LLM Wiki)</h1>

**Audience:** Hermes Desktop (human paste or Hermes session). **Ticket A/B** stays on Cursor — [`CURSOR_PREP_RUNBOOK.md`](./CURSOR_PREP_RUNBOOK.md).

<h2 id="hermes-wiki-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Prerequisites](#1-prereq) — PDFs on disk.
2. [Hermes steps](#2-steps) — project, rescan, smoke.
3. [Prompt block](#3-prompt) — copy-paste for Hermes.

---

<h2 id="1-prereq" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Prerequisites</h2>

Run `01_copy_manuals.sh` first. Expect **6 PDFs** under:

- `brain/retail/raw/sources/fridge-docs/samsung_RF28K9070SG/`
- `brain/retail/raw/sources/fridge-docs/ge_GNE27JYMFS/`
- `brain/retail/raw/sources/fridge-docs/kitchenaid_KRFF507HPS/`

<h2 id="2-steps" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Hermes steps</h2>

1. LLM Wiki app running (`127.0.0.1:19828`).
2. **`llm_wiki_set_project`** → `/Users/jjw8053/projects/second_brain/brain/retail`
3. Rescan / ingest sources → compiled pages under `brain/retail/wiki/`.
4. **`llm_wiki_search`:** e.g. `RF28K9070SG ice maker not making ice`
5. **`llm_wiki_read_file`** on one hit under `brain/retail/wiki/`.
6. Install **`query-retail-brain`** skill on Hermes if missing.

**Do not** load Postgres from Hermes.

<h2 id="3-prompt" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Prompt block</h2>

```text
You are on my Mac helping finish FRU US retail wiki prep. Repo: /Users/jjw8053/projects/second_brain.

1. LLM Wiki running (127.0.0.1:19828).
2. llm_wiki_set_project → /Users/jjw8053/projects/second_brain/brain/retail
3. Verify 6 PDFs under brain/retail/raw/sources/fridge-docs/{samsung_RF28K9070SG,ge_GNE27JYMFS,kitchenaid_KRFF507HPS}/ (user-guide.pdf + repair-guide.pdf each).
4. Rescan / ingest until PDFs compile into brain/retail/wiki/.
5. llm_wiki_search: "ice maker stopped producing cubes RF28K9070SG" — then llm_wiki_read_file on one wiki path.
6. Do NOT run Docker or Postgres scripts.

Stop with: project path set, rescan done, one search + read succeeded.
```

Legacy monolith prompt: [`HERMES_PREP_PROMPT.md`](./HERMES_PREP_PROMPT.md) (Samsung paths — deprecated).
