<h1 id="rrf-strip-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor: retail hybrid RRF with FTS normalize + realistic deterministic seed</h1>

**Status:** **completed** — Phase 6–7 diagnostic-code eval + operator A/B  
**Parent plan:** [`REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md`](./REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md)  
**Execution:** **`qimpltdd`** / [`implreftdd`](../.cursor/rules/tdd/implreftdd-resumimpl-refactor-plan-followthrough.mdc)

## Document outline

1. [Problem](#1-problem)
2. [Why extra updates (twin A/B)](#2-why-extra)
3. [Phases 1–5 (done)](#3-phases-done)
4. [Phase 6 — diagnostic codes + embed/FTS split](#4-phase-6)
5. [Phase 7 — operator A/B by stratum](#5-phase-7)
6. [Quality bar](#6-quality-bar)
7. [Deferred](#7-deferred)

---

<h2 id="1-problem" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Problem</h2>

Hybrid **RRF (reciprocal rank fusion)** was wired and lexical could be non-empty, but **A/B on the narrative seed** mostly flipped **near-duplicate twins** (same issue/city/model + shared eval symptom line; only `detail_when` differed in the cabinet; eval omitted that sentence). That made **V1 vs V1.1** comparisons **meaningless** for judging whether a lexical leg earns its keep vs **pure vector RAG (retrieval-augmented generation)**.

---

<h2 id="2-why-extra" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Why extra updates (twin A/B)</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Observation</th><th>Consequence</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">9 strict top-1 flips, net +1 recall</td><td style="background:#fff3e0">RRF arbitrating twins, not demonstrating BM25-class value</td></tr>
<tr><td style="background:#e3f2fd">Duplicate full bodies (e.g. 000005 vs 000035)</td><td style="background:#ffebee">Strict gold breaks even when prose matches</td></tr>
<tr><td style="background:#e3f2fd">Model already in <code>model_filter</code></td><td style="background:#fff3e0">Lexical must add **sparse exact tokens** (e.g. diag codes), not store IDs</td></tr>
</tbody>
</table>

**Design target (ChatGPT / repair-desk realism):** customer query **paraphrases** the fault; **diagnostic code** appears in intake or only in **technician log** on historical tickets — **FTS** matches code; **vector** on customer-only embed may miss.

---

<h2 id="3-phases-done" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Phases 1–5 (done)</h2>

- [X] **Phase 1** — `text_normalize.py`, FTS query alignment, tests  
- [X] **Phase 2** — `search_text`, `websearch_to_tsquery`, embed path, schema `002`  
- [X] **Phase 3** — superseded store-in-prose approach  
- [X] **Phase 4** — hybrid tests, war story #4, operator smoke  
- [X] **Phase 5** — `seed_narrative.py`, 10-issue pool, no operational IDs in prose/eval  

---

<h2 id="4-phase-6" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phase 6 — diagnostic codes + embed/FTS split</h2>

**TDD mode:** strict-TDD

- [X] Deterministic `SAM-E###` per `(seed, index)` in `seed_narrative.py`
- [X] Stored: `Technician log: diagnostic code {code}.` appended to `customer_query_text`
- [X] `text_for_embedding()` strips tech line; **Gemini document embed** uses customer-facing text only
- [X] `search_text_for_fts()` keeps tech line (code indexed for lexical leg)
- [X] Eval: every 3rd row → stratum **`error_code`**, code-forward query (`format_eval_query_with_code()`)
- [X] `fts_query_text()` maps intake “code SAM-E…” to tech-line shape for `@@` match
- [X] Detail slots indexed by `(seed, index)` to avoid duplicate bodies at 90 rows
- [X] Tests: `tests/test_retail_diag_codes.py`
- [X] Spec: `error_code` stratum in `docs/specs/samsung-retail-synthetic-data.md`
- [X] **Exit:** `./scripts/verify.sh` green (48 pytest)

---

<h2 id="5-phase-7" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Phase 7 — operator A/B by stratum</h2>

- [X] Regenerate corpus (`02`), `03_pg_up_and_load.sh`, `04_run_ab_postgres.sh`
- [X] Record results in `phase6_operator_log.md` (overall + by stratum)
- [X] **Outcome:** overall vector **0.672** vs hybrid **0.896**; lexical **67/67**; **`error_code`** stratum drives hybrid lift (vector misses code-only match on customer embed)

---

<h2 id="6-quality-bar" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Quality bar</h2>

- No LLM in seed; frozen CSV/JSONL in repo for CI  
- D6 promotion still uses strict `recall_at_1`; stratum table is evidence, not auto-promote  

---

<h2 id="7-deferred" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Deferred</h2>

| Item | Notes |
|------|-------|
| Weighted RRF when query regex sees a code | After Phase 7 baseline |
| Cross-encoder rerank | V3 eval |
| Related-model widen (wiki) | V2+ |
