<h1 id="fru-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Hybrid ticket search — Fridges R Us (US aftersales)</h1>

**Audience:** Engineers operating the FRU US service brain.  
**Phone-era evolution:** [`ABOUT_SEARCH_RRF_LEGACY_PHONE.md`](./ABOUT_SEARCH_RRF_LEGACY_PHONE.md).  
**Last updated:** 2026-10-15 (P9 operator ABC, Tantivy, `fru_us_1k` corpus).

## Document outline

1. [Executive summary](#fru-exec) — three modes; headline numbers.
2. [Business problem](#fru-problem) — intake, SKU, store, fault codes.
3. [Two retrieval legs](#fru-legs) — dense + lexical (Tantivy).
4. [Modes A/B/C](#fru-modes) — vector-only, RRF, term boost.
5. [Fusion math](#fru-math) — RRF + `FRU-E###` boost.
6. [Lexical leg](#fru-tantivy) — sidecar BM25 on ticket text.
7. [Eval design](#fru-eval) — 1000 natural + 100 tuned; ladder checker.
8. [Worked examples](#fru-examples) — one row per stratum from P9 reports.
9. [Results](#fru-results) — FRU 1k table (round 0).
10. [Config](#fru-config) — env + YAML.
11. [How we got here](#fru-history) — link legacy phone doc.
12. [Answer bundle](#fru-answer) — tickets + manual pages, live pre-run numbers.
13. [Next](#fru-next) — sales join on `customer_id`.

---

<h2 id="fru-exec" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Executive summary</h2>

Fridges R Us runs **three ticket-search modes** on **1000** historical US service tickets and **100** tuned eval intakes. On committed Postgres + Tantivy reports (eval retune **round 0**), overall **recall@1** is **0.25 → 0.44 → 0.54** for modes **A → B → C** (`check_abc_ladder.py` passes). Lexical backend: **`tantivy`**.

<h2 id="fru-problem" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. The business problem</h2>

Agents see customer prose, fridge SKU (`RF28K9070SG`, `GNE27JYMFS`, `KRFF507HPS`), store city, and sometimes **`FRU-E###`** fault codes. Past tickets repeat the same symptom at the same store — search must rank the right closed ticket without leaking customer ids into query text.

<h2 id="fru-legs" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Two retrieval legs</h2>

**Dense (pgvector)** on embedding-shaped text; **lexical (Tantivy)** on keyword-shaped text including diagnostic codes. Same mechanics as the phone prototype; examples use ice maker, door seal, and **`FRU-E###`**.

<h2 id="fru-modes" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Three search modes A/B/C</h2>

| Mode | Env | Role |
|------|-----|------|
| A | `vector_only` | Semantic baseline |
| B | `rrf_normal` | Fuse dense + lexical |
| C | `rrf_term_boosted` | B + extra mass when query code matches ticket code |

<h2 id="fru-math" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Mathematics of fusion</h2>

Reciprocal rank fusion (RRF) merges leg rankings; mode C adds a configurable boost when **`FRU-E###`** in the live query matches indexed ticket text. Details mirror legacy §9 (without phone-specific weights narrative).

<h2 id="fru-tantivy" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Lexical leg: Tantivy</h2>

Sidecar BM25 index; model filter on SKU. Six-engine comparison lives in [`ABOUT_SEARCH_RRF_LEGACY_PHONE.md`](./ABOUT_SEARCH_RRF_LEGACY_PHONE.md).

<h2 id="fru-eval" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Eval design</h2>

**Profile:** `fru_us_1k` → `sim_data/profiles/fru_us_1000_100/`. Historical CSV is frozen; only the **100** eval rows are retuned. Strata: **50** paraphrase / **30** hybrid_stress / **20** code_in_query. Gate: `scripts/retail/eval/check_abc_ladder.py`.

<h2 id="fru-examples" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. Worked examples</h2>

From P9 reports (`profiles/fru_us_1000_100/reports/`). **Rank@1** = gold ticket is top hit.

<h3 id="fru-ex-paraphrase" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">8.1 Paraphrase — mode B beats A (`eval-0003`)</h3>

**Live query:** `Detroit customer: KRFF507HPS — screen on the door will not respond to taps.`

**Gold ticket:** `T-0042-100524` — touch panel unresponsive on KRFF507HPS in Detroit (stored intake, not verbatim query).

| Mode | recall@1 on this row | Top ticket |
|------|----------------------|------------|
| A `vector_only` | miss | `T-0042-100342` |
| B `rrf_normal` | **hit** | **`T-0042-100524`** |

<h3 id="fru-ex-hybrid" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">8.2 Hybrid stress — mode B beats A (`eval-0063`)</h3>

**Live query:** Mis-pasted ice-maker checkout bait + open **temperature swings** on Los Angeles KRFF507HPS.

**Gold ticket:** `T-0042-100963` — temp fluctuation issue on that unit.

| Mode | recall@1 on this row | Top ticket |
|------|----------------------|------------|
| A `vector_only` | miss | `T-0042-100860` |
| B `rrf_normal` | **hit** | **`T-0042-100963`** |

<h3 id="fru-ex-code" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">8.3 Code in query — mode C beats B (`eval-0084`)</h3>

**Live query:** Wrong symptom (ice clumping) + **`FRU-E434`** on door panel for GNE27JYMFS in Dallas.

**Gold ticket:** `T-0042-100658` — post-outage warm fridge (indexed **`FRU-E434`** on stored text).

| Mode | recall@1 on this row | Top ticket |
|------|----------------------|------------|
| B `rrf_normal` | miss | `T-0042-100780` |
| C `rrf_term_boosted` | **hit** | **`T-0042-100658`** |

<h2 id="fru-results" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">9. Results</h2>

**Corpus:** `fru_us_1000_100` · **Eval retune rounds:** 0 · **Checker:** pass · **`lexical_backend`:** `tantivy` · **`total`:** 100

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Mode</th><th>Overall recall@1</th><th>paraphrase (50)</th><th>hybrid_stress (30)</th><th>code_in_query (20)</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">A <code>vector_only</code></td><td>0.25</td><td>0.26</td><td>0.30</td><td>0.15</td></tr>
<tr><td style="background:#e8f5e9">B <code>rrf_normal</code></td><td>0.44</td><td>0.56</td><td>0.43</td><td>0.15</td></tr>
<tr><td style="background:#fff3e0">C <code>rrf_term_boosted</code></td><td>0.54</td><td>0.56</td><td>0.43</td><td>0.65</td></tr>
</tbody>
</table>

Ladder rules: overall **A &lt; B &lt; C**; hybrid_stress **B &gt; A**; code_in_query **C &gt; B**.

<h2 id="fru-config" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">10. Config reference</h2>

```bash
export RETAIL_SIM_DATA_PROFILE=fru_us_1k
export RETAIL_MARKET=US
export RETAIL_FAULT_CODE_PREFIX=FRU-E
export RETAIL_LEXICAL_BACKEND=tantivy
```

YAML: `scripts/retail/config/fru_us_service.yaml`.

<h2 id="fru-history" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">11. How we got here</h2>

The Samsung AU phone corpus proved hybrid search and the ABC ladder; see [`ABOUT_SEARCH_RRF_LEGACY_PHONE.md`](./ABOUT_SEARCH_RRF_LEGACY_PHONE.md).

<h2 id="fru-answer" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">12. From search to an answer bundle</h2>

Ticket search is one leg of answering a **new** ticket. `scripts/retail/answer/answer_ticket.py` builds a deterministic **`retail_answer.v1`** JSON bundle with **both** legs, always:

- **`tickets.hits`** — top-2 resolved tickets for the same fridge model, each with `cosine_similarity` (query vs ticket embedding; comparable across queries) and `fused_score` (RRF score in modes B/C, `null` in A).
- **`manuals.hits`** — up to 3 passages, each citing `raw_origin.pdf_path` + `pages`. Source is the compiled LLM Wiki page when one is relevant for that model (`source: wiki`, frontmatter `sources:` → PDF, excerpt → page via the committed page index), else the PDF page text itself (`source: raw_pdf`).

No verdict field: a parser or an LLM summarizer reads the bundle and must keep every `ticket_id` and `pdf_path p.N`. Manual gold comes from author-owned `manual_anchors` per issue in the YAML (pages containing those phrases), not from the search's own output.

**Live pre-run (2026-10-15, 32 gold rows, wiki not yet compiled → raw PDF pages only):**

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Metric</th><th>paraphrase</th><th>hybrid_stress</th><th>code_in_query</th><th>no prior ticket</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Same-issue ticket in top-2 (C)</td><td>9/9</td><td>8/9</td><td>5/9</td><td>0 false claims / 5</td></tr>
<tr><td style="background:#e3f2fd">Exact gold ticket in top-2 (C)</td><td>5/9</td><td>5/9</td><td>5/9</td><td>—</td></tr>
<tr><td style="background:#e3f2fd">Manual page within ±1 of gold</td><td>9/9</td><td>7/9</td><td>6/7</td><td>4/5</td></tr>
</tbody>
</table>

"Same-issue" matters more than the exact source ticket: the corpus holds dozens of near-identical tickets per issue, and any of them carries the same fix.

<h2 id="fru-next" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">13. What comes next</h2>

Product path: wiki ingest + agent sidecar — [`REFACTOR_FRU_RETAIL_SERVICE_BRAIN.md`](../ref_plan/wip/REFACTOR_FRU_RETAIL_SERVICE_BRAIN.md). Join sales analytics on **`customer_id`**.
