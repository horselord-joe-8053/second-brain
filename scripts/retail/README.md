# Fridges R Us (US) retail scripts

- **`utils/retail_fru/`** (repo root) — **Gemini embeddings** + sidecar contract; **no mock fallback** (→ `utils/pg_rag/` in product plan V5).
- **`retail_brain/`** — hybrid search, eval, market profiles, **`fru_us_service.yaml`** loader.
- **`config/fru_us_service.yaml`** — FRU models, issues, eval phrasing templates.
- **`sim_data/profiles/fru_us_1000_100/`** — default **1000 + 100** corpus (`fru_us_1k`).
- **`sim_data/profiles/data_*`** — **phone archive** (Samsung AU); profile ids `rrf_data_llm_gen_1k`, `rrf_data_llm_gen_60_10`.
- **`retail_brain/sim_data_profile.py`** — **`RETAIL_SIM_DATA_PROFILE`** (default **`fru_us_1k`**). One profile active in Postgres at a time; **`reload_postgres_corpus.py`** TRUNCATE → load → embed.
- **`seed/validate_llm_corpus.py`** — corpus validator (FRU + phone dirs).
- **`eval/eval_ticket_search.py`** — A/B/C metrics; **`eval/check_abc_ladder.py`** — F15 gate.
- **`retail_brain/lexical_search/`** — keyword leg. **`RETAIL_LEXICAL_BACKEND=tantivy`** (default for FRU ABC).
- **`docker-compose.yml`** — Postgres + pgvector on port **5433**.

**Phone-era only (not default prep path):** `seed/generate_tickets.py`, `seed_narrative.py`, `abcd_demo_eval_spec.py`.

Env (repo `.env`): `GEMINI_API_KEY`, `EMBEDDING_MODEL`; **`RETAIL_SIM_DATA_PROFILE=fru_us_1k`**; **`RETAIL_MARKET=US`**; **`RETAIL_FAULT_CODE_PREFIX=FRU-E`**; `RETAIL_DATABASE_URL`; `RETAIL_TICKET_SEARCH_MODE` (`vector_only` | `rrf_normal` | `rrf_term_boosted`); `RETAIL_LEXICAL_BACKEND=tantivy`.

Operator prep: `cursor_gen/retail_v11_prep/03_pg_up_and_load.sh`, `05_run_abc_postgres.sh`. Spec: [`docs/specs/fru-us-service-synthetic-data.md`](../../docs/specs/fru-us-service-synthetic-data.md).
