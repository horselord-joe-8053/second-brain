<h1 id="v1x-plan" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor: retail ticket search V1.1 → V1.3 (RRF modes + production lexical)</h1>

**Status:** **wip** — ready for **`qimpltdd`** / **`aciubtdd`**  
**Parent:** [`REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md`](../../../docs_manual_gen/REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md) · **Article:** [`ABOUT_SEARCH_RRF.md`](../../../docs_manual_gen/artifacts/ABOUT_SEARCH_RRF.md)  
**Execute with:** [`implreftdd`](../../../.cursor/rules/tdd/implreftdd-resumimpl-refactor-plan-followthrough.mdc)

<h2 id="v1x-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Decisions (locked)](#1-decisions) — modes, weights, λ, code parse.
2. [Phase A — V1.1 `rrf_normal` lexical](#2-phase-a) — fts_query + tests.
3. [Phase B — search mode switch](#3-phase-b) — env + harness A/B/C/D.
4. [Phase C — V1.2 weighted RRF](#4-phase-c) — 70/30.
5. [Phase D — V1.3 code boost](#5-phase-d) — λ = 10 default.
6. [Phase E — operator + docs](#6-phase-e) — reports, ABOUT §7.
7. [Exit / quality bar](#7-exit) — verify, no gold tampering.

**Execution checklist:**

- [ ] **Phase A** — V1.1 production lexical ([§2](#2-phase-a))
- [ ] **Phase B** — `RETAIL_TICKET_SEARCH_MODE` ([§3](#3-phase-b))
- [ ] **Phase C** — V1.2 weighted fusion ([§4](#4-phase-c))
- [ ] **Phase D** — V1.3 code boost ([§5](#5-phase-d))
- [ ] **Phase E** — operator run + update artifacts ([§6](#6-phase-e))

---

<h2 id="1-decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Decisions (locked)</h2>

| ID | Decision |
|----|----------|
| **V1x-1** | **`RETAIL_TICKET_SEARCH_MODE`:** `vector_only` \| `rrf_normal` \| `rrf_weighted` \| `rrf_weighted_boosted` → product **V1 / V1.1 / V1.2 / V1.3**. |
| **V1x-2** | **V1.1 lexical:** light normalize + `ts_rank_cd` on rich query; **remove** whole-query rewrite to tech-line as default (keep tests for legacy if needed). |
| **V1x-3** | **V1.2 weights:** \(w_v=0.7\), \(w_l=0.3\) on each leg’s `1/(k+rank)` terms; **k=60** unchanged. |
| **V1x-4** | **V1.3:** same 70/30 + **λ=10** (`RETAIL_LEXICAL_CODE_BOOST`) on **parsed `SAM-E###` only**; parse from text, **no required column**. |
| **V1x-5** | **Eval:** OK if **`error_code`** recall drops on V1.1 vs demo-era; V1.3 should recover lift. |
| **V1x-6** | **Legacy:** `RETAIL_TICKET_HYBRID_SEARCH=1` → `rrf_normal`; `0` → `vector_only`. |

---

<h2 id="2-phase-a" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Phase A — V1.1 `rrf_normal` lexical</h2>

**TDD mode:** strict-TDD

- [ ] **`fts_query_text`:** screenshot queries keep symptoms + model + code tokens (map to index shape without collapsing to tech-line only).
- [ ] Add/adjust tests in `tests/test_retail_text_normalize.py`, `tests/test_retail_diag_codes.py`.
- [ ] **Red → green:** paraphrase alignment tests; error_code query still overlaps gold `search_text`.
- [ ] **Exit:** `./scripts/verify.sh` green.

---

<h2 id="3-phase-b" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Phase B — search mode switch</h2>

- [ ] **`retail_brain/search_mode.py`** (or extend `hybrid_search.py`): parse mode enum; deprecate boolean-only API internally.
- [ ] Wire **`pg_search.py`**, **`eval_ticket_search.py`**, **`run_ab_compare.sh`**, **`04_run_ab_postgres.sh`** → four JSON reports.
- [ ] Report `mode` field = search mode string.
- [ ] Pytests: mode routing + legacy env alias.

---

<h2 id="4-phase-c" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phase C — V1.2 weighted RRF</h2>

- [ ] **`reciprocal_rank_fusion`:** parameters `vector_weight`, `lexical_weight` (defaults 0.5 / 0.5).
- [ ] **`rrf_weighted`:** pass **0.7 / 0.3**.
- [ ] Tests: weighted fusion changes order vs equal weights on fixture lists.

---

<h2 id="5-phase-d" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Phase D — V1.3 code boost</h2>

- [ ] **`extract_diag_code(text) -> str | None`** in `text_normalize.py` or `diag_codes.py`.
- [ ] Third RRF term or boosted lexical sub-list: ids matching parsed code in indexed text get **λ × 1/(k+1)** (or documented equivalent).
- [ ] **`rrf_weighted_boosted`:** enable boost; default **λ=10** from env.
- [ ] Tests: query with `SAM-E176` promotes gold over twin when vector prefers twin.

---

<h2 id="6-phase-e" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Phase E — operator + docs</h2>

- [ ] Regen if needed: `02` → `03` → new **`05_run_abcd_postgres.sh`** (or extend `04`).
- [ ] Update `phase6_operator_log.md`, [`ABOUT_SEARCH_RRF.md`](../../../docs_manual_gen/artifacts/ABOUT_SEARCH_RRF.md) §7.2.
- [ ] **`docs/specs/samsung-retail-synthetic-data.md`:** V1.1 lexical policy one paragraph.

---

<h2 id="7-exit" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Exit / quality bar</h2>

- [ ] `./scripts/verify.sh` green after each phase.
- [ ] Do **not** edit `expected_ticket_ids` to match top-k ([D8](../../../docs_manual_gen/REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md#2-decisions)).
- [ ] Four-mode report set committed under `scripts/retail/eval/reports/`.

**Start:** `qimpltdd cursor_gen/refactor_plans/wip/REFACTOR_RETAIL_TICKET_SEARCH_V1X.md`
