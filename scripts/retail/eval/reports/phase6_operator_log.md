<h1 id="p6-log" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Phase 6 operator log (Postgres A/B shakedown)</h1>

**When:** 2026-10-10 (local)  
**Corpus:** `COUNT=90`, `SEED=42` → 90 PG rows, 67 eval cases  
**Embeddings:** Gemini `gemini-embedding-2`, dim 768  

<h2 id="p6-snapshot" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">DB snapshot (6.8)</h2>

| Field | Value |
|-------|--------|
| `RETAIL_DATABASE_URL` | `postgresql://retail:retail@127.0.0.1:5433/retail` |
| `service_queries` rows | 90 (67 resolved, 23 received) |
| `service_queries.csv` bytes | 20975 |
| PDFs copied | 6 under `brain/retail/raw/sources/samsung-docs/{a15,a16,a25}/` |

<h2 id="p6-ab" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">A/B results (6.9–6.10)</h2>

**Latest (Phase 5 deterministic narrative seed, `03` reload + re-embed, 2026-10-11):**

| Mode | recall@1 | lexical leg |
|------|----------|-------------|
| V1 vector | 0.836 | n/a |
| V1.1 hybrid | 0.851 | **67/67** nonempty |

Reports: `pg_baseline_v1.json`, `pg_ab_v1_v11.json`. Modest hybrid lift on realistic prose (no store/case-ref tokens in text). **90-ticket shakedown** — not D6 promotion.

**Prior runs:** pre–5.1 ID-in-prose cabinet (misleading hybrid lift); pre-normalize lexical 0/67.

**D6:** 90-ticket shakedown only — re-run at 500+ scale + optional `llm_author_gold.py` before changing defaults.

<h2 id="p6-waivers" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Waivers / fixes this run</h2>

- **6.5 Hermes wiki:** waived — ticket A/B does not use wiki index (D11).
- **HG-PY-PG:** `psycopg2-binary` installed on operator host for `03`.
- **Code fixes:** empty `closed_at` CSV → NULL in loader; Postgres eval loads repo `.env` for query embeddings.
