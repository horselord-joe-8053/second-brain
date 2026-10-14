# Samsung retail scripts

- **`utils/retail_fru/`** (repo root) — **Gemini embeddings** + FRU sidecar contract; **no mock fallback**.
- **`retail_brain/`** — seed, hybrid search, eval (import with `PYTHONPATH=scripts/retail` + repo root for `utils`).
- **`seed/generate_tickets.py`** — synthetic CSV + manifest (**`rrf_data_prag_gen`** profile).
- **`seed/generate_eval_from_manifest.py`** — strict eval JSONL (`expected_ticket_ids = [source]`).
- **`retail_brain/sim_data_profile.py`** — **`RETAIL_SIM_DATA_PROFILE`**: `rrf_data_llm_gen_1k` (default, `sim_data/profiles/data_1000_100/`), `rrf_data_llm_gen_60_10` (alias `rrf_data_llm_gen`), vs `rrf_data_prag_gen` (`seed/generated/`). One profile active in Postgres at a time; **`reload_postgres_corpus.py`** TRUNCATE → load → embed.
- **`seed/generate_llm_corpus_v2.py`** + **`seed/validate_llm_corpus.py`** — natural llm_gen corpus (60+10); validator runs in `verify-local.sh` when CSV present.
- **`seed/llm_author_gold.py`** — **offline only** optional `acceptable_ticket_ids` (not runtime eval).
- **`eval/eval_ticket_search.py`** — V1/V1.1 metrics (`RETAIL_TICKET_HYBRID_SEARCH`).
- **`retail_brain/lexical_search/`** — keyword leg. `RETAIL_LEXICAL_BACKEND=tantivy` (default), `bm25x`, `parade_db`, or `open_search`. Postgres stays the ticket store. See that folder's README.
- **`docker-compose.yml`** — optional Postgres + pgvector on port 5433.

Env (repo `.env`): `GEMINI_API_KEY`, `EMBEDDING_MODEL` (e.g. `gemini-embedding-2`); **`RETAIL_MARKET=AU|BR`** (default **AU** — drives synthetic copy, eval paraphrases, and Postgres `to_tsvector` / `plainto_tsquery` config); **`RETAIL_SIM_DATA_PROFILE=rrf_data_llm_gen|rrf_data_prag_gen`** (which CSV/eval/reports tree to use); `RETAIL_DATABASE_URL`, `RETAIL_TICKET_SEARCH_MODE` / `RETAIL_TICKET_HYBRID_SEARCH`, `RETAIL_SIDECAR_URL` (when HTTP sidecar is deployed).
