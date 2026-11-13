<h1 id="cursor-prep-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Cursor prep runbook — FRU US retail (Postgres + ABC)</h1>

**Audience:** Cursor / shell operator. **Not** Hermes wiki ingest — see [`HERMES_WIKI_OPERATOR.md`](./HERMES_WIKI_OPERATOR.md).

<h2 id="cursor-prep-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Env](#1-env) — FRU defaults.
2. [Scripts 00–05](#2-scripts) — Docker, load, ABC.
3. [Exit](#3-exit) — what Cursor does not run.

---

<h2 id="1-env" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Env</h2>

```bash
export RETAIL_SIM_DATA_PROFILE=fru_us_1k
export RETAIL_MARKET=US
export RETAIL_FAULT_CODE_PREFIX=FRU-E
export RETAIL_LEXICAL_BACKEND=tantivy
# Repo .env: GEMINI_API_KEY, EMBEDDING_MODEL, RETAIL_DATABASE_URL
```

<h2 id="2-scripts" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Scripts</h2>

| Step | Script | Purpose |
|------|--------|---------|
| 0 | `00_docker_ensure.sh` | Docker daemon |
| 1 | `01_copy_manuals.sh` | Copy staged fridge PDFs → `brain/retail/raw/sources/fridge-docs/` |
| 3 | `03_pg_up_and_load.sh` | Schema migrations, TRUNCATE, load CSV, Gemini embed, Tantivy rebuild |
| 5 | `05_run_abc_postgres.sh` | A/B/C eval + `check_abc_ladder.py` |

Corpus path: `scripts/retail/sim_data/profiles/fru_us_1000_100/`.

<h2 id="3-exit" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Exit</h2>

- Cursor **does not** run Hermes `llm_wiki_*` for product manual Q&A (D9).
- After PDF copy, hand off to [`HERMES_WIKI_OPERATOR.md`](./HERMES_WIKI_OPERATOR.md) for wiki compile smoke.
