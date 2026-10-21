<h1 id="rlfc-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Retail learned lane — full-copy + service-manual operator notes</h1>

**Plan:** [`REFACTOR_LEARNED_SECTION_COPY_PLUS_CARDS.md`](../ref_plan/new/REFACTOR_LEARNED_SECTION_COPY_PLUS_CARDS.md) (P6). **App repo:** `nu_llm_wiki`.

<h2 id="rlfc-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Source Watch settings](#rlfc-settings) — UI labels and values.
2. [External shards](#rlfc-shards) — Prompt C v4 + raw tree.
3. [Artifacts](#rlfc-artifacts) — diagnosis and benchmark links.
4. [Operator checklist](#rlfc-checklist) — re-ingest lane D.

---

<h2 id="rlfc-settings" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Source Watch settings</h2>

Configure in LLM Wiki **Source Watch** for project `brain/retail-md-learned` (UI-only until brain config is committed):

| Setting | Value | Meaning |
|---------|--------|---------|
| **Source page mode** | `full-copy` | One raw `.md` shard → one `wiki/sources/*.md` page (bytes + frontmatter); no LLM summary for the source page. |
| **Ingest profile** | `service-manual` | Step 2 is **cards-only** from the raw shard; knowledge-unit / entity rules apply; stray `wiki/sources/` FILE blocks from the model are dropped. |

Default modes remain `summary` + `default` for other retail lane projects unless you intentionally match lane D.

---

<h2 id="rlfc-shards" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. External shards</h2>

| Item | Path |
|------|------|
| **Prompt C v4** (coarse split, 4–10 parts per PDF) | `brain/retail/archive/fridge_prompts_pdf_or_zip_updated/Prompt_C_v4_split.md` |
| **Legacy v3** (one `##` → one file; very large shard count) | `Prompt_C_v3_split.md` (same folder) |
| **Operator raw tree (split-less / v4)** | `brain/retail-md-learned/raw/sources/fridge-docs-split-less/` |

Replace raw shards when PDFs change; re-ingest so wiki source pages and cards refresh.

---

<h2 id="rlfc-artifacts" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Artifacts</h2>

| Doc | Role |
|-----|------|
| [`LEARNED_MD_VS_TXT_WIKI_SEARCH.md`](./LEARNED_MD_VS_TXT_WIKI_SEARCH.md) | Why thin wiki hurt search before full-copy |
| [`REFACTOR_RETAIL_MANUAL_INGEST_ABCD_BENCHMARK.md`](../ref_plan/new/REFACTOR_RETAIL_MANUAL_INGEST_ABCD_BENCHMARK.md) | Lane A–D automated QA after ingest |
| [`tests/retail_multi_profiles/README.md`](../../tests/retail_multi_profiles/README.md) | Harness layout (when implemented) |

---

<h2 id="rlfc-checklist" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Operator checklist</h2>

1. LLM Wiki running; open project path `…/brain/retail-md-learned`.
2. Source Watch: **full-copy** + **service-manual**.
3. Confirm raw shards under `raw/sources/` (v4 / split-less tree).
4. Run rescan / ingest; wait for queue to finish.
5. Optional: remove stale wiki pages if raw files were deleted (automatic orphan cleanup is plan **P5** in `nu_llm_wiki` — operator may delete orphans manually until that ships).
