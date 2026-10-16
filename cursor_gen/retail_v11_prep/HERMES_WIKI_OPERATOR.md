<h1 id="hermes-wiki-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Hermes operator — FRU fridge manuals (LLM Wiki)</h1>

**Audience:** Hermes Desktop (human paste or Hermes session). **Ticket A/B** stays on Cursor — [`CURSOR_PREP_RUNBOOK.md`](./CURSOR_PREP_RUNBOOK.md).

<h2 id="hermes-wiki-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Prerequisites](#1-prereq) — ``.txt`` manuals in raw; PDFs in archive.
2. [Hermes steps](#2-steps) — project, rescan, smoke.
3. [Prompt block](#3-prompt) — copy-paste for Hermes.

---

<h2 id="1-prereq" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Prerequisites</h2>

Expect **``.txt``** under `brain/retail/raw/sources/fridge-docs/<sku>/` (built by `scripts/retail/manuals/build_pdf_txt_and_page_idx.py`). PDFs are under **`brain/retail/archive/fridge-docs/`** only — not Source Watch.

<h2 id="2-steps" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Hermes steps</h2>

1. LLM Wiki app running (`127.0.0.1:19828`).
2. **`llm_wiki_set_project`** → `/Users/jjw8053/projects/second_brain/brain/retail`
3. Rescan / ingest sources → compiled pages under `brain/retail/wiki/`.
4. **`llm_wiki_search`:** e.g. `RF28K9070SG ice maker not making ice`
5. **`llm_wiki_read_file`** on one hit under `brain/retail/wiki/`.
6. Install **`query-retail-brain`** skill on Hermes if missing.
7. Check one compiled source page keeps frontmatter **`sources: ["fridge-docs/<sku>/<guide>.txt"]`** — the answer bundle cites **`doc_path`**. Then smoke from the repo:
   `scripts/py scripts/retail/answer/answer_ticket.py --query "RF28K9070SG ice maker not making ice" --md` → expect a manual hit `(via wiki …)`.

**Profiles:** `brain/retail` is the default brain-profile; the personal brain is a separate LLM Wiki project at `brain/personal` (see runbook §2.1). **Duplicates:** GE and KitchenAid `repair-guide.pdf` are byte-identical copies of their `user-guide.pdf` (the page index flags them `duplicate_of`); compiling them twice only duplicates wiki pages.

**Do not** load Postgres from Hermes.

<h2 id="2-1-hg-txt-3" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.1 HG-TXT-3 — after English ``.txt`` trim (P18)</h2>

See [`docs_manual_gen/artifacts/RETAIL_LLM_WIKI_TXT_COMPILE.md`](../../docs_manual_gen/artifacts/RETAIL_LLM_WIKI_TXT_COMPILE.md).

1. Set LLM Wiki project **Output language → English** (not auto).
2. Remove the source row from `brain/retail/.llm-wiki/ingest-cache.json` for the manual you are recompiling.
3. Delete thin `wiki/sources/*repair-guide*` (and optional entity stubs) if re-ingest should replace them.
4. `POST …/sources/rescan`; wait for ingest queue idle.
5. Accept when **`type: source`** body includes **English procedural** text (error codes, ice maker), not only entity blurbs; optional: `RUN_RETAIL_E2E=1` shows **`manual_hit_sources.wiki > 0`**.

<h2 id="3-prompt" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Prompt block</h2>

```text
You are on my Mac helping finish FRU US retail wiki prep. Repo: /Users/jjw8053/projects/second_brain.

1. LLM Wiki running (127.0.0.1:19828).
2. llm_wiki_set_project → /Users/jjw8053/projects/second_brain/brain/retail
3. Verify ``.txt`` under brain/retail/raw/sources/fridge-docs/{samsung_RF28K9070SG,ge_GNE27JYMFS,kitchenaid_KRFF507HPS}/.
4. Rescan / ingest until ``.txt`` files compile into brain/retail/wiki/.
5. llm_wiki_search: "ice maker stopped producing cubes RF28K9070SG" — then llm_wiki_read_file on one wiki path.
6. Do NOT run Docker or Postgres scripts.

Stop with: project path set, rescan done, one search + read succeeded.
```

Legacy monolith prompt: [`HERMES_PREP_PROMPT.md`](./HERMES_PREP_PROMPT.md) (Samsung paths — deprecated).
