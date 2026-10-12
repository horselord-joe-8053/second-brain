<h1 id="llm-v2-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor: natural LLM sim corpus (rrf_data_llm_gen) + honest search eval</h1>

**Status:** P1–P4 complete (P5 deferred)  
**Branch:** `feature/bootstrap-rrf-evolve-3-llm-gen`  
**Parent:** [`REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md`](./REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md)  
**Profile:** `RETAIL_SIM_DATA_PROFILE=rrf_data_llm_gen` → `tmp/simulated_data/`  
**Execution:** **`qimpltdd`** after alignment; Phase 1 can start with prompt + regen (no search-code changes required).

<h2 id="llm-v2-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Goal](#1-goal) — natural data while keeping A/B/C/D runnable.
2. [Decisions](#2-decisions) — locked from alignment.
3. [What we stop doing](#3-stop) — artificial corpus/eval shaping.
4. [Phases](#4-phases) — P1 prompt v2 + regen first.
5. [Execution checklist](#5-checklist) — human-visible progress.
6. [Acceptance](#6-acceptance) — exit criteria per phase.

---

<h2 id="1-goal" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Goal</h2>

Run **V1 / V1.1 / V1.2 / V1.3** A/B/C/D on **`rrf_data_llm_gen`** while treating sim data as **production-like**, not as a fixture tuned to make one search mode “win.”

**Historical corpus (`service_queries.csv`):** maximum **lexical and story diversity**, **minimum schema constraints**, **no near-duplicate bodies** planted to confuse vector.

**Incoming sim tickets (`ticket_retrieval.jsonl`):** each eval row is a **new intake** with exactly one **golden** historical `ticket_id` (`expected_ticket_ids` + `source_ticket_id`).

**Parallel code track (later phases):** stop stripping **SAM-E###** from embeddings; limit “fluff” removal to **configurable genuine boilerplate** (`|`‑separated phrases), not diagnostic codes.

**You are not missing anything critical** if you also plan for: (a) **validator** after generation (duplicate prose, gold `status=resolved` for PG search), (b) **re-embed + reload** after corpus or embed-policy changes, (c) **strata** as **labels** derived after authoring—not quotas that force query shapes in the prompt.

---

<h2 id="2-decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Decisions</h2>

**last_aligned:** 2026-10-12

| ID | Decision |
|----|----------|
| **D1** | Corpus size **60 historical + 10 eval** for `rrf_data_llm_gen`. |
| **D2** | **~50%** of historical tickets include **SAM-E###** somewhere in `customer_query_text` (natural placement); the rest have **no** SAM-E token. |
| **D3** | Eval queries: **natural mix** — when gold has SAM-E, **~half** of those eval rows mention the code in the intake, **~half** describe the fault only (production-like). |
| **D4** | **No** prompt rules that require **duplicate symptom bodies** with different codes (“hard negative clones”). |
| **D5** | **No** mandatory `Technician log: diagnostic code …` suffix; tech-line format allowed but not required. |
| **D6** | Phase 1 ships **prompt v2 + regenerated** `tmp/simulated_data/*` + operator steps (not prompt-only). |
| **D7** | **`rrf_data_prag_gen`** unchanged in Phase 1; optional convergence in a later phase. |

---

<h2 id="3-stop" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. What we stop doing</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Artifact</th><th>Undesirable pattern</th><th>v2 approach</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><code>prompt.txt</code> v1</td><td style="background:#ffebee">100% tech-line suffix; “hard negatives” with same story + different SAM-E; fixed stratum quotas in author prompt</td><td style="background:#e8f5e9">Diversity-first; optional post-hoc <code>stratum</code> tagging</td></tr>
<tr><td style="background:#e3f2fd"><code>text_for_embedding()</code></td><td style="background:#ffebee">Strips entire tech line including SAM-E</td><td style="background:#fff3e0">Phase 3: retain SAM-E; fluff via env list</td></tr>
<tr><td style="background:#e3f2fd"><code>seed_narrative</code> (prag_gen)</td><td style="background:#fff3e0">Explicit twin pairs + scheduled <code>error_code</code> rows</td><td style="background:#fff3e0">Out of scope for P1; document as separate profile</td></tr>
<tr><td style="background:#e3f2fd">Eval interpretation</td><td style="background:#ffebee">Expect V1.1/V1.2 lift without BM25/FTS when queries are paraphrase-only</td><td style="background:#e8f5e9">Report lexical_nonempty + plan Qdrant/BM25 separately</td></tr>
</tbody>
</table>

---

<h2 id="4-phases" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phases</h2>

<h3 id="4-p1" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.1 Phase 1 — Data-gen prompt v2 + regenerate LLM profile</h3>

**Deliverables**

- `tmp/simulated_data/prompt_v2.txt` — author instructions (replace v1 as default after review).
- Regenerated `service_queries.csv`, `ticket_manifest.jsonl`, `ticket_retrieval.jsonl` (60 + 10).
- `tmp/simulated_data/README.md` — operator: validate → `03_pg_up_and_load.sh` → `05_run_abcd_postgres.sh`.
- Archive v1 prompt as `prompt_v1_archived.txt` (optional copy for diff).

**Prompt v2 content rules (summary)**

- **Models:** Galaxy A15 / A16 / A25 5G only; AU cities; CSV schema unchanged.
- **Historical (60):** unique `customer_query_text` per row (no copy-paste clones); varied openings and symptom vocabulary; **≥15 distinct issue themes**; **~30 rows (~50%)** contain **SAM-E###** once, naturally (customer mention and/or technician note—no fixed template).
- **Status:** mostly `resolved`; avoid pointing eval gold at non-`resolved` rows (search filters resolved today).
- **Eval (10):** each picks a distinct gold `ticket_id`; paraphrase intakes; **D3** code-in-query mix; include `model_filter`, `expected_ticket_ids`, `source_ticket_id`, `stratum` (author or post-tag: `paraphrase` | `literal_token` | `error_code` | `code_in_query` optional).
- **Forbidden in prompt:** twin/hard-negative cloning; “identical symptoms, different code” instructions; mandatory tech-line suffix; eval queries that copy stored text verbatim.

**Exit:** Human review table eval_id → gold → has SAM-E in query?; files committed on branch; no pytest change required.

<h3 id="4-p2" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.2 Phase 2 — Corpus validator (CI-friendly)</h3>

- Script e.g. `scripts/retail/seed/validate_llm_corpus.py`: duplicate normalized body detection; SAM-E count ~50% ± tolerance; all eval gold ids exist and **resolved**; anti-leakage (eval ≠ stored text); JSONL schema.
- Wire into `./scripts/verify.sh` or document as operator gate for llm profile.

**Exit:** validator passes on regenerated corpus.

<h3 id="4-p3" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.3 Phase 3 — Embed + fluff policy (search code)</h3>

- **`text_for_embedding()`:** keep **SAM-E###** in embedded text; strip only phrases from **`RETAIL_EMBED_STRIP_PHRASES`** (env, `|`-separated, e.g. `Case ref ITM-|Technician log:` wrappers if desired—not the code token).
- **`search_text_for_fts` / BM25 future:** same strip list where appropriate; codes remain.
- Re-run `reload_postgres_corpus.py` for llm profile; update tests in `test_retail_text_normalize.py`.

**Exit:** `./scripts/verify.sh` green; note embed model + date in `tmp/simulated_data/README.md`.

<h3 id="4-p4" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.4 Phase 4 — Operator A/B/C/D on natural llm corpus</h3>

- `RETAIL_SIM_DATA_PROFILE=rrf_data_llm_gen` → load + `05_run_abcd_postgres.sh`.
- Write reports under `tmp/simulated_data/reports/`; append summary to `phase6_operator_log.md` (profile + lexical_nonempty + by-stratum).
- Update [`ABOUT_SEARCH_RRF.md`](./artifacts/ABOUT_SEARCH_RRF.md) §13 with **honest** narrative (no “demo twin” assumption for llm profile).

**Exit:** four JSON reports; stratum table recorded; no gold edits after run.

<h3 id="4-p5" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.5 Phase 5 — Lexical production path (deferred decision)</h3>

- Choose **Postgres ParadeDB BM25**, **Qdrant hybrid**, or **softened FTS query**; out of scope until P1–P4 characterize natural corpus metrics.
- Parent Samsung plan Phase for infra when metrics justify it.

---

<h2 id="5-checklist" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Execution checklist</h2>

- [X] **P1** — Author `prompt_v2.txt`; regenerate 60 + 10; update `tmp/simulated_data/README.md`
- [X] **P2** — `validate_llm_corpus.py` + gate
- [X] **P3** — `RETAIL_EMBED_STRIP_PHRASES` + retain SAM-E in embed; tests green
- [X] **P4** — llm profile A/B/C/D + operator log + ABOUT §13.3
- [ ] **P5** — (optional) BM25/Qdrant/ParadeDB decision doc

---

<h2 id="6-acceptance" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Acceptance</h2>

- **Data:** No pair of historical rows with **identical** normalized `customer_query_text` (ignoring SAM-E token only is **not** exempt—bodies must differ substantively).
- **Eval:** 10 rows, unique gold ids, **D3** code-in-query mix documented in review table.
- **Search:** Each mode measured on **same** frozen JSONL gold; no post-hoc gold edits.
- **Honesty:** Docs state when **V1.3** carries `error_code` stratum vs when **lexical leg is empty** on paraphrase-heavy queries.
