<h1 id="lex-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor: switchable lexical search (Tantivy default)</h1>

**Status:** P1–P8 complete (`rrf_data_llm_gen` matrix: 16 JSON reports under `tmp/simulated_data/reports/lexical_matrix/`)  
**Branch:** `feature/bootstrap-rrf-evolve-4-lexical-searches`  
**Parent:** [`REFACTOR_RETAIL_LLM_CORPUS_V2_NATURAL.md`](./REFACTOR_RETAIL_LLM_CORPUS_V2_NATURAL.md) phase 5 (closed)  
**Execute with:** `qimpltdd docs_manual_gen/ref_plan/completed/REFACTOR_RETAIL_LEXICAL_BACKENDS.md`  
**Folder note:** retail plans live under **`docs_manual_gen/ref_plan/`** (`new/` · `wip/` · `completed/`).

<h2 id="lex-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Goal](#1-goal) — four keyword engines behind one switch.
2. [Decisions](#2-decisions) — locked choices from alignment.
3. [Practicality](#3-practicality) — what a config value can and cannot do.
4. [Phases](#4-phases) — Python 3.12, then each backend.
5. [Execution checklist](#5-checklist) — human-visible progress.
6. [Quality bar](#6-quality) — tests, comments, docs, TDD mode per phase.
7. [Deferred](#7-deferred) — out-of-scope follow-ups.
8. [Phase 8 — Lexical × A/B/C/D matrix](#4-p8) — four backends, llm_gen corpus (mandatory).
9. [References](#9-references) — code and docs the implementer must open.

---

<h2 id="1-goal" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Goal</h2>

Postgres stays the system of record (the database that holds the ticket rows and the vector embeddings). The keyword leg of hybrid search (the list of ticket ids ranked by word overlap, later fused with the vector list) becomes a switch:

`RETAIL_LEXICAL_BACKEND` is one of `bm25x`, `tantivy`, `parade_db`, `open_search`. **Default: `tantivy`.**

Each backend is its own module under `scripts/retail/retail_brain/lexical_search/`, with one `README.md` in that directory. `lexical_ids()` in `scripts/retail/retail_brain/pg_search.py` calls the selected module and **stops using** Postgres full-text search (`websearch_to_tsquery` / `ts_rank_cd`).

The vector leg (`vector_ids`) and the Python code-boost after fusion stay as they are.

This is both a production seam (ops can change the keyword engine without rewriting fusion) and a teaching layout (four real clients, one interface).

---

<h2 id="2-decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Decisions</h2>

**last_aligned:** 2026-10-12

| ID | Decision |
|----|----------|
| **D1** | Allowed values: `bm25x`, `tantivy`, `parade_db`, `open_search`. Default **`tantivy`** when the env var is unset. Unknown values **raise**. |
| **D2** | Postgres full-text search is **removed** from `lexical_ids()`. No `pg_fts` value and no silent fallback. |
| **D3** | `bm25x` means the PyPI package **bm25x 0.3.1** (wheels exist **only** for CPython 3.12). Do not reimplement BM25 in-repo. |
| **D4** | Interpreter for **product scripts** is **Python 3.12** (`python3.12` on `PATH`). Do **not** replace Apple’s `/usr/bin/python3` (3.9.6). Existing pytest must pass on 3.12 **before** lexical modules land. |
| **D5** | Script scope for D4: `scripts/**` (shell and `#!/usr/bin/env python3` shebangs, including brain/Hermes) and `cursor_gen/retail_v11_prep/**`. Do **not** edit kit copies under `.cursor/skills/fabrication/` or `bootstrap_webapp/`. |
| **D6** | ParadeDB and OpenSearch are real client modules with **fake** unit tests. Live Docker is documented in the package README. `./scripts/verify-local.sh` does **not** start those services. A live test **skips** unless `RETAIL_PARADEDB_URL` or `RETAIL_OPENSEARCH_URL` is set. |
| **D7** | Rebuild **only the selected** backend after corpus reload. Search reads that index. If the selected index or service is missing, **fail with a clear error** (do not return an empty list and do not fall back to full-text search). |
| **D8** | Retail Postgres image stays `pgvector/pgvector:pg16` on port **5433**. ParadeDB is not swapped into that container. |
| **D9** | Qdrant hybrid (option 6 in [`ABOUT_SEARCH_RRF.md`](../../artifacts/ABOUT_SEARCH_RRF.md) section 11.4) is out of scope. |
| **D10** | **Plan complete** requires **four** lexical backends × **A/B/C/D** (16 eval JSON files) on **`rrf_data_llm_gen`**. One Postgres load + embed; then **`rebuild_lexical_index.py`** per backend (same vectors). Reports under `tmp/simulated_data/reports/lexical_matrix/<backend>/`. ParadeDB and OpenSearch sidecars run **one at a time** (low RAM). |

---

<h2 id="3-practicality" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Practicality</h2>

One Python interface plus one env var is practical. All four engines being “up” for every `verify-local` run is not.

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Backend</th><th>What “implemented” means here</th><th>Constraint</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><code>tantivy</code></td><td style="background:#e8f5e9">In-process index on disk. Default. Unit-tested with a temp directory.</td><td style="background:#e8f5e9">PyPI <code>tantivy</code> 0.26.x has a cp312 wheel. Needs Python ≥ 3.10.</td></tr>
<tr><td style="background:#e3f2fd"><code>bm25x</code></td><td style="background:#e8f5e9">Thin adapter over <code>import bm25x</code>. Same search contract as Tantivy.</td><td style="background:#fff3e0">Wheels are <strong>cp312 only</strong>, no source tarball, empty PyPI description. The section 11.4 snippet is a sketch — confirm the real symbols at import time and adapt the wrapper. Do not treat that snippet as a stable API.</td></tr>
<tr><td style="background:#e3f2fd"><code>parade_db</code></td><td style="background:#fff3e0">SQL client. Unit test uses a fake cursor. README shows a separate ParadeDB container (doc spike used port 5434).</td><td style="background:#ffebee">Cannot flip the current retail database to ParadeDB with an env var. The extension is not in <code>pgvector/pgvector:pg16</code>.</td></tr>
<tr><td style="background:#e3f2fd"><code>open_search</code></td><td style="background:#fff3e0">HTTP client. Unit test uses a fake transport. README shows single-node Docker on port 9200.</td><td style="background:#ffebee">Separate Java process. Not part of default verify.</td></tr>
</tbody>
</table>

**Packages this repo already imports, on Python 3.12:** `psycopg2-binary`, `pytest`, `PyYAML`, `httpx`, and `playwright` all publish 3.12-compatible distributions. Installing 3.12 does not remove the 3.9 or 3.10 environments. A fresh 3.12 install has an empty package set until `pip` is run there.

**Shared contract** (every backend):

```python
def rebuild(self, rows: list[tuple[str, str, str | None]]) -> None:
    """rows: (ticket_id, customer_query_text, model) for resolved tickets only."""

def search_ids(self, query: str, *, k: int, model_filter: str | None = None) -> list[str]:
    """Ordered ticket ids. Uses search_text_for_fts / fts_query_text. No tsquery."""
```

Index files go under `tmp/retail_lexical/` (add that path to `.gitignore`). Env override: `RETAIL_LEXICAL_INDEX_PATH`.

---

<h2 id="4-phases" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phases</h2>

<h3 id="4-p1" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.1 Phase 1 — Point product scripts at Python 3.12</h3>

**Why first:** `bm25x` cannot import on 3.9 or 3.10. Lexical work starts only after the current tests are green on 3.12.

**Mechanism**

- Install CPython 3.12 so `python3.12` resolves on `PATH` (python.org installer or Homebrew). Leave `/usr/bin/python3` as Apple’s 3.9.6.
- Add `scripts/py` that execs `python3.12` and fails with a one-line install hint if that binary is missing.
- Shell under D5 scope calls `"$ROOT/scripts/py"` instead of bare `python3`. Includes `scripts/verify.sh`, `scripts/verify-local.sh`, `scripts/brain/**`, and `cursor_gen/retail_v11_prep/**`.
- Shebangs in `scripts/**/*.py` become `#!/usr/bin/env python3.12`.
- On 3.12, install at least `pytest`, `psycopg2-binary`, and `PyYAML` (brain config reads YAML). Add a wheel only if an existing test import fails. Do not require Playwright browsers for this gate.

**Exit:** `python3.12 -m pytest -q tests/` green, and `./scripts/verify-local.sh` green, **before** any file under `lexical_search/` exists.

<h3 id="4-p2" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.2 Phase 2 — Package, switch, and stop using full-text search</h3>

- Create `scripts/retail/retail_brain/lexical_search/` with `__init__.py` (factory), `base.py` (protocol), and `README.md` (layout, env vars, which backends need Docker).
- `lexical_backend_from_env()` reads `RETAIL_LEXICAL_BACKEND`, default `tantivy`.
- `lexical_ids()` in `pg_search.py` keeps its current signature (`cur`, `query`, `model_filter`, `limit`) so callers do not change, and its body calls `search_ids`. It must not execute `websearch_to_tsquery`.
- `.env.example`: `RETAIL_LEXICAL_BACKEND=tantivy` and a commented `RETAIL_LEXICAL_INDEX_PATH`.
- File header on each new module: what the file is for and that Postgres remains the ticket store.

**Exit:** factory tests green; a test proves `lexical_ids` does not send a tsquery.

<h3 id="4-p3" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.3 Phase 3 — Tantivy (default)</h3>

- `tantivy_index.py`: schema fields `body`, `ticket_id` (raw), `model` (raw). `rebuild` replaces the directory. `search_ids` applies `model_filter` and returns ids in rank order.
- `pip install` `tantivy` for `python3.12` (pin the version that has a cp312 wheel; 0.26.2 was current when this plan was written).
- `scripts/retail/reload_postgres_corpus.py`: after a successful load, rebuild **only** when the active backend is `tantivy` (later phases add their own branch). Search must not rebuild.
- README section: default path, how reload fills the index.

**Exit:** temp-dir Tantivy test green (including a model filter that drops the other model). `verify-local` still green.

<h3 id="4-p4" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.4 Phase 4 — bm25x adapter</h3>

- `bm25x_index.py` wraps the installed extension. Map integer doc ids back to `ticket_id`. Persist the id map next to the index directory so a new process can search without a rebuild.
- Discover the real API with `help(bm25x)` / `dir` on 3.12. If it differs from the section 11.4 sketch (`BM25(index=..., method="lucene")`, `add`, `search(..., subset=)`), follow the library and record the difference in the README. Do not vendor a copy of BM25.
- Same temp-dir contract test as Tantivy: two tickets, one query, model filter.

**Exit:** test green on Python 3.12. If `import bm25x` fails, the phase is blocked (missing 3.12 wheel), not skipped.

<h3 id="4-p5" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.5 Phase 5 — ParadeDB client (no live service in verify)</h3>

- `parade_db.py`: build the BM25 SQL (ParadeDB `@@@` / score — confirm against the image tag named in the README) and return `ticket_id`s from an injected cursor.
- Unit test: fake cursor returns rows; assert the SQL mentions the query text and the model filter; assert id order.
- Optional test marked skip unless `RETAIL_PARADEDB_URL` is set. Do not add ParadeDB to `scripts/retail/docker-compose.yml` in this plan (D8).
- README: separate `paradedb/paradedb` container, port 5434, copy of ticket text from Postgres, not a replacement of the system of record.

**Exit:** fake-cursor test green with Docker stopped.

<h3 id="4-p6" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.6 Phase 6 — OpenSearch client (no live service in verify)</h3>

- `open_search.py`: index mapping (`search_text` text, `model` keyword, `ticket_id` keyword), bulk rebuild, search with a model filter. HTTP via an injected transport (do not require `opensearch-py` if `urllib` is enough; if a client library is used, pin one with `Requires-Python` covering 3.12).
- Unit test: fake transport records the bulk body and the search JSON; returned hits become ticket ids.
- Optional skip-unless `RETAIL_OPENSEARCH_URL`.
- README: single-node Docker on 9200, security plugin off for local dev, Python keeps fusion.

**Exit:** fake-transport test green with nothing listening on 9200.

<h3 id="4-p7" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.7 Phase 7 — Docs match the switch</h3>

- Package `README.md` is the operator map: directory layout, the four values, default, rebuild-on-reload, fail-loud, which two need Docker.
- [`ABOUT_SEARCH_RRF.md`](../../artifacts/ABOUT_SEARCH_RRF.md) section 11.4: default lexical leg is Tantivy; Postgres full-text search is no longer what `lexical_ids()` runs; bm25x stays an alternate value, not the default.
- `scripts/retail/README.md` and `.env.example` name `RETAIL_LEXICAL_BACKEND`.

**Exit:** docs updated; `./scripts/verify-local.sh` still green. No new search behavior in this phase.

<h3 id="4-p8" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.8 Phase 8 — Lexical backend × A/B/C/D matrix (mandatory)</h3>

**Why:** P1–P7 prove **unit** contracts. Production comparison needs the same **llm_gen** gold run four times with `RETAIL_LEXICAL_BACKEND` set to each engine (order: **tantivy → bm25x → parade_db → open_search**).

**Mechanism**

1. **Once:** `03_pg_up_and_load.sh` with `RETAIL_SIM_DATA_PROFILE=rrf_data_llm_gen` (needs `GEMINI_API_KEY` + retail_pg on 5433). Or set `RETAIL_LEXICAL_MATRIX_SKIP_PG_LOAD=1` if PG is already loaded.
2. **Per backend:** set `RETAIL_LEXICAL_BACKEND`; start sidecar if needed; `rebuild_lexical_index.py`; run four search modes into `tmp/simulated_data/reports/lexical_matrix/<backend>/`.
3. **Docker (RAM):** `cursor_gen/retail_v11_prep/lexical_docker/stop_sidecars.sh` before embedded backends; `parade_up.sh` / `opensearch_up.sh` start **one** sidecar at a time (not with the other sidecar up).
4. **Orchestrator:** `bash cursor_gen/retail_v11_prep/06_run_abcd_lexical_matrix.sh`  
   Optional: `RETAIL_LEXICAL_MATRIX_SKIP_PG_LOAD=1` (reuse PG); `RETAIL_LEXICAL_MATRIX_ONLY=tantivy,bm25x` (partial backends).
5. **Summary:** `tmp/simulated_data/reports/lexical_matrix/lexical_matrix_summary.md`; append highlights to `scripts/retail/eval/reports/phase6_operator_log.md` and [`ABOUT_SEARCH_RRF.md`](../../artifacts/ABOUT_SEARCH_RRF.md) §13 as needed.

**Exit:** 16 JSON reports (4 backends × 4 modes); summary file lists report dirs; `./scripts/verify-local.sh` still green (matrix is **not** in default verify).

---

<h2 id="5-checklist" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Execution checklist</h2>

- [X] **P1** — `python3.12` on PATH; `scripts/py`; shebangs and shell in D5 scope; pytest + `psycopg2-binary` + `PyYAML` installed for 3.12; `python3.12 -m pytest -q tests/` and `./scripts/verify-local.sh` green
- [X] **P2** — `lexical_search/` factory, protocol, README skeleton; `lexical_ids()` delegates; no tsquery; `.env.example` default `tantivy`
- [X] **P3** — Tantivy rebuild + search; reload builds the Tantivy index when that backend is selected; temp-dir test green
- [X] **P4** — bm25x adapter against the real 3.12 wheel; id map persisted; temp-dir test green
- [X] **P5** — ParadeDB SQL client + fake cursor test; README Docker note; verify does not start ParadeDB
- [X] **P6** — OpenSearch client + fake transport test; README Docker note; verify does not start OpenSearch
- [X] **P7** — package README finished; section 11.4 and retail README match the switch
- [X] **P8a** — `06_run_abcd_lexical_matrix.sh`, `rebuild_lexical_index.py`, `lexical_docker/*`, Parade schema SQL; `tests/test_retail_lexical_matrix_prep.py` green
- [X] **P8b** — Operator matrix run: 16 JSON under `tmp/simulated_data/reports/lexical_matrix/<backend>/` + `lexical_matrix_summary.md`

---

<h2 id="6-quality" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Quality bar</h2>

| Area | Expectation |
|------|-------------|
| **Tests** | New tests under `tests/`. Each backend phase has a contract test that does not need the other engines. Default verify stays on the existing suite plus those tests. |
| **Comments** | File header on every new module (purpose, and that Postgres is still the ticket store). Comment the bm25x symbol mapping if it diverges from the section 11.4 sketch. |
| **Docs** | Package README is required, not optional. Section 11.4 and `.env.example` update in P7. |
| **DRY** | One factory, one protocol. Do not copy search-text normalization into each backend; call `search_text_for_fts` and `fts_query_text`. |
| **Secrets** | No credentials. ParadeDB and OpenSearch local docs use the same throwaway password style as the retail compose file, or none. |

<h3 id="6-1-tdd" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">6.1 TDD bar (per phase)</h3>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Phase</th><th>TDD mode</th><th>Test-first artifact</th><th>Red case</th><th>Green gate</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">1 Python 3.12</td><td style="background:#e8f5e9"><strong>strict-TDD</strong></td><td style="background:#e8f5e9"><code>tests/test_repo_python312.py</code> — <code>test_interpreter_is_312</code>, <code>test_product_scripts_do_not_call_bare_python3</code></td><td style="background:#ffebee">Suite still runs on 3.9, or a D5 shell script still calls bare <code>python3</code></td><td style="background:#e8f5e9"><code>python3.12 -m pytest -q tests/test_repo_python312.py tests/</code> and <code>./scripts/verify-local.sh</code></td></tr>
<tr><td style="background:#e3f2fd">2 Factory</td><td style="background:#e8f5e9"><strong>strict-TDD</strong></td><td style="background:#e8f5e9"><code>tests/test_retail_lexical_factory.py</code> — <code>test_default_is_tantivy</code>, <code>test_unknown_backend_raises</code>, <code>test_lexical_ids_does_not_use_tsquery</code></td><td style="background:#ffebee">Unset env does not select Tantivy, or <code>lexical_ids</code> still builds a tsquery</td><td style="background:#e8f5e9"><code>python3.12 -m pytest -q tests/test_retail_lexical_factory.py</code></td></tr>
<tr><td style="background:#e3f2fd">3 Tantivy</td><td style="background:#e8f5e9"><strong>strict-TDD</strong></td><td style="background:#e8f5e9"><code>tests/test_retail_lexical_tantivy.py</code> — <code>test_search_returns_matching_ticket</code>, <code>test_model_filter_excludes_other_model</code></td><td style="background:#ffebee">Import or search missing; filter returns the other model</td><td style="background:#e8f5e9"><code>python3.12 -m pytest -q tests/test_retail_lexical_tantivy.py</code></td></tr>
<tr><td style="background:#e3f2fd">4 bm25x</td><td style="background:#e8f5e9"><strong>strict-TDD</strong></td><td style="background:#e8f5e9"><code>tests/test_retail_lexical_bm25x.py</code> — same two contracts as Tantivy</td><td style="background:#ffebee"><code>import bm25x</code> fails, or ids/filter mismatch</td><td style="background:#e8f5e9"><code>python3.12 -m pytest -q tests/test_retail_lexical_bm25x.py</code></td></tr>
<tr><td style="background:#e3f2fd">5 ParadeDB</td><td style="background:#e8f5e9"><strong>strict-TDD</strong></td><td style="background:#e8f5e9"><code>tests/test_retail_lexical_parade.py</code> — <code>test_fake_cursor_returns_ids_and_sql</code></td><td style="background:#ffebee">No SQL builder, or model filter omitted</td><td style="background:#e8f5e9">pytest that file with Docker stopped</td></tr>
<tr><td style="background:#e3f2fd">6 OpenSearch</td><td style="background:#e8f5e9"><strong>strict-TDD</strong></td><td style="background:#e8f5e9"><code>tests/test_retail_lexical_opensearch.py</code> — <code>test_fake_transport_returns_ids</code></td><td style="background:#ffebee">Client opens a real socket, or hits are not ticket ids</td><td style="background:#e8f5e9">pytest that file with nothing on port 9200</td></tr>
<tr><td style="background:#e3f2fd">7 Docs</td><td style="background:#fff8e1"><strong>smoke-after-delete</strong></td><td style="background:#fff3e0">No new red test. README and section 11.4 are the artifact.</td><td style="background:#fff3e0">—</td><td style="background:#e8f5e9"><code>./scripts/verify-local.sh</code> still green</td></tr>
<tr><td style="background:#e3f2fd">8 Matrix prep</td><td style="background:#e8f5e9"><strong>strict-TDD</strong></td><td style="background:#e8f5e9"><code>tests/test_retail_lexical_matrix_prep.py</code></td><td style="background:#ffebee">Orchestrator or sidecar scripts missing</td><td style="background:#e8f5e9">pytest that file + <code>verify-local</code></td></tr>
<tr><td style="background:#e3f2fd">8 Matrix run</td><td style="background:#fff3e0"><strong>operator</strong></td><td style="background:#fff3e0">16 JSON reports + summary md</td><td style="background:#ffebee">HG-EMBED / HG-DOCKER / sidecar timeout</td><td style="background:#e8f5e9"><code>06_run_abcd_lexical_matrix.sh</code> exit 0</td></tr>
</tbody>
</table>

---

<h2 id="7-deferred" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Deferred</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Item</th><th>Reason</th><th>Urgency</th><th>Recommended handling</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Optional pytest marked live against ParadeDB / OpenSearch URLs</td><td>Phase 8 matrix is the primary live check</td><td style="background:#e8f5e9">Low</td><td>Keep unit fakes in default verify; add skip-if-no-URL tests only if needed later.</td></tr>
<tr><td style="background:#e3f2fd">Qdrant hybrid</td><td>D9</td><td style="background:#e8f5e9">Not this plan</td><td>Leave section 11.4 option 6 as documentation only.</td></tr>
<tr><td style="background:#e3f2fd">Python 3.15</td><td><code>bm25x</code> has no 3.15 wheel; Tantivy wheels stopped at cp314 when this plan was written</td><td style="background:#e8f5e9">Later</td><td>Stay on 3.12 until those projects publish wheels.</td></tr>
<tr><td style="background:#e3f2fd">Replace Apple <code>/usr/bin/python3</code></td><td>System interpreter. Other tools may depend on 3.9.</td><td style="background:#ffebee">Do not</td><td>Keep calling <code>python3.12</code> or <code>scripts/py</code>.</td></tr>
</tbody>
</table>

---

<h2 id="9-references" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">9. References</h2>

| Path | Why |
|------|-----|
| [`ABOUT_SEARCH_RRF.md`](../../artifacts/ABOUT_SEARCH_RRF.md) section 11.4 | Six-way comparison and the bm25x / Tantivy sketches |
| [`scripts/retail/retail_brain/pg_search.py`](../scripts/retail/retail_brain/pg_search.py) | `lexical_ids()` today (Postgres full-text search) |
| [`scripts/retail/reload_postgres_corpus.py`](../scripts/retail/reload_postgres_corpus.py) | Hook for rebuilding the active index |
| [`scripts/retail/docker-compose.yml`](../scripts/retail/docker-compose.yml) | Retail Postgres stays pgvector on 5433 |
| [`scripts/verify-local.sh`](../scripts/verify-local.sh) | Gate that must stay green without ParadeDB or OpenSearch |
| [`cursor_gen/retail_v11_prep/06_run_abcd_lexical_matrix.sh`](../cursor_gen/retail_v11_prep/06_run_abcd_lexical_matrix.sh) | Phase 8 orchestrator (four backends × A/B/C/D) |
| [`scripts/retail/rebuild_lexical_index.py`](../scripts/retail/rebuild_lexical_index.py) | Rebuild keyword index only (no re-embed) |
| [`.cursor/rules/tdd/qimpltdd-quick-implement-refactor-plan.mdc`](../.cursor/rules/tdd/qimpltdd-quick-implement-refactor-plan.mdc) | How to execute this plan |

**Execute:** `qimpltdd docs_manual_gen/ref_plan/completed/REFACTOR_RETAIL_LEXICAL_BACKENDS.md`
