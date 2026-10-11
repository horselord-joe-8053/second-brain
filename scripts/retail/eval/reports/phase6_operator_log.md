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

<h2 id="p6-ab-v1x" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Production-shaped V1.1–V1.3 (same PG snapshot)</h2>

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
