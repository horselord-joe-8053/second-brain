<h1 id="p6-log" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Phase 6 operator log (Postgres A/B shakedown)</h1>

**When:** 2026-10-11 (stage-1 hybrid demo corpus)  
**Corpus:** `COUNT=90`, `SEED=42` → 67 eval cases  
**Embeddings:** Gemini **document** = customer prose only (`text_for_embedding` strips tech line); **query** = live intake text (includes error code on `error_code` stratum)

<h2 id="p6-ab-stage1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Latest A/B — paired twins + error-code stratum</h2>

| Mode | recall@1 (strict) | lexical leg |
|------|-------------------|-------------|
| V1 vector | **0.567** (38/67) | — |
| V1.1 hybrid | **0.672** (45/67) | **44/67** nonempty |

**By stratum:**

| Stratum | n | Vector | Hybrid | Notes |
|---------|---|--------|--------|-------|
| `error_code` | 7 | **0/7** | **7/7** | Vector top-1 = intake-shaped **twin**; lexical + RRF → **gold** |
| `paraphrase` | 55 | 33/55 | 33/55 | Unchanged vs vector on this slice |
| `literal_token` | 5 | 5/5 | 5/5 | — |

**Hybrid-only wins (7):** all `error_code` — vector ranked `T-…-(gold+1)`; hybrid ranked gold (`eval-0006`, `eval-0018`, `eval-0030`, `eval-0042`, `eval-0054`, `eval-0066`, `eval-0078`).

Reports: `pg_baseline_v1.json`, `pg_ab_v1_v11.json`.

**Read:** Stage-1 fixture shows **hybrid beats vector overall** driven by **`error_code`** rows where **vector misses** (twin intake shape) and **lexical hits** (code in query ↔ tech line in FTS). RRF **lexical tie-break** on equal fusion score avoids losing those rows when vector and lexical both rank gold at rank 2.

<h2 id="p6-ab-v1x" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Production-shaped V1.1–V1.3 (same PG snapshot) — historical</h2>

*Four-mode era (includes removed `rrf_weighted`). Current operator ladder: [three-mode collapse](#p6-three-modes).*

**When:** 2026-10-12  
**Modes:** `RETAIL_TICKET_SEARCH_MODE` = `vector_only` | `rrf_normal` | `rrf_weighted` | `rrf_weighted_boosted`  
**Script:** `cursor_gen/retail_v11_prep/05_run_abcd_postgres.sh`

| Mode | recall@1 | error_code (7) |
|------|----------|----------------|
| `vector_only` | 0.567 | 0/7 |
| `rrf_normal` | 0.567 | 0/7 |
| `rrf_weighted` | 0.567 | 0/7 |
| `rrf_weighted_boosted` | **0.672** | **7/7** |

Reports: `pg_baseline_v1.json`, `pg_ab_v1_1_normal.json`, `pg_ab_v1_2_weighted.json`, `pg_ab_v1_3_boosted.json`.

**Read:** Rich FTS + equal or 70/30 RRF **does not** recover `error_code` until **V1.3 code boost (λ=10)** — matches D18 acceptance. V1.3 aligns with stage-1 hybrid headline without demo-era tech-line-only FTS rewrite.

<h2 id="p6-llm-v2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Natural LLM corpus v2 (`rrf_data_llm_gen`)</h2>

**When:** 2026-10-12  
**Corpus:** 60 tickets / 10 eval — `generate_llm_corpus_v2.py`; SAM-E in **embed**; no twin clones  
**Profile:** `RETAIL_SIM_DATA_PROFILE=rrf_data_llm_gen`

| Mode | recall@1 | lexical_nonempty |
|------|----------|------------------|
| vector_only | **1.00** (10/10) | — |
| rrf_normal | **1.00** | 0/10 |
| rrf_weighted | **1.00** | 0/10 |
| rrf_weighted_boosted | **1.00** | 0/10 |

Reports: `tmp/simulated_data/reports/pg_*.json`

**Read:** All modes tie at **N=10** after embed policy fix; **lexical leg still inactive** on paraphrase eval wording. Use **prag_gen** + larger N for mode differentiation until BM25/Qdrant lands.

<h2 id="p6-lexical-matrix" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Lexical backend matrix (four engines × A/B/C/D)</h2>

**When:** 2026-10-12  
**Script:** `cursor_gen/retail_v11_prep/06_run_abcd_lexical_matrix.sh`  
**Summary:** `tmp/simulated_data/reports/lexical_matrix/lexical_matrix_summary.md`

| Backend | rrf_normal recall@1 | lexical_nonempty |
|---------|---------------------|------------------|
| tantivy (default) | 0.800 | 10/10 |
| bm25x | 0.800 | 10/10 |
| parade_db | 0.800 | 10/10 |
| open_search | 0.800 | 10/10 |

**Read:** On **llm_gen** with Tantivy/bm25x/Parade/OpenSearch keyword legs, hybrid modes **activate the lexical leg** (10/10) vs earlier PG-FTS run (0/10). Recall@1 on **rrf_normal** is **0.800** for all four backends on this snapshot — keyword engine choice did not change top-1 on N=10.

<h2 id="p6-demo-abcd" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Demo eval A/B/C/D (historical four-mode ladder)</h2>

<span style="background:#fff9c4;padding:2px 6px">**Superseded:** current ABC + P4 eval wording — [three-mode collapse](#p6-three-modes) and [P4 product-story](#p6-p4-product-story).</span>

**When:** 2026-10-14  
**Eval:** `abcd_demo_eval_spec.py` → `tmp/simulated_data/ticket_retrieval.jsonl` (eval-only; 60-row CSV unchanged)  
**Lexical:** `RETAIL_LEXICAL_BACKEND=tantivy`  
**Script:** `05_run_abcd_postgres.sh` (legacy → `05_run_abc_postgres.sh`)

| Arm | Mode | recall@1 | lexical_nonempty |
|-----|------|----------|------------------|
| A | `vector_only` | **0.80** (8/10) | — |
| B | `rrf_normal` | **0.80** | 10/10 |
| C | `rrf_weighted` | **0.80** | 10/10 |
| D | `rrf_weighted_boosted` | **1.00** (10/10) | 10/10 |

**Vector-only misses:** `eval-0001` (gold `T-0042-000000`, dense top `T-0042-000042`), `eval-0005` (gold `T-0042-000030`, dense top `T-0042-000012`). **D-only recovery:** SAM-E in query + V1.3 λ; B/C keep bait at rank 1.

**Recommendation:** To show **B** (equal RRF) and **C** (70/30) lifting before λ, author intakes where gold is **lexical top-1** but **vector rank ≥ 3** and **no SAM-E** in the query (pure fusion story), or inject additional historical neighbors so bait no longer wins the lexical leg.

<h3 id="p6-demo-abcd-p4" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">P4 re-run (fusion ladder retune, 2026-10-14)</h3>

| Arm | recall@1 | Notes |
|-----|----------|-------|
| A | **0.80** | Miss `eval-0001`, `eval-0005` (dense neighbor #1) |
| B | **1.00** | Equal RRF + lexical #1 on gold fixes both |
| C | **0.80** | **H10:** 70/30 reverts same two rows (vector bait wins dense) |
| D | **1.00** | SAM-E λ on `eval-0001` / `eval-0005` + code-stratum rows |

**C &lt; B regression (2 rows):** `eval-0001` vector top `T-0042-000042` vs gold `T-0042-000000`; `eval-0005` vector top `T-0042-000012` vs gold `T-0042-000030`. Lexical leg ranks gold first on both after P4 wording.

<h2 id="p6-three-modes" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Three-mode collapse (V1 / V1.1 / V1.2)</h2>

**When:** 2026-10-14  
**Change:** Removed `rrf_weighted` (70/30). Renamed **`rrf_weighted_boosted` → `rrf_term_boosted`**; hybrid modes use **equal RRF**; only V1.2 adds SAM-E λ.  
**Script:** `05_run_abc_postgres.sh`

| Arm | Mode | recall@1 |
|-----|------|----------|
| A | `vector_only` | **0.50** (5/10) |
| B | `rrf_normal` | **0.80** (8/10) |
| C | `rrf_term_boosted` | **1.00** (10/10) |

**Read:** Strict **A &lt; B &lt; C** on demo eval; term boost lifts `eval-0003` / `eval-0010` where equal RRF still tops the wrong neighbor.

<h3 id="p6-p4-product-story" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">P4 product-story eval (2026-10-14)</h3>

**Plan:** `REFACTOR_RETAIL_SEARCH_THREE_MODES.md` §4.1. **Eval-only** retune of `hybrid_stress` rows: **open issue** + **closed/mis-route bait** (not two equal open complaints). **No SAM-E** on B rows.

| Arm | recall@1 |
|-----|----------|
| A | **0.50** |
| B | **0.80** |
| C | **1.00** |

**B lift:** `eval-0001`, `eval-0005`, `eval-0007` — vector leg tops lookalike neighbor; lexical + RRF tops gold.
