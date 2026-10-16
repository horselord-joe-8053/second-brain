<h1 id="doc-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Retail LLM Wiki compile from fridge ``.txt`` manuals</h1>

**Status:** analysis + operator gates (**HG-TXT-3**) — ties to brain-profiles **P19** and **`nu_llm_wiki`** ingest in [`/Users/jjw8053/projects/nu_llm_wiki`](../../../projects/nu_llm_wiki).

<h2 id="outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Symptom](#symptom) — thin repair-guide wiki vs rich ``.txt``.
2. [Ingest pipeline (two LLM stages)](#pipeline) — what is sent to the model.
3. [Why personal uploads looked fine](#personal) — tables vs summaries.
4. [Why retail manuals fail manual-leg wiki hits](#retail-fail) — relevance + language.
5. [Force re-ingest](#force) — cache bust + rescan.
6. [Recommended fixes](#fixes) — Second Brain vs **nu_llm_wiki**.

---

<h2 id="symptom" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Symptom</h2>

Example: [`brain/retail/wiki/sources/11-fridge-docs--18-samsungrf28k9070sg--12-repair-guide--16k4klu.md`](../../brain/retail/wiki/sources/11-fridge-docs--18-samsungrf28k9070sg--12-repair-guide--16k4klu.md) vs [`repair-guide.txt`](../../brain/retail/raw/sources/fridge-docs/samsung_RF28K9070SG/repair-guide.txt) (~16k chars).

| Observation | Before forced re-ingest | After cache bust + rescan (2026-10-16, `logs/ops/bp_p19_repair_guide_reingest.log`) |
|-------------|-------------------------|-------------------------------------------------------------------------------------|
| Source page size | Large blob with inlined `---FILE:` stubs | ~1.4k — **no** nested FILE markers in body |
| Language | Often French/Romanian summaries | **English** marketing-style bullets |
| Procedural content | Missing | **Still missing** — no error-code table, no “ice maker does not make ice” symptom rows |
| Entity fan-out | Many stub pages in one response | Separate `wiki/concepts/diagnostic-mode.md`, `error-codes.md`, etc. (still thin) |

Live E2E: **`manual_hit_sources.wiki == 0`**, **`raw_txt`** carries manual gold — **unchanged** after re-ingest; compile shape improved but **HG-TXT-3** acceptance (English procedural excerpts in `type: source`) **not met**.

---

<h2 id="pipeline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Ingest pipeline (two LLM stages)</h2>

Implementation: **`nu_llm_wiki/src/lib/ingest.ts`**.

| Stage | Function | Model input (aggregated) |
|-------|----------|---------------------------|
| **1 — Analysis** | `buildAnalysisPrompt(purpose, index, sourceContent, schema)` | System-style user message: “expert research analyst”; sections **Key Entities**, **Key Concepts**, **Main Arguments**, **Recommendations**; **`languageRule(sourceContent)`** (Settings → output language, or auto-detect from source); optional **Wiki Purpose**, **Current Wiki Index**, **Project Schema**. **Full source text** is appended for the chat call (chunked when &gt; budget). |
| **2 — Generation** | `buildGenerationPrompt(...)` | “Wiki maintainer”; must emit `---FILE: wiki/...---` blocks: **(1)** source summary at `wiki/sources/...`, **(2)** entity/concept pages from analysis; **`sources: ["fridge-docs/.../repair-guide.txt"]`** in frontmatter; **`languageRule`** repeated at end. Parser: `parseFileBlocks()`. |

**Not** “embed the PDF.” The model **never** receives a request to copy procedural sections verbatim into the source summary unless the analysis stage emphasized them and generation prompt rules apply (DDL/tables verbatim — appliance prose is usually paraphrased).

**Entity fan-out:** Analysis asks for entities with “standalone-page significance”; generation creates **entity + concept** FILE blocks. Small repair PDFs still produce Diagnostic Mode, Error Codes, etc., with **one-paragraph** bodies — hence useless search snippets for “ice maker not making ice.”

---

<h2 id="personal" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Why personal uploads looked fine</h2>

| Source | Compile result |
|--------|----------------|
| [`brain/personal/wiki/sources/7-uploads--46-james-homemade-conjugation-notes-o-2026-verb-a--e9m6g0.md`](../../brain/personal/wiki/sources/7-uploads--46-james-homemade-conjugation-notes-o-2026-verb-a--e9m6g0.md) | **Markdown tables** preserved — dense, searchable tokens |
| Slide / election uploads | Long narrative sections survive in wiki body |
| Retail fridge ``.txt`` | **Summary + entity graph**; body often **non-English** when `outputLanguage: auto` tracks mixed or wrong detect |

---

<h2 id="retail-fail" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Why retail manuals fail manual-leg wiki hits</h2>

Second Brain **`answer_manuals._wiki_hits`** requires:

1. Frontmatter `sources:` under the SKU’s `fridge-docs/<sku>/…`.
2. **Token overlap** between ticket query and **wiki page body** ≥ **0.34**.

Thin summaries / wrong language → “wiki returned 10 page(s) but none relevant.” **`raw_txt`** on committed English ``.txt`` (after **P18** trim) remains the reliable leg until wiki bodies improve.

---

<h2 id="force" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Force re-ingest (operator)</h2>

1. Rebuild raw English: `scripts/py scripts/retail/manuals/build_pdf_txt_and_page_idx.py`
2. Remove cache row for the source in `brain/retail/.llm-wiki/ingest-cache.json` (key e.g. `fridge-docs/samsung_RF28K9070SG/repair-guide.txt`).
3. Optional: delete stale `wiki/sources/11-fridge-docs--18-samsungrf28k9070sg--12-repair-guide--16k4klu.md` and dependent entity stubs (HG-TXT-1).
4. LLM Wiki app running; `POST /api/v1/projects/{id}/sources/rescan` (see [`SECOND_BRAIN_RUNBOOK.md`](../SECOND_BRAIN_RUNBOOK.md) §8.4).
5. Poll `.llm-wiki/ingest-queue.json` until idle; read compiled source page; smoke `llm_wiki_search` + live E2E.

**Note:** Re-ingest **without** product changes often reproduces the same summary shape — fixes are in **§6**.

---

<h2 id="fixes" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Recommended fixes</h2>

<h3 id="fixes-sb" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">6.1 Second Brain (done / in progress)</h3>

- **P18** — English-only ``.txt`` via [`multilingual_trim.py`](../../scripts/retail/manuals/multilingual_trim.py).
- Keep **`raw_txt`** fallback (E14) — do not block shipping on wiki quality.
- **HG-TXT-3** acceptance: source summary contains **English procedural** excerpts (error codes, ice maker) matching a smoke query.

<h3 id="fixes-settings" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">6.2 LLM Wiki settings (no code)</h3>

- Set project **Output language** to **English** (not **auto**) for `brain/retail` — avoids French/Romanian summaries when auto mis-detects.
- Re-run rescan after **P18** corpus refresh.

<h3 id="fixes-nu" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">6.3 nu_llm_wiki product (if wiki leg must carry gold)</h3>

| Idea | Where | Rationale |
|------|--------|-----------|
| **Manual / appliance profile** | `buildGenerationPrompt` + schema for `brain/retail` | Source summary must include **verbatim excerpts** (symptom tables, error code lists, numbered steps) in fenced blocks; cap entity pages for service manuals |
| **Skip entity FILE blocks** for `raw/sources/fridge-docs/**` | ingest routing | One **`type: source`** page with chunked ## sections from ``.txt`` beats nine entity blurbs |
| **Pass-through mode** | new ingest mode for `.txt` | Split ``.txt`` on headings → wiki sections without LLM summarization (embed those chunks) |
| **Retail schema.md** in prompt | already injected | Add explicit types: `procedure`, `symptom_table`; route to `wiki/manuals/` |
| **Fix inlined `---FILE:` in one blob** | parser / generation QA | Repair-guide page should not contain unparsed nested FILE markers — generation or merge bug |

Until then, **FRU demo narrative** = Postgres tickets + **`raw_txt`** manuals; wiki is optional enrichment.
