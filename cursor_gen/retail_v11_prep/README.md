<h1 id="prep-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Retail V1.1 A/B — local prep (temporary)</h1>

**Purpose:** Get **real Postgres + PDFs** ready before V1 vs V1.1 A/B. Scripts are **operator helpers** (not long-term product entrypoints).

<h2 id="prep-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Current state](#1-state) — what is / is not done.
2. [Prep order](#2-order) — run scripts 00 → 04; teardown 05.
 2.1 [Docker Desktop](#2-1-docker) — what is / is not automated.
 2.2 [External software pattern](#2-2-external) — require_cmd / stop + prompt.
3. [Hermes handoff](#3-hermes) — Nashsu steps the coding agent cannot do.
4. [Defaults](#4-defaults) — corpus size, market, and embeddings.

---

<h2 id="1-state" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Current state</h2>

| Item | Status |
|------|--------|
| Synthetic tickets in **PostgreSQL** | **Yes** — 90 rows on `:5433` after Phase 6 shakedown |
| CI eval | **Yes** — pytest stubs embed; production uses Gemini via `.env` |
| **6 PDF manuals** | Copied to **`brain/retail/raw/sources/samsung-docs/`** |
| LLM Wiki **compile** of PDFs | **No** — Hermes **rescan** still required for manual Q&A |
| V1.1 A/B on **Postgres** | **Done** — see `scripts/retail/eval/reports/phase6_operator_log.md` |

---

<h2 id="2-order" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Prep order</h2>

From repo root:

```bash
bash cursor_gen/retail_v11_prep/00_docker_ensure.sh    # start daemon if Docker.app exists
bash cursor_gen/retail_v11_prep/01_copy_manuals.sh
bash cursor_gen/retail_v11_prep/02_generate_corpus.sh    # phase 1: COUNT=50 (default)
# … implement / load …
COUNT=90 bash cursor_gen/retail_v11_prep/02_generate_corpus.sh   # phase 2: pre-A/B
bash cursor_gen/retail_v11_prep/03_pg_up_and_load.sh   # calls 00; compose up + load
bash cursor_gen/retail_v11_prep/04_run_ab_postgres.sh
# when done:
bash cursor_gen/retail_v11_prep/05_teardown.sh           # compose down
# QUIT_DOCKER_DESKTOP=1 bash cursor_gen/retail_v11_prep/05_teardown.sh
```

<h3 id="2-1-docker" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.1 Docker Desktop — automation limits</h3>

| Action | Scripted? |
|--------|-----------|
| **Install / download Docker Desktop** | **No** — script **stops** if `which docker` fails; prints install hint. |
| **Start daemon** if CLI + `Docker.app` exist | **Yes** — `00_docker_ensure.sh` (`open -a Docker`, wait for `docker info`). |
| **Homebrew cask upgrade** | **Optional, idempotent** — `RETAIL_DOCKER_BREW_UPGRADE=1` runs `brew upgrade --cask docker` once per invocation (needs network; only if cask `docker` is installed). |
| **In-app “Update Docker Desktop” UI** | **No** — fail fast **HG-DOCKER-UPDATE**; human completes update in Docker Desktop, then re-run `00`. |
| **Retail PG up/down** | **Yes** — `03_*` / `05_teardown.sh` (`docker compose` in `scripts/retail/`). |
| **Quit Docker Desktop** | **Optional** — `QUIT_DOCKER_DESKTOP=1` on `05_teardown.sh`. |

```bash
# After you approve a Docker Desktop update in the UI, or for Homebrew-managed Docker:
RETAIL_DOCKER_BREW_UPGRADE=1 bash cursor_gen/retail_v11_prep/00_docker_ensure.sh
```

<h3 id="2-2-external" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.2 External software pattern</h3>

Prep scripts **do not** auto-install system or GUI packages. Shared helper: [`lib/require_external.sh`](./lib/require_external.sh).

1. **`require_cmd <name>`** — if `command -v` fails → **STOP**, print install instructions, **exit 1**.
2. **`require_python_module <name>`** — same for `python3 -import` (e.g. `psycopg2` in `03_pg_up_and_load.sh`).
3. Agent / operator installs manually, then re-runs the script.

Use the same pattern for any future external deps (e.g. `hermes` CLI smoke — prompt only, do not brew-install from CI).

Then run **Hermes** prompt in [`HERMES_PREP_PROMPT.md`](./HERMES_PREP_PROMPT.md) for PDF → wiki.

---

<h2 id="3-hermes" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Hermes handoff</h2>

See **`HERMES_PREP_PROMPT.md`** — copy/paste into Hermes Desktop after step 01.

---

<h2 id="4-defaults" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Defaults</h2>

- **Sim data profile:** **`RETAIL_SIM_DATA_PROFILE=rrf_data_llm_gen`** (default) — `tmp/simulated_data/*.csv` + eval JSONL; reports under `tmp/simulated_data/reports/`. **`rrf_data_prag_gen`** — `scripts/retail/seed/generated/` + reports under `scripts/retail/eval/reports/prag_gen/`. Steps **03** / **04** / **05** print a banner with the active profile. **03** and **`reload_postgres_corpus.py`** **TRUNCATE** `service_queries` before load (idempotent; no mixed corpora in PG).
- **Market:** **`RETAIL_MARKET=AU`** (default) — en-AU synthetic copy + Postgres `english` FTS; **`BR`** for pt-BR + `portuguese`. Set in repo `.env` before `02` / `03` / `04`.
- **Phased corpus (prag_gen only):** `COUNT=50` while implementing; **`COUNT=90`** (same `SEED=42`) right before A/B—run **`02_generate_corpus.sh`** when profile is **`rrf_data_prag_gen`**. LLM profile skips **02** if files already exist under **`tmp/simulated_data/`**.
- **Embeddings:** **Gemini only** — `GEMINI_API_KEY` + `EMBEDDING_MODEL` in repo `.env`; `utils/retail_fru/embeddings.py`. Fails fast if missing. Plan [Phase 6](../../docs_manual_gen/ref_plan/wip/REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md#15-phase-6), **D10–D11**.
