<h1 id="bnd-analysis-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">TEST_ANALYSIS — Bundled manual + ticket Q&amp;A (B20)</h1>

**Status:** **EVO-18 (M10)** operator matrix complete (**2026-10-28**). **Promoted manual stack:** `page_heading` ingest + **`page_top5`** + manual **Tantivy**; optional **`RETAIL_D7=decompose`** for compound questions. Best full B20: **`b20-evo18-d7-20261028`** **15/20** judge. Historical six-row PRE-T0 gate **`b20-customer-six-20261027`** was **0/6**; with D2+D7: **`b20-evo18-d7-six-20261028`** **3/6**. Canonical PRE-T0 full-20: **`b20-brand-model-20261027`** **14/20**.

**Artifacts:** targeted `ops/runs/retail-bundled-qa/b20-customer-six-20261027/results.jsonl`; pre-rewrite full baseline `ops/runs/retail-bundled-qa/b20-brand-model-20261027/results.jsonl`.

<h2 id="bnd-analysis-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Setup](#bnd-setup) — legs, k values, gold.
 1.1 [Manual leg source (Lane B)](#bnd-manual-source) — `brain/retail-md` + PG.
2. [Headline metrics](#bnd-headline) — **`b20-brand-model-20261027`** (canonical).
 2.1 [Run comparison](#bnd-compare) — fixed scope vs broken 20261026 run.
 2.2 [Natural-question gate](#bnd-natural-gate) — six rewritten prompts before a new full run.
3. [Per-row scoreboard](#bnd-rows) — all 20 ids (canonical run).
4. [Historical — manual leg empty](#bnd-root-cause) — SKU filter bug (**20261026** only).
 4.1 [Product scope contract (M9)](#bnd-uniform-metadata) — brand + OEM model.
5. [Failure drill-down](#bnd-failures) — six judge failures (**20261027**).
 5.1 [Summary table](#bnd-fail-six-summary) — all six rows.
 5.2 [Per-id detail tables](#bnd-fail-six-detail) — six Field/Content drill-downs (20261027).
 5.3 [Historical E01 & E02](#bnd-e01-e02) — empty manual leg (**20261026**).
6. [Interpretation](#bnd-interpret) — what failed and why.
7. [Reproduce](#bnd-repro) — operator commands.

---

<h2 id="bnd-setup" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Setup</h2>

| Knob | Value |
|------|--------|
| **Gold** | `tests/retail_multi_profiles/data/retail-bundled-qa-b20.json` (10 easy + 10 hard) |
| **k_manuals / k_tickets** | **5 / 2** (`config/brain-stack.example.yaml` → `second_brain.retail_evidence`) |
| **Manual leg profile** | `MANUAL_B_RAW_PG_HYBRID` (Postgres hybrid RRF, **D5 rerank off**) |
| **Manual corpus (D2)** | **Lane B** — [`brain/retail-md`](../../../brain/retail-md), glob `raw/sources/fridge-docs_md/**/*.md` (external Markdown, not LLM Wiki pages) |
| **Manual index** | Postgres `manual_chunks` with `lane_id = 'B'` (same ingest path as M90 Lane B raw RAG) |
| **Ticket leg** | Postgres, `RETAIL_TICKET_SEARCH_MODE=rrf_term_boosted` (ABC mode **C**) |
| **Assembly** | Fixed-k concat (`retail_brain.bundle_context`) |
| **Answer LLM** | OpenAI `gpt-4o-mini`, temperature **0** |
| **Judge** | Gemini `gemini-3.1-flash-lite`, temperature **0** |

---

<h2 id="bnd-manual-source" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1.1 Manual leg source (Lane B)</h2>

**Yes — the bundled harness targets Lane B (`brain/retail-md`), not wiki/`brain/retail` Lane A.**

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Layer</th><th>Value</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Ingest lane</td><td><strong>B</strong> per [`config/retail-ingest-lanes.yaml`](../../../config/retail-ingest-lanes.yaml)</td></tr>
<tr><td style="background:#e3f2fd">Project path</td><td><code>brain/retail-md</code></td></tr>
<tr><td style="background:#e3f2fd">Raw sources</td><td><code>raw/sources/fridge-docs_md/**/*.md</code></td></tr>
<tr><td style="background:#e3f2fd">Retrieval</td><td><code>ManualEvidenceRetriever</code> → PG vector + lexical RRF (<code>MANUAL_B_RAW_PG_HYBRID</code>)</td></tr>
<tr><td style="background:#e3f2fd">Not used</td><td>LLM Wiki HTTP, Lane C/D txt/learned, or ticket index</td></tr>
</tbody>
</table>

<h3 id="bnd-natural-gate" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.2 Natural-question gate (post-rewrite)</h3>

Run: <code>b20-customer-six-20261027</code>. The six prompts no longer reveal the answer or refer to retrieval artifacts such as past/similar cases or what a guide “says.” The retrieval pipeline completed normally, but all six remained judge failures; per the aligned gate, the full 20 was not rerun.

| Check | Result |
|-------|--------|
| Judge pass | **0 / 6** |
| Expected ticket id in top-2 | **0 / 6** |
| Manual leg non-empty | **6 / 6** (5 chunks each) |
| Main finding | Natural wording changed which similar tickets ranked, but did not recover the labeled ids or the missing manual numeric/procedure facts. |

---

<h2 id="bnd-headline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Headline metrics</h2>

**Canonical run:** `b20-brand-model-20261027` · Artifacts: `ops/runs/retail-bundled-qa/b20-brand-model-20261027/results.jsonl`

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Metric</th><th>All 20</th><th>Easy (10)</th><th>Hard (10)</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Judge pass (answer vs gold)</td><td style="background:#e8f5e9"><strong>14 / 20 (70%)</strong></td><td style="background:#e8f5e9">8 / 10</td><td style="background:#fff3e0">6 / 10</td></tr>
<tr><td style="background:#e3f2fd">Expected ticket id in top-2 packet</td><td style="background:#fff3e0"><strong>10 / 20 (50%)</strong></td><td style="background:#e8f5e9">6 / 10</td><td style="background:#ffebee">4 / 10</td></tr>
<tr><td style="background:#e3f2fd">Manual chunks in packet (non-empty leg)</td><td style="background:#e8f5e9"><strong>20 / 20</strong> (always 5)</td><td>10 / 10</td><td>10 / 10</td></tr>
<tr><td style="background:#e3f2fd">Mean manual retrieve ms</td><td colspan="3"><strong>491</strong> ms (PG hybrid, brand+OEM filter)</td></tr>
<tr><td style="background:#e3f2fd">Mean answer LLM ms</td><td colspan="3"><strong>1,647</strong> ms</td></tr>
<tr><td style="background:#e3f2fd">Mean judge ms</td><td colspan="3"><strong>1,632</strong> ms</td></tr>
<tr><td style="background:#e3f2fd">Wall clock (operator log)</td><td colspan="3">~100 s for 20 rows</td></tr>
</tbody>
</table>

**Notable passes without gold ticket in top-2:** `BND-H01`, `BND-H03`, `BND-E07`, `BND-E10` — manual + wrong/similar tickets still judged OK when excerpts carried gold facts.

<h3 id="bnd-compare" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.1 Run comparison</h3>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Metric</th><th><code>b20-brand-model-20261027</code></th><th><code>b20-full-20261026</code> (buggy filter)</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Product filter</td><td style="background:#e8f5e9">M9 <code>brand</code> + <code>oem_model</code></td><td style="background:#ffebee">Bare OEM as <code>model_id</code></td></tr>
<tr><td style="background:#e3f2fd">Judge pass</td><td style="background:#e8f5e9"><strong>14 / 20</strong></td><td style="background:#ffebee">2 / 20</td></tr>
<tr><td style="background:#e3f2fd">Ticket-in-packet</td><td>10 / 20</td><td>10 / 20</td></tr>
<tr><td style="background:#e3f2fd">Empty manual leg</td><td style="background:#e8f5e9"><strong>0 / 20</strong></td><td style="background:#ffebee">~18 / 20</td></tr>
</tbody>
</table>

---

<h2 id="bnd-rows" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Per-row scoreboard</h2>

Source: **`b20-brand-model-20261027`** · Full payloads in `results.jsonl` (`candidate_answer`, `manual_leg_context`, `ticket_leg_context`).

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Id</th><th>Diff</th><th>Judge</th><th>Ticket in packet</th><th>Manual k</th><th>Notes (20261027)</th></tr>
</thead>
<tbody>
<tr><td>BND-E01</td><td>easy</td><td style="background:#e8f5e9">pass</td><td style="background:#e8f5e9">yes</td><td>5</td><td>Display board + door alarm 2 min</td></tr>
<tr><td>BND-E02</td><td>easy</td><td style="background:#e8f5e9">pass</td><td style="background:#e8f5e9">yes</td><td>5</td><td>Air damper + factory presets</td></tr>
<tr><td>BND-E03</td><td>easy</td><td style="background:#ffebee">fail</td><td style="background:#ffebee">no</td><td>5</td><td>Wrong tickets; filter-only answer — [§5.2](#bnd-fail-six-detail)</td></tr>
<tr><td>BND-E04</td><td>easy</td><td style="background:#e8f5e9">pass</td><td style="background:#e8f5e9">yes</td><td>5</td><td>Fill-tube heater + 35–120 psi</td></tr>
<tr><td>BND-E05</td><td>easy</td><td style="background:#e8f5e9">pass</td><td style="background:#e8f5e9">yes</td><td>5</td><td>Auger + outlet spec</td></tr>
<tr><td>BND-E06</td><td>easy</td><td style="background:#e8f5e9">pass</td><td style="background:#e8f5e9">yes</td><td>5</td><td>Hinge cams + 6 mo filter</td></tr>
<tr><td>BND-E07</td><td>easy</td><td style="background:#e8f5e9">pass</td><td style="background:#ffebee">no</td><td>5</td><td>Heater wire + freezer temps (judge OK w/o gold ticket)</td></tr>
<tr><td>BND-E08</td><td>easy</td><td style="background:#ffebee">fail</td><td style="background:#ffebee">no</td><td>5</td><td>Wrong ambient range 34–44°F — [§5.2](#bnd-fail-six-detail)</td></tr>
<tr><td>BND-E09</td><td>easy</td><td style="background:#e8f5e9">pass</td><td style="background:#e8f5e9">yes</td><td>5</td><td>Air damper + Control Lock 3 s</td></tr>
<tr><td>BND-E10</td><td>easy</td><td style="background:#e8f5e9">pass</td><td style="background:#ffebee">no</td><td>5</td><td>Start relay + door alarm (judge OK w/o gold ticket)</td></tr>
<tr><td>BND-H01</td><td>hard</td><td style="background:#e8f5e9">pass</td><td style="background:#ffebee">no</td><td>5</td><td>Air damper + 12–24 h ice</td></tr>
<tr><td>BND-H02</td><td>hard</td><td style="background:#ffebee">fail</td><td style="background:#ffebee">no</td><td>5</td><td>20 psi vs gold 25–120 — [§5.2](#bnd-fail-six-detail)</td></tr>
<tr><td>BND-H03</td><td>hard</td><td style="background:#e8f5e9">pass</td><td style="background:#ffebee">no</td><td>5</td><td>Paraphrase OK without labeled ticket</td></tr>
<tr><td>BND-H04</td><td>hard</td><td style="background:#e8f5e9">pass</td><td style="background:#e8f5e9">yes</td><td>5</td><td>Fill-tube heater + ice maker off</td></tr>
<tr><td>BND-H05</td><td>hard</td><td style="background:#e8f5e9">pass</td><td style="background:#e8f5e9">yes</td><td>5</td><td>Hinge + filter interval</td></tr>
<tr><td>BND-H06</td><td>hard</td><td style="background:#e8f5e9">pass</td><td style="background:#e8f5e9">yes</td><td>5</td><td>Was fail on empty-manual run; now pass</td></tr>
<tr><td>BND-H07</td><td>hard</td><td style="background:#ffebee">fail</td><td style="background:#ffebee">no</td><td>5</td><td>Missing Power Freeze 3 s hold — [§5.2](#bnd-fail-six-detail)</td></tr>
<tr><td>BND-H08</td><td>hard</td><td style="background:#ffebee">fail</td><td style="background:#ffebee">no</td><td>5</td><td>Freezer button span not found — [§5.2](#bnd-fail-six-detail)</td></tr>
<tr><td>BND-H09</td><td>hard</td><td style="background:#e8f5e9">pass</td><td style="background:#e8f5e9">yes</td><td>5</td><td>FlexZone / soft-freeze</td></tr>
<tr><td>BND-H10</td><td>hard</td><td style="background:#ffebee">fail</td><td style="background:#ffebee">no</td><td>5</td><td>Room temp 3°F nonsense — [§5.2](#bnd-fail-six-detail)</td></tr>
</tbody>
</table>

---

<h2 id="bnd-root-cause" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Historical — manual leg empty on most rows (20261026)</h2>

Run **`b20-full-20261026`** passed B20’s bare ticket SKU (e.g. <code>GNE27JYMFS</code>) into PG retrieval as <code>model_id</code>. Indexed Lane B chunks use **folder ids** (e.g. <code>ge_GNE27JYMFS</code>). The filter matched **zero rows**, so the manual leg context was **empty** even though hybrid search returned in ~200 ms.

| B20 JSON field | Example | PG `manual_chunks.model_id` |
|----------------|---------|----------------------------|
| <code>model</code> | <code>GNE27JYMFS</code> | <code>ge_GNE27JYMFS</code> |

M90 avoids this: suite rows use <code>ge_GNE27JYMFS</code>, and the harness calls <code>resolve_retrieval_sku</code> + company profile mapping. **Code fix:** all legs should use <code>retail_brain.product_scope.resolve_product_scope</code> (see [§4.1](#bnd-uniform-metadata)).

**Impact:** Ticket leg often worked; answer LLM saw **tickets only** → judge failures on manual half and inflated “Insufficient_Information” rates. **Re-run B20** after the fix before trusting headline metrics.

---

<h2 id="bnd-uniform-metadata" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4.1 Uniform product metadata (best practice)</h2>

<h3 id="bnd-industry" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">What production RAG systems do (2024–2026)</h3>

Vector and hybrid search stacks (OpenSearch kNN, pgvector, Qdrant, Weaviate, Pinecone, etc.) treat **metadata filtering** as first-class: every chunk/document carries **stable, filterable attributes** (tenant, product, locale, doc type). At **query time**, one normalized scope object drives filters on **all** retrievers — not different string conventions per index.

Typical pattern:

1. **Canonical entity id** on every indexed row (your case: <code>catalog_sku = ge_GNE27JYMFS</code>).
2. **Secondary aliases** where the source system uses another code (tickets: OEM <code>GNE27JYMFS</code> on <code>service_queries.model</code>).
3. **Resolve once** at the API/harness boundary; log the resolved scope on every answer/evidence payload.
4. **Optional:** duplicate <code>catalog_sku</code> onto ticket rows at ingest so both legs filter the same metadata key long term.

<h3 id="bnd-repo-contract" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">This repo — exact contract</h3>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Field</th><th>Format</th><th>Used by</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong><code>catalog_sku</code></strong></td><td><code>ge_GNE27JYMFS</code>, <code>kitchenaid_KRFF507HPS</code>, …</td><td>Manual PG <code>manual_chunks.model_id</code>, raw paths, M90/B20 gold, ingest lanes</td></tr>
<tr><td style="background:#e3f2fd"><strong><code>oem_model</code></strong></td><td><code>GNE27JYMFS</code> (manufacturer model code)</td><td>Ticket Postgres <code>service_queries.model</code>, customer query text</td></tr>
<tr><td style="background:#e3f2fd"><strong><code>lane_id</code></strong></td><td><code>B</code> (manual only)</td><td>Which corpus (<code>brain/retail-md</code>)</td></tr>
</tbody>
</table>

**Single entry point (M9):** <code>scripts/retail/retail_brain/product_scope.py</code> → <code>resolve_product_scope(…)</code> returns <code>ProductScope</code> with:

- <code>.manual_filter</code> / <code>.ticket_filter</code> → <strong>brand + OEM model</strong> (same pair on both legs)  
- <code>.ingest_key</code> → folder slug (e.g. <code>ge_GNE27JYMFS</code>) for lineage only  
- <code>.to_metadata()</code> → JSON on every harness/bundle row  

**Catalog helpers** live in <code>retail_brain/sku_scope.py</code> (moved out of tests); <code>resolve_retrieval_sku</code> now accepts suite hints in **either** catalog or OEM form (<code>suite_oem_fallback</code>).

<h3 id="bnd-gold-fixtures" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">Gold fixtures — naming</h3>

| Today (B20) | Recommended |
|-------------|-------------|
| <code>"model": "GNE27JYMFS"</code> | <code>"catalog_sku": "ge_GNE27JYMFS"</code> plus optional <code>"oem_model": "GNE27JYMFS"</code> |

Until B20 JSON is migrated, <code>resolve_product_scope</code> maps bare suite <code>model</code> via <code>fru_us_service.yaml</code>. New suites should **author catalog_sku only** in the canonical form.

<h3 id="bnd-future-ingest" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">Future ingest (optional hardening)</h3>

- Add <code>catalog_sku</code> column on <code>service_queries</code> (denormalized from <code>model</code> at load time).  
- Store both fields in Tantivy/lexical ticket index metadata.  
- Manual chunks already use <code>model_id = catalog_sku</code> — keep that name or rename column to <code>catalog_sku</code> in a later migration for clarity.

---

<h2 id="bnd-failures" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Failure drill-down — six judge failures (20261027)</h2>

Current six-row evidence: <code>b20-customer-six-20261027</code>. Every row received **5 manual chunks**, but only **BND-E03** received the expected manual page/fact. The other five are manual top-5 retrieval misses. All six missed the strict labeled ticket id, although five packets contained another ticket with the same resolution.

<h3 id="bnd-fail-six-summary" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">5.1 Summary table</h3>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Id</th><th>Gold ticket</th><th>Top-2 tickets (current run)</th><th>Expected manual</th><th>Diagnostic full-pool rank</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">BND-E03</td><td>T-0042-100043</td><td>T-0042-100931, T-0042-100382</td><td>GE user guide p.14 — XWFE housing</td><td style="background:#e8f5e9"><strong>2</strong> (in packet)</td></tr>
<tr><td style="background:#e3f2fd">BND-E08</td><td>T-0042-100004</td><td>T-0042-100825, T-0042-100980</td><td>Samsung user guide p.27 — 50–110°F ambient</td><td style="background:#ffebee"><strong>49</strong></td></tr>
<tr><td style="background:#e3f2fd">BND-H02</td><td>T-0042-100017</td><td>T-0042-100383, T-0042-100426</td><td>GE user guide p.20 — 25–120 psi</td><td style="background:#ffebee"><strong>17</strong></td></tr>
<tr><td style="background:#e3f2fd">BND-H07</td><td>T-0042-100002</td><td>T-0042-100482, T-0042-100738</td><td>Samsung user guide p.37 — hold Freezer 3 sec</td><td style="background:#ffebee"><strong>22</strong></td></tr>
<tr><td style="background:#e3f2fd">BND-H08</td><td>T-0042-100004</td><td>T-0042-100422, T-0042-100783</td><td>Samsung user guide p.37 — 5°F to −8°F</td><td style="background:#ffebee"><strong>23</strong></td></tr>
<tr><td style="background:#e3f2fd">BND-H10</td><td>T-0042-100010</td><td>T-0042-100176, T-0042-100777</td><td>Samsung user guide p.27 — 50–110°F ambient</td><td style="background:#ffebee"><strong>45</strong></td></tr>
</tbody>
</table>

<h3 id="bnd-fail-six-detail" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">5.2 Per-id detail tables</h3>

Evidence from current run <code>b20-customer-six-20261027</code>. Manual leg: **5 chunks**, filter <strong>brand + OEM model</strong> (M9). Full verbatim context: <code>ops/runs/retail-bundled-qa/b20-customer-six-20261027/results.jsonl</code>.

<h4 id="bnd-fail-e03" style="color:#00695c;font-size:1em;font-weight:600;margin-top:0.75em">5.2.1 BND-E03</h4>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Field</th><th>Content</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>Question</strong> (current full text)</td><td>My GNE27JYMFS keeps freezing the ice cubes into one solid clump, and the food sometimes feels warm even though the app reports normal temperatures. What should a technician check or repair to stop this, and where is the XWFE filter housing located?</td></tr>
<tr><td style="background:#e3f2fd"><strong>Gold / expected answer</strong></td><td>The repair adjusted the freezer temperature and replaced the bin auger seal. The XWFE filter housing is in the back upper-right corner of the refrigerator compartment.</td></tr>
<tr><td style="background:#fff8e1"><strong>Expected ticket</strong> (gold label — <em>not in top-2 packet</em>)</td><td><strong>T-0042-100043</strong> · issue <code>ice_clumping</code> · FRU-E118<br><br><strong>Customer:</strong> Intake: GNE27JYMFS owner in Long Beach, CA — ice cubes clumping together in the bin. Smart app shows normal temps but food feels warm. Ticket context #43: no power blinks. Technician later confirmed FRU-E118 in the service log.<br><br><strong>Resolution:</strong> Adjusted freezer temperature and replaced bin auger seal.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Historical ticket leg</strong> (top 2 retrieved, mode C)</td><td><strong>T-0042-100931</strong> (rank 1) — ice maker stopped producing cubes; <em>cleared jammed auger and reset ice-maker module.</em><br><br><strong>T-0042-100382</strong> (rank 2) — water leaking from ice-maker housing; <em>replaced fill-tube heater and tightened inlet valve.</em></td></tr>
<tr><td style="background:#fff8e1"><strong>Expected manual evidence</strong></td><td><strong>Anchor:</strong> <code>ge_GNE27JYMFS-E03</code><br><strong>Manual:</strong> <code>fridge-docs/ge_GNE27JYMFS/user-guide.pdf</code> · printed/PDF page <strong>14</strong><br><strong>Lane B source:</strong> <code>brain/retail-md/raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md</code>, heading <code>PDF page 14</code><br><strong>Expected fact:</strong> “The water filter cartridge holder is located in the back upper-right corner of the refrigerator compartment.”</td></tr>
<tr><td style="background:#e8f5e9"><strong>Retrieved manual leg</strong> (Lane B PG)</td><td><strong>5 chunks</strong>. The expected page-14 XWFE passage <strong>was in the packet</strong>; the model correctly returned the location. Filter: <code>GE</code> + <code>GNE27JYMFS</code>.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Verbatim model answer</strong> (<code>b20-customer-six-20261027</code>)</td><td>To address the issue of your GNE27JYMFS freezing ice cubes into a solid clump and the food feeling warm despite normal app temperature readings, a technician should check the following:<br><br>1. <strong>Ice Maker Module</strong>: The technician should clear any jammed auger and reset the ice maker module, as this has been a resolution in past tickets for similar issues.<br><br>2. <strong>Temperature Settings</strong>: Ensure that the refrigerator control is set to an appropriate temperature. If it is set too cold, it may cause food to feel warm and ice to freeze improperly.<br><br>3. <strong>Air Flow</strong>: Check if food is too close to the air vent at the back of the refrigerator, as this can affect cooling efficiency.<br><br>4. <strong>Water Filter</strong>: If the water filter is clogged, it may affect ice production. The technician should verify the condition of the XWFE filter and replace it if necessary.<br><br>The XWFE filter housing is located in the back upper-right corner of the refrigerator compartment.</td></tr>
<tr><td style="background:#fff3e0"><strong>Judge</strong></td><td>Fail — speculative troubleshooting not supported by the gold answer; it did not cleanly give the auger-seal/freezer-setpoint repair.</td></tr>
</tbody>
</table>

<h4 id="bnd-fail-e08" style="color:#00695c;font-size:1em;font-weight:600;margin-top:0.75em">5.2.2 BND-E08</h4>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Field</th><th>Content</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>Question</strong> (current full text)</td><td>The water dispenser on my RF28K9070SG has slowed to a trickle and the display showed FRU-E103. What should a technician check or replace, and what room-temperature range is safe for operating the refrigerator?</td></tr>
<tr><td style="background:#e3f2fd"><strong>Gold / expected answer</strong></td><td>The case replaced a clogged inline filter and flushed the water line. The allowed room temperature is 50–110°F (10–43°C).</td></tr>
<tr><td style="background:#fff8e1"><strong>Expected ticket</strong> (gold label — <em>not in top-2 packet</em>)</td><td><strong>T-0042-100004</strong> · FRU-E103 on service menu<br><br><strong>Customer:</strong> RF28K9070SG water dispenser runs very slowly (Virginia Beach Store). Kids leave door open sometimes. Ticket context #4. Display showed FRU-E103.<br><br><strong>Resolution:</strong> Replaced clogged inline filter and flushed water line.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Historical ticket leg</strong> (top 2 retrieved, mode C)</td><td><strong>T-0042-100825</strong> (rank 1) — slow dispenser, Raleigh, FRU-E513 — <em>same inline-filter + flush resolution as gold.</em><br><strong>T-0042-100980</strong> (rank 2) — slow dispenser, Raleigh, FRU-E591 — <em>same resolution as gold.</em></td></tr>
<tr><td style="background:#fff8e1"><strong>Expected manual evidence</strong></td><td><strong>Anchor:</strong> <code>samsung_RF28K9070SG-E01</code><br><strong>Manual:</strong> <code>fridge-docs/samsung_RF28K9070SG/user-guide.pdf</code> · printed/PDF page <strong>27</strong><br><strong>Lane B source:</strong> <code>brain/retail-md/raw/sources/fridge-docs_md/samsung_RF28K9070SG/user-guide.md</code>, heading <code>PDF page 27</code><br><strong>Expected fact:</strong> Site temperature must be <strong>50–110°F (10–43°C)</strong>.</td></tr>
<tr><td style="background:#ffebee"><strong>Retrieved manual leg</strong> (Lane B PG)</td><td><strong>5 chunks</strong>, but expected page 27 / <strong>50–110°F</strong> passage was <strong>not in the packet</strong>. Retrieved text instead led toward the refrigerator setpoint band; manual retrieval miss.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Verbatim model answer</strong> (<code>b20-customer-six-20261027</code>)</td><td>To address the issue of the water dispenser on your RF28K9070SG slowing to a trickle and displaying FRU-E103, a technician should check and potentially replace the clogged inline filter and flush the water line, as indicated in past tickets where similar issues were resolved.<br><br>Regarding the safe operating conditions for the refrigerator, the manual does not specify an exact room-temperature range. However, it does mention that if the ambient room temperature is too low, it can affect the refrigerator's performance. Therefore, it is advisable to ensure that the refrigerator is not exposed to excessively low temperatures to maintain optimal functionality.<br><br>In summary, the technician should:<br>1. Check and replace the clogged inline filter.<br>2. Flush the water line.<br>3. Ensure the refrigerator is in a suitable ambient temperature environment.</td></tr>
<tr><td style="background:#fff3e0"><strong>Judge</strong></td><td>Fail — omitted the required <strong>50–110°F</strong> operating range and incorrectly said no exact range was available.</td></tr>
</tbody>
</table>

<h4 id="bnd-fail-h02" style="color:#00695c;font-size:1em;font-weight:600;margin-top:0.75em">5.2.3 BND-H02</h4>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Field</th><th>Content</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>Question</strong> (current full text)</td><td>The door display on my GNE27JYMFS no longer responds when I press it. What component should a technician reset or repair, and what cold-water pressure does the ice maker need?</td></tr>
<tr><td style="background:#e3f2fd"><strong>Gold / expected answer</strong></td><td>They power-cycled the display board and updated firmware. The cold-water line should supply 25–120 psi (172–827 kPa).</td></tr>
<tr><td style="background:#fff8e1"><strong>Expected ticket</strong> (gold label — <em>not in top-2 packet</em>)</td><td><strong>T-0042-100017</strong> · FRU-E108 (owner photo)<br><br><strong>Customer:</strong> GNE27JYMFS touch panel unresponsive (Omaha Store). Ticket context #17: extended warranty.<br><br><strong>Resolution:</strong> Power-cycled display board and updated firmware.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Historical ticket leg</strong> (top 2 retrieved, mode C)</td><td><strong>T-0042-100383</strong> (rank 1) — ice-maker housing leak, Omaha, FRU-E293 — fill-tube heater resolution.<br><strong>T-0042-100426</strong> (rank 2) — touch panel unresponsive, Mesa, FRU-E317 — <em>power-cycled display board and updated firmware.</em></td></tr>
<tr><td style="background:#fff8e1"><strong>Expected manual evidence</strong></td><td><strong>Anchor:</strong> <code>ge_GNE27JYMFS-E05</code><br><strong>Manual:</strong> <code>fridge-docs/ge_GNE27JYMFS/user-guide.pdf</code> · printed/PDF page <strong>20</strong><br><strong>Lane B source:</strong> <code>brain/retail-md/raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md</code>, heading <code>PDF page 20</code><br><strong>Expected fact:</strong> Automatic ice maker cold-water pressure must be <strong>25–120 psi (172–827 kPa)</strong>.</td></tr>
<tr><td style="background:#ffebee"><strong>Retrieved manual leg</strong> (Lane B PG)</td><td><strong>5 chunks</strong>, but expected page 20 pressure passage was <strong>not in the packet</strong>. Retrieved text mentioned low pressure generally; the model supplied an unsupported <strong>20–120 psi</strong>.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Verbatim model answer</strong> (<code>b20-customer-six-20261027</code>)</td><td>To resolve the issue with the unresponsive door display on your GNE27JYMFS, a technician should power-cycle the display board and update the firmware, as indicated in past ticket T-0042-100426.<br><br>Regarding the ice maker, it requires a cold-water pressure of 20 to 120 psi to function properly, although this specific detail was not provided in the past tickets or manual excerpts.<br><br>Therefore, the technician should focus on resetting the display board and ensuring the water pressure is within the required range for the ice maker.</td></tr>
<tr><td style="background:#fff3e0"><strong>Judge</strong></td><td>Fail — display-board repair correct; pressure range wrong (gold: <strong>25–120 psi</strong>).</td></tr>
</tbody>
</table>

<h4 id="bnd-fail-h07" style="color:#00695c;font-size:1em;font-weight:600;margin-top:0.75em">5.2.4 BND-H07</h4>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Field</th><th>Content</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>Question</strong> (current full text)</td><td>Puddles keep forming under the crisper drawers in my RF28K9070SG even though it is on a dedicated 20-amp circuit. What should a technician clear or repair, and how do I start Power Freeze?</td></tr>
<tr><td style="background:#e3f2fd"><strong>Gold / expected answer</strong></td><td>They cleared the defrost drain tube and installed a heater-wire kit. Press and hold Freezer for 3 seconds.</td></tr>
<tr><td style="background:#fff8e1"><strong>Expected ticket</strong> (gold label — <em>not in top-2 packet</em>)</td><td><strong>T-0042-100002</strong> · FRU-E101 · second visit · dedicated 20A<br><br><strong>Customer:</strong> RF28K9070SG water pooling under crisper drawers (Virginia Beach). Unit on dedicated 20A circuit. Ticket context #2: second visit. FRU-E101 in service log.<br><br><strong>Resolution:</strong> Cleared defrost drain tube and installed heater wire kit.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Historical ticket leg</strong> (top 2 retrieved, mode C)</td><td><strong>T-0042-100482</strong> (rank 1) — pooling under crispers, Kansas City — <em>same drain + heater-kit resolution as gold.</em><br><strong>T-0042-100738</strong> (rank 2) — pooling under crispers, Kansas City — <em>same resolution as gold.</em></td></tr>
<tr><td style="background:#fff8e1"><strong>Expected manual evidence</strong></td><td><strong>Anchor:</strong> <code>samsung_RF28K9070SG-E03</code><br><strong>Manual:</strong> <code>fridge-docs/samsung_RF28K9070SG/user-guide.pdf</code> · printed/PDF page <strong>37</strong><br><strong>Lane B source:</strong> <code>brain/retail-md/raw/sources/fridge-docs_md/samsung_RF28K9070SG/user-guide.md</code>, heading <code>PDF page 37</code><br><strong>Expected fact:</strong> “To activate Power Freeze, press and hold Freezer for <strong>3 seconds</strong>.”</td></tr>
<tr><td style="background:#ffebee"><strong>Retrieved manual leg</strong> (Lane B PG)</td><td><strong>5 chunks</strong>, but expected page 37 Power Freeze passage was <strong>not in the packet</strong>. The model guessed “press” and omitted the hold duration; manual retrieval miss.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Verbatim model answer</strong> (<code>b20-customer-six-20261027</code>)</td><td>To address the issue of water pooling under the crisper drawers in your RF28K9070SG, the technician should clear the defrost drain tube and install a heater wire kit, as indicated in previous resolved tickets.<br><br>To start Power Freeze, locate the feature panel on your refrigerator. Press the “Freezer / Power Freeze” button to activate the Power Freeze function. This will help in quickly freezing items in the freezer compartment.<br><br>If you encounter any further issues, ensure that the refrigerator is properly leveled and that the door closes securely to prevent condensation and pooling.</td></tr>
<tr><td style="background:#fff3e0"><strong>Judge</strong></td><td>Fail — repair correct; Power Freeze instruction omitted the required <strong>3-second hold</strong> and added unsupported advice.</td></tr>
</tbody>
</table>

<h4 id="bnd-fail-h08" style="color:#00695c;font-size:1em;font-weight:600;margin-top:0.75em">5.2.5 BND-H08</h4>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Field</th><th>Content</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>Question</strong> (current full text)</td><td>The water dispenser on my RF28K9070SG only trickles after I fill several jugs. What part should a technician check or replace, and what temperature range can I select with the Freezer button?</td></tr>
<tr><td style="background:#e3f2fd"><strong>Gold / expected answer</strong></td><td>They replaced a clogged inline filter and flushed the water line. Freezer settings run from 5°F (−15°C) down to −8°F (−23°C).</td></tr>
<tr><td style="background:#fff8e1"><strong>Expected ticket</strong> (gold label — <em>not in top-2 packet</em>)</td><td><strong>T-0042-100004</strong> (same gold id as BND-E08 — slow dispenser + FRU-E103). See [§5.2.2](#bnd-fail-e08) for full customer/resolution.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Historical ticket leg</strong> (top 2 retrieved, mode C)</td><td><strong>T-0042-100422</strong> (rank 1) — slow dispenser, Kansas City — inline filter + flush.<br><strong>T-0042-100783</strong> (rank 2) — slow dispenser, Colorado Springs — inline filter + flush.</td></tr>
<tr><td style="background:#fff8e1"><strong>Expected manual evidence</strong></td><td><strong>Anchor:</strong> <code>samsung_RF28K9070SG-E02</code><br><strong>Manual:</strong> <code>fridge-docs/samsung_RF28K9070SG/user-guide.pdf</code> · printed/PDF page <strong>37</strong><br><strong>Lane B source:</strong> <code>brain/retail-md/raw/sources/fridge-docs_md/samsung_RF28K9070SG/user-guide.md</code>, heading <code>PDF page 37</code><br><strong>Expected fact:</strong> Freezer button settings range from <strong>5°F (−15°C) to −8°F (−23°C)</strong>.</td></tr>
<tr><td style="background:#ffebee"><strong>Retrieved manual leg</strong> (Lane B PG)</td><td><strong>5 chunks</strong>, but expected page 37 temperature passage was <strong>not in the packet</strong>. Retrieved excerpts covered water-line/ice purge, so the model abstained; manual retrieval miss.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Verbatim model answer</strong> (<code>b20-customer-six-20261027</code>)</td><td>To resolve the issue of the water dispenser on your RF28K9070SG only trickling after filling several jugs, a technician should check or replace the clogged inline filter and flush the water line, as indicated in past tickets T-0042-100422 and T-0042-100783.<br><br>Regarding the temperature range that can be selected with the Freezer button, the manual does not specify the exact temperature range available. Therefore, the response is: <code>Insufficient_Information_Based_On_Given_PDF</code>.</td></tr>
<tr><td style="background:#fff3e0"><strong>Judge</strong></td><td>Fail — filter repair correct; failed to provide the gold Freezer range <strong>5°F to −8°F</strong>.</td></tr>
</tbody>
</table>

<h4 id="bnd-fail-h10" style="color:#00695c;font-size:1em;font-weight:600;margin-top:0.75em">5.2.6 BND-H10</h4>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Field</th><th>Content</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>Question</strong> (current full text)</td><td>My RF28K9070SG has a loud hum near the compressor and the food feels warm even though the app reports normal temperatures; the display also showed FRU-E104. After checking that the refrigerator is level, what electrical part should a technician inspect or replace, and what room-temperature range is safe for operation?</td></tr>
<tr><td style="background:#e3f2fd"><strong>Gold / expected answer</strong></td><td>After leveling and tightening the condenser mounts, the start relay was replaced. The allowed ambient range is 50–110°F (10–43°C).</td></tr>
<tr><td style="background:#fff8e1"><strong>Expected ticket</strong> (gold label — <em>not in top-2 packet</em>)</td><td><strong>T-0042-100010</strong> · FRU-E104 · Atlanta<br><br><strong>Customer:</strong> RF28K9070SG loud humming from compressor area. Smart app shows normal temps but food feels warm. Ticket context #10: original install. Display showed FRU-E104.<br><br><strong>Resolution:</strong> Leveled unit, tightened condenser mounts, replaced start relay.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Historical ticket leg</strong> (top 2 retrieved, mode C)</td><td><strong>T-0042-100176</strong> (rank 1) — compressor hum, Kansas City, FRU-E184 — <em>same resolution as gold.</em><br><strong>T-0042-100777</strong> (rank 2) — compressor hum, Kansas City, FRU-E492 — <em>same resolution as gold.</em></td></tr>
<tr><td style="background:#fff8e1"><strong>Expected manual evidence</strong></td><td><strong>Anchor:</strong> <code>samsung_RF28K9070SG-E01</code><br><strong>Manual:</strong> <code>fridge-docs/samsung_RF28K9070SG/user-guide.pdf</code> · printed/PDF page <strong>27</strong><br><strong>Lane B source:</strong> <code>brain/retail-md/raw/sources/fridge-docs_md/samsung_RF28K9070SG/user-guide.md</code>, heading <code>PDF page 27</code><br><strong>Expected fact:</strong> Installation-site temperature must be <strong>50–110°F (10–43°C)</strong>.</td></tr>
<tr><td style="background:#ffebee"><strong>Retrieved manual leg</strong> (Lane B PG)</td><td><strong>5 chunks</strong>, but expected user-guide page 27 passage was <strong>not in the packet</strong>. In a widened diagnostic over all 59 product-filtered chunks, it ranked lexical <strong>48</strong>, vector <strong>35</strong>, and fused <strong>45</strong>. Production only admits each leg's top 20 before fusion, so this chunk was excluded before reciprocal rank fusion. Top evidence came from <code>repair-guide.md</code> and user-guide troubleshooting; manual retrieval miss.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Verbatim model answer</strong> (<code>b20-customer-six-20261027</code>)</td><td>The technician should inspect or replace the start relay, as indicated in the past tickets where similar issues were resolved. Additionally, the safe room-temperature range for operation is not explicitly stated in the provided excerpts. Therefore, based on the information available, the response is:<br><br><code>Insufficient_Information_Based_On_Given_PDF</code></td></tr>
<tr><td style="background:#fff3e0"><strong>Judge</strong></td><td>Fail — start relay correct; omitted the required operating range <strong>50–110°F</strong>.</td></tr>
</tbody>
</table>

<p><strong>Pattern:</strong> All six rows: <strong>gold ticket id ∉ top-2</strong> (strict id label), but five packets still carry the <em>same resolution text</em> on another ticket. Manual evidence is the sharper blocker: the expected page/fact is absent from top-5 on five rows. E03 is the exception—the correct XWFE passage is present, but the ticket packet drives speculative repair advice.</p>

<h3 id="bnd-e01-e02" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">5.3 Historical — BND-E01 &amp; BND-E02 (empty manual leg, 20261026)</h3>

Evidence from run <code>b20-full-20261026</code> (ticket leg + model answer). Manual leg text below is what the harness **actually fed** (empty). Ticket leg text reproduced with the same Postgres + mode **C** settings. **After M9, E01 and E02 judge pass** on <code>b20-brand-model-20261027</code> — see [§3](#bnd-rows).

<h4 id="bnd-e01-table" style="color:#00695c;font-size:1em;font-weight:600;margin-top:0.75em">5.3.1 BND-E01</h4>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Field</th><th>Content</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>Question</strong></td><td>On a GNE27JYMFS the touch panel is unresponsive (same complaint as a resolved Omaha case that showed FRU-E108). What did that case do, and when does the user guide say the door alarm beeps?</td></tr>
<tr><td style="background:#e3f2fd"><strong>Gold / expected answer</strong></td><td>The resolved case power-cycled the display board and updated firmware. When the door alarm is enabled, it sounds if either door stays open for more than 2 minutes; closing the door stops the beeping.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Historical ticket leg</strong> (top 2, mode C)</td><td><strong>T-0042-100017</strong> (expected) — Resolution: <em>Power-cycled display board and updated firmware.</em><br><br><strong>T-0042-100831</strong> — same resolution text (duplicate symptom class).</td></tr>
<tr><td style="background:#ffebee"><strong>Manual leg</strong> (Lane B PG, as run)</td><td><strong>(empty)</strong> — 0 chunks. PG filter used <code>model_id=GNE27JYMFS</code>; index has <code>ge_GNE27JYMFS</code> only.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Model answer</strong> (bundled LLM output)</td><td>To resolve the unresponsive touch panel… power-cycling the display board and updating the firmware.<br><br>Regarding the door alarm beeping, there is no information provided in the excerpts about when the door alarm beeps.<br><br><code>Insufficient_Information_Based_On_Given_PDF</code></td></tr>
<tr><td style="background:#fff3e0"><strong>Judge</strong></td><td>Fail — ticket half OK; manual half missing (door alarm timing).</td></tr>
</tbody>
</table>

<p><strong>Counterfactual (same query, correct filter <code>ge_GNE27JYMFS</code>):</strong> PG returns 5 chunks from <code>raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md</code>, including: <em>“The alarm will sound if either door is left open for more than 2 minutes. The beeping stops when you close the door.”</em> — so this easy row is primarily a <strong>harness SKU bug</strong>, not missing ingest.</p>

<h4 id="bnd-e02-table" style="color:#00695c;font-size:1em;font-weight:600;margin-top:0.75em">5.3.2 BND-E02</h4>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Field</th><th>Content</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>Question</strong></td><td>A GNE27JYMFS has warm spots on the upper refrigerator shelves after a Costco load (Long Beach case, no fault code in the short symptom). What was the resolution, and what factory refrigerator and freezer presets does the top-control guide list?</td></tr>
<tr><td style="background:#e3f2fd"><strong>Gold / expected answer</strong></td><td>The case cleared a blocked air damper and recalibrated the temperature sensors. Factory presets are 37°F (2.8°C) for the refrigerator and 0°F (−17.8°C) for the freezer.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Historical ticket leg</strong> (top 2, mode C)</td><td><strong>T-0042-100845</strong> (rank 1) — Resolution: <em>Cleared blocked air damper and recalibrated temperature sensors.</em><br><br><strong>T-0042-100000</strong> (expected, rank 2) — same resolution (Long Beach / Costco wording).</td></tr>
<tr><td style="background:#ffebee"><strong>Manual leg</strong> (Lane B PG, as run)</td><td><strong>(empty)</strong> — same SKU filter bug as E01.</td></tr>
<tr><td style="background:#e3f2fd"><strong>Model answer</strong> (bundled LLM output)</td><td>Resolution: Cleared blocked air damper and recalibrated temperature sensors.<br><br>Factory refrigerator and freezer presets: <code>Insufficient_Information_Based_On_Given_PDF</code></td></tr>
<tr><td style="background:#fff3e0"><strong>Judge</strong></td><td>Fail — ticket half OK; factory presets not stated.</td></tr>
</tbody>
</table>

<p><strong>Counterfactual (filter <code>ge_GNE27JYMFS</code>):</strong> top chunks include factory preset copy: freezer <strong>0°F (−17.8°C)</strong>, refrigerator <strong>37°F (2.8°C)</strong> from the same user-guide controls section.</p>

---

<h2 id="bnd-interpret" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Interpretation</h2>

1. **Prior full-20 baseline:** <code>b20-brand-model-20261027</code> scored **14/20** by the judge, **10/20** on strict expected-ticket-id inclusion, and had **0** empty manual legs. The later targeted run <code>b20-customer-six-20261027</code> uses the six rewritten customer questions and scored **0/6**; the full 20 has not yet been rerun with those rewrites.
2. **Strict id recall is not effective evidence recall:** all six targeted rows missed their labeled ticket id in the top two, but five retrieved a different ticket carrying the same repair. Those five ticket legs made a real, correct contribution and are not ticket-evidence failures.
3. **Only BND-E03 is a true ticket-evidence failure:** neither returned ticket contains the gold repair. A same-repair duplicate, <code>T-0042-100993</code>, ranked third and was cut by <code>k_tickets=2</code>; the labeled ticket ranked fifth. The mixed query split the labeled ticket across vector rank 13 and lexical rank 6, while reciprocal rank fusion favored ice-maker and water-system distractors that scored moderately well in both lists.
4. **The other five are manual retrieval failures:** their expected manual chunks ranked **49 (E08), 17 (H02), 22 (H07), 23 (H08), and 45 (H10)**, outside <code>k_manuals=5</code>. The facts do exist in the verified Lane B Markdown sources; this is ranking failure, not missing source content or wrong brand/model filtering.
5. **Why manual ranking fails:** one combined customer question is sent unchanged to both retrieval legs. Service symptoms and repair language intended for ticket search therefore compete with the specification or procedure terms intended for manual search. Hybrid lexical/vector fusion rewards broadly related troubleshooting pages, and the fixed top-five cutoff removes the exact installation or control page before answer generation.
6. **Per-case displacement:** E08/H10 ambient-temperature facts on Samsung page 27 lose to slow-dispenser, compressor, and general troubleshooting chunks; H02 pressure on GE page 20 loses to display and ice-maker troubleshooting; H07/H08 controls on Samsung page 37 lose to condensation, dispenser, and repair-guide chunks.
7. **Answer generation amplifies missing evidence:** E08, H08, and H10 hedge or abstain; H02 invents a **20–120 psi** range; H07 guesses “press” but omits the required three-second hold. E03 receives the correct XWFE location but adds unsupported troubleshooting from the two wrong tickets. Retrieval is the primary failure in all six; unsupported guessing or overreach is a secondary generation failure in E03, H02, and H07.
8. **Fragile manual-pool construction:** Lane B has 208 chunks, but the search currently loads an unordered cross-product pool with <code>LIMIT 200</code> before product filtering. All six expected facts happened to be present in the loaded pool in this run, so that cap did not cause these failures; nevertheless, SQL should apply lane + brand + OEM model before limiting and ranking.
9. **Historical lesson (20261026):** an empty manual filter inflated the earlier judge failures; [§5.3](#bnd-e01-e02) documents E01/E02 before M9. E01/E02 passed after brand+OEM filtering in the prior full-20 run.
10. **No separate report:** M90 post-M9 lives in <code>ops/runs/retail-lane-abcd-raw/m90-brand-model-20261027/</code> — document it in <code>TEST_ANALYSIS_A2_MANUAL_RAG_PG.md</code> when a headline row is needed (**33/60** answerable).

---

<h2 id="bnd-repro" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Reproduce</h2>

```bash
set -a && source .env && set +a
export PYTHONPATH="$PWD/scripts/retail:$PWD"
export RETAIL_LEXICAL_BACKEND=tantivy RETAIL_SIM_DATA_PROFILE=fru_us_1k

# Smoke (2 ids)
./scripts/py tests/retail_multi_profiles/run_bundled_qa.py --smoke --run-id b20-smoke

# Full B20
./scripts/py tests/retail_multi_profiles/run_bundled_qa.py --full --run-id b20-brand-model-YYYYMMDD
```

**Unit gates:**

```bash
./scripts/py -m pytest tests/retail/test_bundle_context.py tests/retail_multi_profiles/test_bundled_qa_suite.py -q
```

**Plan:** [`REFACTOR_BUNDLED_MANUAL_TICKET_QA.md`](../ref_plan/new/REFACTOR_BUNDLED_MANUAL_TICKET_QA.md) · **Parent:** [`REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md`](../ref_plan/new/REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md) minor **M4**.

---

<h2 id="bnd-evo18" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. EVO-18 run-profile comparisons (vs PRE-T0)</h2>

**Baseline (PRE-T0):** `b20-brand-model-20261027` — judge **14/20**, ticket-in-packet **10/20**, median ms: manual_retrieval **456**, answer **1504**, judge **1743**. Registry: [`REALIGNMENT_DIMENSIONS.md`](aggregated/REALIGNMENT_DIMENSIONS.md) §11.

| Profile | Run-id | Δ vs PRE-T0 | Judge | Ticket top-2 | Manual empty | Latency (med ms) | Notes |
|---------|--------|-------------|-------|--------------|--------------|------------------|-------|
| **PRE-T0** | `b20-brand-model-20261027` | — | 14/20 | 10/20 | 0/20 | 456 / 1504 / 1743 | overlap lexical; pool `LIMIT 200` then Python filter |
| **EVO18-T0** | `b20-evo18-t0-20261028` | SQL pool + manual Tantivy | **11/20** (−3 vs PRE-T0) | **10/20** (=) | **0/20** | **272 / 1626 / 1134** (faster manual leg) | Judge regressions on E03,E08,H02,H07,H08,H09 — ticket leg unchanged |
| **EVO18-D2-PAGE** | `b20-evo18-d2-page-20261028` | `page_heading` + global_top5 | **14/20** (= PRE-T0) | 10/20 | 0/20 | ~270 / ~1600 / ~1100 | M90 **42/60** (+9 vs PRE-T0) |
| **EVO18-D2-PACK-PAGE** | `b20-evo18-d2-pack-page-20261028` | + `page_top5` | **14/20** | 10/20 | 0/20 | similar | M90 **44/60** (best manual-only) |
| **EVO18-D7-DECOMPOSE** | `b20-evo18-d7-20261028` | + sentence D7 | **15/20** (+1 vs D2) | — | 0/20 | higher manual RTT | Six-row **`b20-evo18-d7-six-20261028`**: **3/6** (was 0/6) |

**Operator (EVO18-T0):** `RETAIL_MANUAL_LEXICAL_BACKEND=tantivy` · rebuild manual index · `./scripts/py tests/retail_multi_profiles/run_bundled_qa.py --full --run-id b20-evo18-t0-YYYYMMDD`
