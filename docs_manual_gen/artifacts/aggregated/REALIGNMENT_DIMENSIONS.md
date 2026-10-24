<h1 id="dim-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Benchmark dimensions — FRU Second Brain search &amp; Q&amp;A</h1>

**Purpose:** Name **orthogonal knobs** so each implementation (done or planned) is one **run profile**, comparable on the **same test contract** when dimensions match.  
**Companion plans:** [`REFACTOR_FURTHER_ENHANCEMENT_GPT.md`](../../ref_plan/new/REFACTOR_FURTHER_ENHANCEMENT_GPT.md) · [`REALIGNMENT_REFACTOR_GOALS.md`](./REALIGNMENT_REFACTOR_GOALS.md) · [`AGGREGATED_TEST_ANALYSIS_LLM_WIKI_AND_RAG.md`](./AGGREGATED_TEST_ANALYSIS_LLM_WIKI_AND_RAG.md).

<h2 id="dim-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Part 1 — Is your summary right?](#dim-part1) — validate A/B manual + ticket work.
2. [Dimension definitions](#dim-defs) — D1–D6 (optimized from your D1–D3).
3. [D2 manual lanes](#dim-d2) — A/B/C/D registry.
4. [D3 retrieval catalog](#dim-d3) — ticket, wiki, raw arms.
5. [Run profile idea](#dim-profiles) — config/compare by combo.
6. [Table 2.1 — Implemented &amp; tested](#dim-t21) — what exists today.
7. [Table 2.2 — Planned refactor phases](#dim-t22) — GPT plan items.
8. [Cross-dimension notes](#dim-notes) — common confusions.
9. [Next step for harness](#dim-harness) — one config object.
10. [Experiment policy](#dim-experiment) — one-Δ rule (avoid grid explosion).

---

<h2 id="dim-part1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Part 1 — Is your summary right?</h2>

**Mostly yes**, with a few **important corrections** so dimensions stay honest.

<h3 id="dim-part1-a" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">1.1 A — Historical ticket Q&amp;A</h3>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Your statement</th><th>Verdict</th><th>Precision</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Benchmark for <strong>3 fridge models</strong></td><td style="background:#fff3e0">⚠ Partly</td><td>Suite uses those SKUs often, but eval is <strong>100 tuned queries</strong> on <strong>1k</strong> ticket corpus (<code>fru_us_1k</code>), not the same <strong>90-Q</strong> manual suite.</td></tr>
<tr><td style="background:#e3f2fd">RRF (vector + lexical + lambda)</td><td style="background:#e8f5e9">✓</td><td>Modes <strong>A/B/C</strong>: <code>vector_only</code> → <code>rrf_normal</code> → <code>rrf_term_boosted</code> (<strong>FRU-E###</strong> boost, your “lambda”). BM25-like leg = <strong>Tantivy</strong> sidecar.</td></tr>
<tr><td style="background:#e3f2fd">Historical tickets as raw base</td><td style="background:#e8f5e9">✓</td><td><strong>System of record:</strong> Postgres <code>service_queries</code> + vectors + Tantivy index. Loaded from CSV in prep scripts.</td></tr>
<tr><td style="background:#e3f2fd">Raw base is .txt or jsonl list</td><td style="background:#ffcdd2">✗</td><td><strong>JSONL</strong> (<code>ticket_retrieval.jsonl</code>) is <strong>eval gold only</strong> (query + expected ticket ids). Search index is <strong>not</strong> a flat ticket file list.</td></tr>
</tbody>
</table>

**Metric:** recall@1 / recall@3 on retrieval — **not** LLM answer+judge pass rate (unless you add that later).

<h3 id="dim-part1-b" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">1.2 B — Manual Q&amp;A (90 questions × 3 models)</h3>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Your statement</th><th>Verdict</th><th>Precision</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>B1</strong> LLM Wiki, lanes A–D, manuals as base</td><td style="background:#e8f5e9">✓</td><td>Harness <code>retrieval_mode=llm_wiki</code>; search hits <code>wiki/**</code> (hybrid + graph inside LLM Wiki). <strong>360 rows</strong> = 90×4 lanes.</td></tr>
<tr><td style="background:#e3f2fd"><strong>B2</strong> RAG on lanes B,C,D</td><td style="background:#fff3e0">⚠</td><td>Done arm is <strong>raw vector RAG only</strong> (Lance on <code>raw/sources/**</code>) — <strong>no RRF on raw yet</strong>. Lane A raw disabled.</td></tr>
<tr><td style="background:#e3f2fd"><strong>B3</strong> Raw beats wiki on B &amp; C; wiki slightly ahead on D</td><td style="background:#e8f5e9">✓</td><td>Overall pass rate (90 Q): B <strong>+21.1</strong> pt, C <strong>+28.9</strong> pt raw; D wiki <strong>67.8%</strong> vs raw <strong>65.6%</strong> (−2.2 pt). Answerable (60): D wiki <strong>31</strong> vs raw <strong>~29</strong> — “slightly ahead,” raw much faster.</td></tr>
</tbody>
</table>

**Naming fix:** Compare **B1 = wiki hybrid** vs **B2 = raw dense** — not “RAG+RRF” vs wiki until Phase 1 lands **D3.R-H** on raw.

---

<h2 id="dim-defs" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Dimension definitions</h2>

Your three dimensions become **six** so ticket vs manual vs future corpora do not collide, and **harness** vs **retrieval** are separable.

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Dim</th><th>Name</th><th>Question it answers</th><th>When N/A</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>D1</strong></td><td><strong>Knowledge corpus</strong></td><td>Which <strong>company data domain</strong> is searched?</td><td>—</td></tr>
<tr><td style="background:#e3f2fd"><strong>D2</strong></td><td><strong>Manual preparation lane</strong></td><td>In what <strong>shape</strong> were product PDFs prepared before ingest/RAG?</td><td>D1 ≠ product manuals</td></tr>
<tr><td style="background:#e3f2fd"><strong>D3</strong></td><td><strong>Retrieval engine</strong></td><td>How are candidates <strong>ranked</strong> (legs + fusion + boosts)?</td><td>—</td></tr>
<tr><td style="background:#e3f2fd"><strong>D4</strong></td><td><strong>Evidence surface</strong></td><td>Where do hit records live (what store is queried)?</td><td>Mostly implied by D1+D3 path</td></tr>
<tr><td style="background:#e3f2fd"><strong>D5</strong></td><td><strong>Post-retrieval stack</strong></td><td>After top-k: rerank, verify, agentic re-search?</td><td>Default <code>none</code> today</td></tr>
<tr><td style="background:#e3f2fd"><strong>D6</strong></td><td><strong>Evaluation contract</strong></td><td>Which benchmark and metric (same questions for fair compare)?</td><td>—</td></tr>
</tbody>
</table>

<h3 id="dim-d1-values" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.1 D1 — Knowledge corpus (your D1, expanded)</h3>

| Code | Label | Examples in FRU repo |
|------|--------|----------------------|
| **D1.T** | Historical service tickets | Closed cases, resolutions, `FRU-E###` |
| **D1.M** | Product information documents | Manuals, repair guides (origin PDF) |
| **D1.S** | Sales / CRM *(future)* | Ultra-FRU sales join on `customer_id` |
| **D1.O** | Operational playbooks *(future)* | Theme exports → wiki playbooks |
| **D1.P** | Policy / warranty legal *(future)* | Not indexed yet |

**Note:** **Compiled LLM Wiki** is not a separate D1 — it is **D1.M** material presented through **D4.W** (wiki store) with **D3.W** engine.

<h3 id="dim-d2-values" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.2 D2 — Manual preparation lane (your D2)</h3>

Applies when **D1.M** (including wiki ingest **and** raw RAG glob for that lane). Registry: `config/retail-ingest-lanes.yaml`.

| Code | Lane | Preparation (starting point for search) |
|------|------|----------------------------------------|
| **D2.A** | A | Original PDF via in-app LLM Wiki ingest |
| **D2.B** | B | Per-page Markdown (+ page screenshots in corpus) |
| **D2.C** | C | Plain text extract from PDFs (`user-guide.txt` style) |
| **D2.D** | D | Technician-style Markdown shards (**Prompt C v4**) |

<h3 id="dim-d3-values" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.3 D3 — Retrieval engine (your D3, split by surface)</h3>

See [§4 catalog](#dim-d3). Ticket **A/B/C** map to your **D3.A / D3.B**. Raw **RRF** is **planned**, not shipped.

<h3 id="dim-d4-values" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.4 D4 — Evidence surface</h3>

| Code | Store | Typical hit |
|------|--------|-------------|
| **D4.PG** | Postgres + pgvector | Ticket row |
| **D4.LX** | Tantivy sidecar | Ticket id (lexical leg) |
| **D4.W** | LLM Wiki project | Wiki page path |
| **D4.LC** | Lance `.retail-raw-rag/` | Chunk of `raw/sources/**` |

<h3 id="dim-d5-values" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.5 D5 — Post-retrieval stack</h3>

| Code | Layer |
|------|--------|
| **D5.0** | None (retrieve → answer) |
| **D5.R** | Listwise LLM rerank on candidate list |
| **D5.V** | EvidenceVerifier (coverage / applicability / claim check) |
| **D5.A** | AgenticRetrievalController (bounded extra search) |
| **D5.C** | COS router (provisional vs evidence-backed) |

Stacks compose: e.g. **D5.R+V+A** = rerank then verify then one re-query.

<h3 id="dim-d6-values" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.6 D6 — Evaluation contract</h3>

| Code | Suite | Metric |
|------|--------|--------|
| **D6.T100** | `ticket_retrieval.jsonl` (100 rows) | recall@1, recall@3, stratum splits |
| **D6.M90** | `retail-manual-qa-test-suite.json` (90×lanes) | Judge pass overall / answerable(60) / strata |
| **D6.REPLAY** | Sources-only replay subset | Pass count on fixed ticket subset |
| **D6.AUDIT** | Wiki claim registry | Unsupported / contradicted rates |

**Fair compare rule:** Same **D6** + same **D2** lane (if manual) + same **D1** — only vary **D3** and/or **D5**.

---

<h2 id="dim-d2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. D2 manual lanes (quick reference)</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Lane</th><th>Brain path</th><th>Wiki ingest kind</th><th>Raw RAG glob (D4.LC)</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>A</strong></td><td><code>brain/retail</code></td><td>pdf_in_app</td><td><span style="background:#ffcdd2;padding:2px 4px">disabled</span></td></tr>
<tr><td style="background:#e3f2fd"><strong>B</strong></td><td><code>brain/retail-md</code></td><td>external_markdown</td><td><code>fridge-docs_md/**/*.md</code></td></tr>
<tr><td style="background:#e3f2fd"><strong>C</strong></td><td><code>brain/retail-txt</code></td><td>external_text</td><td><code>fridge-docs/**/*.txt</code></td></tr>
<tr><td style="background:#e3f2fd"><strong>D</strong></td><td><code>brain/retail-md-learned</code></td><td>learned_markdown</td><td><code>fridge-docs-split-less/**/*.md</code></td></tr>
</tbody>
</table>

Lanes are **experimental LLM Wiki projects** — not the same switch as `BRAIN_PROFILE`.

---

<h2 id="dim-d3" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. D3 retrieval catalog</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Code</th><th>Legs</th><th>D4</th><th>Status</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>D3.T-A</strong></td><td>Dense only</td><td>D4.PG</td><td style="background:#e8f5e9">✓ ticket eval mode A</td></tr>
<tr><td style="background:#e3f2fd"><strong>D3.T-B</strong></td><td>Dense + lexical → RRF</td><td>D4.PG + D4.LX</td><td style="background:#e8f5e9">✓ mode B</td></tr>
<tr><td style="background:#e3f2fd"><strong>D3.T-C</strong></td><td>RRF + diagnostic code boost</td><td>D4.PG + D4.LX</td><td style="background:#e8f5e9">✓ mode C (prod default)</td></tr>
<tr><td style="background:#e3f2fd"><strong>D3.W-H</strong></td><td>Wiki lexical + dense + RRF + graph slot</td><td>D4.W</td><td style="background:#e8f5e9">✓ manual wiki arm</td></tr>
<tr><td style="background:#e3f2fd"><strong>D3.R-V</strong></td><td>Dense vector on raw chunks</td><td>D4.LC</td><td style="background:#e8f5e9">✓ raw RAG baseline</td></tr>
<tr><td style="background:#e3f2fd"><strong>D3.R-H</strong></td><td>BM25/Tantivy or Lance keyword + vector → RRF, SKU filter</td><td>D4.LC</td><td style="background:#e8f5e9">✓ P1.1 Lane B (34/60 interim)</td></tr>
<tr><td style="background:#e3f2fd"><strong>D5.R</strong> (not D3)</td><td>Listwise rerank on any D3 pool</td><td>same D4</td><td style="background:#fff3e0">library ✓; harness **llm_listwise** open (P1.2b)</td></tr>
</tbody>
</table>

---

<h2 id="dim-profiles" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Run profile idea — does your config goal make sense?</h2>

**Yes.** Treat a **run profile** as a named tuple:

```text
profile_id = (D1, D2?, D3, D4, D5, D6, lane?)
```

Examples:

| profile_id | Meaning |
|------------|---------|
| `TICKET|T|D3.T-C|PG+LX|0|T100|` | Ticket hybrid + code boost, standard eval |
| `MANUAL|M|D2.B|D3.W-H|W|0|M90|B` | Lane B LLM Wiki full harness |
| `MANUAL|M|D2.B|D3.R-V|LC|0|M90|B` | Lane B raw vector (done) |
| `MANUAL|M|D2.B|D3.R-H|LC|R+V+A|M90|B` | Phase 1 target on lane B |

**Compare fairly:** hold **D6** and **D2** fixed, sweep **D3** and **D5**.  
**Do not** compare `D6.T100` to `D6.M90` directly — different questions.

**Harness (partial → P1.0b):** YAML **`run_profiles:`** in `tests/retail_multi_profiles/data/run-config.yaml` maps informal ids → **D3** today; **D5** must live on each profile block (**R18–R20** in GPT plan).

**Implementer / operator doc:** [`RUN_PROFILES.md`](../../../tests/retail_multi_profiles/docs/RUN_PROFILES.md) — **`ResolvedRunProfile`**, `d5.rerank.enabled` (off switch) + `d5.rerank.backend` (default **`llm_listwise`** when enabled), env overrides, pre-flight.

**Target profile shape (Lane B raw — illustrative):**

```yaml
MANUAL_B_RAW_HYBRID_RERANK:
  retrieval_mode: raw_rag
  raw_retrieval: hybrid_rrf          # D3.R-H only
  lanes: B
  d5:
    rerank:
      enabled: true
      backend: llm_listwise          # D5.R — not a separate D3 engine name
    verifier:
      enabled: true                  # D5.V
    agentic:
      enabled: true
      max_loops: 1                   # D5.A (R4)
```

**Legacy mistake:** treating `raw_retrieval: hybrid_rrf_rerank` as “rerank on” without **`d5.rerank`** + wired **`rank_fn`** — rerank was a no-op in interim **v1** runs (**R21**).

---

<h2 id="dim-t21" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Table 2.1 — Implemented &amp; tested</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>ID</th><th>Description</th><th>D1</th><th>D2</th><th>D3</th><th>D4</th><th>D5</th><th>D6</th><th>Operator / artifact</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>IMP-T-ABC</strong></td><td>Ticket search A/B/C ladder</td><td>D1.T</td><td>—</td><td>T-A / T-B / T-C</td><td>PG+LX</td><td>D5.0</td><td>D6.T100</td><td><code>05_run_abc_postgres.sh</code> · ABOUT_SEARCH_RRF_FRU</td></tr>
<tr><td style="background:#e3f2fd"><strong>IMP-M-WIKI-ABCD</strong></td><td>LLM Wiki manual Q&amp;A all lanes</td><td>D1.M</td><td>A–D</td><td>D3.W-H</td><td>D4.W</td><td>D5.0</td><td>D6.M90</td><td><code>abcd-full-openai-v2</code></td></tr>
<tr><td style="background:#e3f2fd"><strong>IMP-M-RAW-BCD</strong></td><td>Raw vector RAG manual Q&amp;A</td><td>D1.M</td><td>B,C,D</td><td>D3.R-V</td><td>D4.LC</td><td>D5.0</td><td>D6.M90</td><td><code>abcd-raw-full-openai-v1</code></td></tr>
<tr><td style="background:#e3f2fd"><strong>IMP-M-REPLAY</strong></td><td>Wiki sources-only replay (subset)</td><td>D1.M</td><td>B,D</td><td>D3.W-H + page filter</td><td>D4.W</td><td>D5.0</td><td>D6.REPLAY</td><td><code>sources_only_replay.py</code></td></tr>
<tr><td style="background:#e3f2fd"><strong>IMP-BUNDLE</strong></td><td><code>retail_answer.v1</code> ticket+manual JSON</td><td>T+M</td><td>retail txt path</td><td>T-C + wiki</td><td>PG+W</td><td>D5.0</td><td>CI E2E</td><td>brain-profiles plan</td></tr>
</tbody>
</table>

---

<h2 id="dim-t22" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Table 2.2 — Planned refactor (GPT plan phases)</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Plan item</th><th>Phase</th><th>D1</th><th>D2</th><th>D3 Δ</th><th>D5 Δ</th><th>D6</th><th>Primary lane (R10)</th></tr>
</thead>
<tbody>
<tr><td style="background:#e8f5e9"><strong>P1.1</strong> Retriever core</td><td>1 A2</td><td>D1.M</td><td>B (→C smoke)</td><td>→ <strong>D3.R-H</strong></td><td>D5.0</td><td>D6.M90</td><td>B</td></tr>
<tr><td style="background:#e8f5e9"><strong>P1.2</strong> Listwise rerank</td><td>1</td><td>D1.M</td><td>B</td><td>→ D3.R-H + <strong>RR</strong></td><td>+D5.R</td><td>D6.M90</td><td>B</td></tr>
<tr><td style="background:#e8f5e9"><strong>P1.3–P1.4</strong> Evidence + agentic</td><td>1</td><td>D1.M</td><td>B</td><td>R-H + RR</td><td>+D5.V + <strong>D5.A</strong></td><td>D6.M90</td><td>B</td></tr>
<tr><td style="background:#fff3e0"><strong>P2.1–P2.4</strong> Ticket adapters</td><td>2 A3</td><td>D1.T</td><td>—</td><td>T-C + optional RR</td><td>+V (+A)</td><td>D6.T100</td><td>—</td></tr>
<tr><td style="background:#fff3e0"><strong>P3.1–P3.2</strong> Wiki claim audit</td><td>3 A1</td><td>D1.M</td><td>B</td><td>— (offline)</td><td>+V (claims)</td><td><strong>D6.AUDIT</strong></td><td>B</td></tr>
<tr><td style="background:#fff3e0"><strong>P3.3–P3.5</strong> wiki_evidence modes</td><td>3</td><td>D1.M</td><td>B</td><td>W-H + filter / RR</td><td>+R (+V)</td><td>D6.M90</td><td>B</td></tr>
<tr><td style="background:#ffebee"><strong>P4.1–P4.3</strong> COS + API</td><td>4 B</td><td>T+M</td><td>B</td><td>multi</td><td>+<strong>D5.C</strong> + wiki_leads</td><td>demo scripts</td><td>—</td></tr>
</tbody>
</table>

**Track labels (A1/A2/A3/B)** = **product ownership**, not extra dimensions: each track picks **(D1, D3, D5)** policies.

---

<h2 id="dim-notes" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. Cross-dimension notes</h2>

1. **D2 ≠ D3:** Lane B per-page MD can use **wiki hybrid (D3.W-H)** or **raw vector (D3.R-V)** on **different files** (`wiki/**` vs `raw/sources/**`).
2. **“RRF on manuals”** today = **wiki only**. Raw **D3.R-H** is the main Phase 1 engineering gap.
3. **Tickets never use D2** — use **model_filter** and code boost instead of manual lanes.
4. **Lane D later:** still valid for **D2.D** experiments; promotion baseline is **D2.B** per grill **G4**.
5. **BM25:** Tantivy on tickets and (planned) keyword leg on raw; wiki has its own lexical leg — not one shared BM25 index across all D1.

---

<h2 id="dim-harness" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">9. Next step for harness (optional P1.0)</h2>

Before more modes proliferate, add **`run_profiles.yaml`** (or extend `run-config.yaml`) with:

- **`profile_id`**
- dimension columns **D1–D6**
- resolved CLI/env for `tests.retail_multi_profiles` and `eval_ticket_search.py`

Then analysis docs reference **profile_id**, not ad-hoc run names only.

**Related refactor plan section:** [Dimension-led map](../../ref_plan/new/REFACTOR_FURTHER_ENHANCEMENT_GPT.md#gpt-dim-map).

---

<h2 id="dim-experiment" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">10. Experiment policy</h2>

1. **One Δ per run** — change only **D3** or **D5** (or one **D2** lane switch), never several at once.
2. **Fix D6 + D2 + D1** before comparing rankers.
3. **Retrieval screen → judged confirm** — smoke or recall@k before full **D6.M90** LLM judge.
4. **Register every run** — `profile_id` in ops JSONL even before YAML automation (Phase **P1.0**).
5. **Separate optimum per D1** — ticket best ≠ manual best ≠ COS route.
6. **Phase exit trio** (plan **R15**): smoke → full **D6** benchmark → analysis doc with **profile_id** + delta vs last comparable run.
