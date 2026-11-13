<h1 id="lex-readme-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Keyword search backends</h1>

Postgres holds the ticket rows and the vector embeddings. This folder is only the keyword leg: it returns ordered ticket ids. Python still fuses that list with the vector list.

<h2 id="lex-readme-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Switch](#lex-readme-switch) — one environment variable.
2. [Layout](#lex-readme-layout) — which file does what.
3. [Rebuild](#lex-readme-rebuild) — when the index is filled.
4. [External services](#lex-readme-external) — ParadeDB and OpenSearch.
5. [A/B/C matrix](#lex-readme-matrix) — three search modes × four backends on llm_gen.

---

<h2 id="lex-readme-switch" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Switch</h2>

`RETAIL_LEXICAL_BACKEND` is one of:

| Value | Engine | Needs a separate process? |
|-------|--------|---------------------------|
| `tantivy` | Embedded Tantivy index (default when unset) | No |
| `bm25x` | PyPI package `bm25x` (Python 3.12 only) | No |
| `parade_db` | SQL against `RETAIL_PARADEDB_URL` | Yes |
| `open_search` | HTTP against `RETAIL_OPENSEARCH_URL` | Yes |

Any other value raises. There is no fallback to Postgres full-text search. If the selected index or service is missing, search raises instead of returning an empty list.

Product scripts run on Python 3.12 via `scripts/py`. Apple's `python3` is left alone.

---

<h2 id="lex-readme-layout" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Layout</h2>

| File | Role |
|------|------|
| `__init__.py` | Reads the env var, opens one backend, `rebuild_active(rows)` |
| `paths.py` | Directory for embedded indexes (`RETAIL_LEXICAL_INDEX_PATH` or `tmp/retail_lexical/`) |
| `tantivy_index.py` | Default. Disk index, fields `body`, `ticket_id`, `model` |
| `bm25x_index.py` | Wrapper. `BM25(index=..., method="lucene")`, plus `tickets.json` so ids survive a new process |
| `parade_db.py` | Table `lexical_tickets` on the ParadeDB server. Operator `@@@` |
| `open_search.py` | Index `retail_tickets`. Tests pass a fake HTTP function |

`pg_search.lexical_ids()` keeps its old arguments and calls `search_ids`. It does not send a tsquery.

Text going into every backend uses `search_text_for_fts` on the stored ticket and `fts_query_text` on the live question.

---

<h2 id="lex-readme-rebuild" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Rebuild</h2>

`scripts/retail/reload_postgres_corpus.py` loads Postgres, embeds, then rebuilds **only the selected** backend from resolved tickets. Search does not rebuild.

Embedded index files are gitignored under `tmp/retail_lexical/`.

---

<h2 id="lex-readme-external" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. External services</h2>

Default `./scripts/verify-local.sh` does not start these. Unit tests use a fake cursor and a fake HTTP transport.

**ParadeDB** (separate from retail Postgres on port 5433):

```bash
docker run --rm -e POSTGRES_PASSWORD=retail -p 5434:5432 paradedb/paradedb:latest
```

Set `RETAIL_PARADEDB_URL=postgresql://postgres:retail@127.0.0.1:5434/postgres`. Schema: `scripts/retail/schema/003_lexical_parade_tickets.sql` (applied by `parade_up.sh`). Requires `vector` + `pg_search` extensions in the Parade image.

**OpenSearch:**

```bash
docker run -d --name retail-os -p 9200:9200 \
  -e discovery.type=single-node \
  -e DISABLE_SECURITY_PLUGIN=true \
  opensearchproject/opensearch:2
```

Set `RETAIL_OPENSEARCH_URL=http://127.0.0.1:9200`. On Linux the host may need a higher `vm.max_map_count`.

---

<h2 id="lex-readme-matrix" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. A/B/C matrix (× four lexical backends)</h2>

Compare all four backends on **`rrf_data_llm_gen`** (one Postgres embed load, rebuild per backend):

```bash
export RETAIL_SIM_DATA_PROFILE=rrf_data_llm_gen
bash cursor_gen/retail_v11_prep/06_run_abcd_lexical_matrix.sh   # three search modes × four backends
bash cursor_gen/retail_v11_prep/05_run_abc_postgres.sh          # llm_gen A/B/C on Tantivy
```

Reports: `tmp/simulated_data/reports/lexical_matrix/<backend>/`. Sidecar scripts under `cursor_gen/retail_v11_prep/lexical_docker/` stop ParadeDB before OpenSearch (and vice versa) so only one RAM-heavy lexical container runs at a time.
