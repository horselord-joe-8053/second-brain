# Samsung retail scripts

- **`utils/retail_fru/`** (repo root) — **Gemini embeddings** + FRU sidecar contract; **no mock fallback**.
- **`retail_brain/`** — seed, hybrid search, eval (import with `PYTHONPATH=scripts/retail` + repo root for `utils`).
- **`seed/generate_tickets.py`** — synthetic CSV + manifest.
- **`seed/generate_eval_from_manifest.py`** — strict eval JSONL (`expected_ticket_ids = [source]`).
- **`seed/llm_author_gold.py`** — **offline only** optional `acceptable_ticket_ids` (not runtime eval).
- **`eval/eval_ticket_search.py`** — V1/V1.1 metrics (`RETAIL_TICKET_HYBRID_SEARCH`).
- **`docker-compose.yml`** — optional Postgres + pgvector on port 5433.

Env (repo `.env`): `GEMINI_API_KEY`, `EMBEDDING_MODEL` (e.g. `gemini-embedding-2`); **`RETAIL_MARKET=AU|BR`** (default **AU** — drives synthetic copy, eval paraphrases, and Postgres `to_tsvector` / `plainto_tsquery` config); `RETAIL_DATABASE_URL`, `RETAIL_TICKET_HYBRID_SEARCH`, `RETAIL_SIDECAR_URL` (when HTTP sidecar is deployed).
