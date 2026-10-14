<h1 id="three-modes-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor: three ticket search modes (V1 / V1.1 / V1.2)</h1>

**Status:** **completed** (P4 product-story eval retune 2026-10-14)  
**Branch:** `feature/bootstrap-rrf-evolve-6-lexical-abc-only`  
**Profile:** `RETAIL_SIM_DATA_PROFILE=rrf_data_llm_gen`  
**Execute:** `qimpltdd docs_manual_gen/ref_plan/completed/REFACTOR_RETAIL_SEARCH_THREE_MODES.md`

<h2 id="three-modes-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Goal](#1-goal) — drop 70/30; rename term boost.
2. [Decisions](#2-decisions) — aligned from user MC.
3. [Phases](#3-phases) — code, eval wipe, ABC run.
4. [Eval ladder design](#4-eval) — strict A &lt; B &lt; C if natural.
5. [Checklist](#5-checklist) — progress.
6. [Acceptance](#6-acceptance)

---

<h2 id="1-goal" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Goal</h2>

Remove **`rrf_weighted` (70/30)** and **`rrf_weighted_boosted`** as if they never existed. Ship **three** modes:

| Arm | Product | Mode | Behavior |
|-----|---------|------|----------|
| A | V1 | `vector_only` | Dense only |
| B | V1.1 | `rrf_normal` | Equal RRF (50/50) |
| C | V1.2 | `rrf_term_boosted` | Equal RRF + λ on parsed **SAM-E###** in query |

**Hard break** — no env aliases for removed modes.

---

<h2 id="2-decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Decisions</h2>

**last_aligned:** 2026-10-14

| ID | Decision |
|----|----------|
| **T1** | Mode string **`rrf_term_boosted`**; λ unchanged (`RETAIL_LEXICAL_CODE_BOOST`, SAM-E parse). |
| **T2** | **`rrf_list_weights`** = (0.5, 0.5) for **both** hybrid modes. |
| **T3** | **Sim data:** keep committed **`service_queries.csv`** (60 rows); wipe **eval JSONL, archives, reports**, rebuild **lexical index** only. |
| **T4** | **Eval:** author via **`abcd_demo_eval_spec.py`** + PG/Tantivy trace; no CSV edits. |
| **T5** | **Ladder:** strict **recall@1(A) &lt; recall@1(B) &lt; recall@1(C)** if natural; else soft non-decreasing + ≥2 B-over-A and ≥2 C-over-B rows. |
| **T7** | **P4 grill (2026-10-14):** extend this plan; **eval-only + trace**; rewrite **3** `hybrid_stress` rows (single open issue + closed/misroute bait); **no SAM-E** on B rows; strict ladder **preferred** (`.cursor/rules/grillnow-pre-implement-multiple-choice.mdc`). |
| **T6** | **Operator:** `05_run_abc_postgres.sh` → `pg_baseline_v1.json`, `pg_ab_v1_1_normal.json`, `pg_ab_v1_2_term_boosted.json`. |

---

<h2 id="3-phases" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Phases</h2>

<h3 id="3-p1" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">P1 — Code + tests (strict-TDD)</h3>

- `search_mode.py`, callers, `.env.example`.
- Remove 70/30 tests; add `rrf_term_boosted` equal-weight + boost tests.
- **Exit:** `./scripts/verify.sh` green.

<h3 id="3-p2" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">P2 — Eval wipe + retune</h3>

- Delete `ticket_retrieval*.jsonl` (except regenerate from spec), `tmp/.../reports/pg_*.json`, old weighted/boosted artifacts.
- Retune 10 eval rows: ~6 vector-easy, ~2 fusion (B lift), ~2 term (C lift vs B).
- `demo_lift` enum: `vector_only` \| `rrf_normal` \| `rrf_term_boosted`.
- **Exit:** validator OK.

<h3 id="3-p3" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">P3 — Operator ABC + docs</h3>

- Rebuild lexical index; run ABC; update ABOUT §13 + operator log.
- **Exit:** [§6](#6-acceptance) ladder recorded.

---

<h2 id="4-eval" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Eval ladder design</h2>

**Teaching story:** semantic paraphrase (A), keyword fusion when dense leg wrong (B), **error code as strong term** when both legs tie on wrong twin (C).

<h3 id="4-p4" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.1 P4 — Product-story eval (grill MC answers)</h3>

**B-lift rows (`hybrid_stress`):** one **open** issue (gold ticket); leading clause is **closed-case or mis-routed** wording that steers the **vector leg** toward a lookalike neighbor — not two equal open complaints. Author with **`RETAIL_EVAL_TRACE_LEGS=1`**: neighbor **vector #1**, gold **lexical #1**, fused gold **#1** under `rrf_normal`. **No SAM-E** in B-row queries (codes reserved for **C** rows).

**C-lift rows (`code_in_query`):** unchanged intent — symptom text may favor wrong twin; **SAM-E###** in query disambiguates under `rrf_term_boosted`.

**Exit:** `./scripts/verify.sh`; `05_run_abc_postgres.sh`; record recall@1; update ABOUT §13.4 narrative + operator log.

---

<h2 id="5-checklist" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Checklist</h2>

- [X] **P1** — Three modes in code + tests
- [X] **P2** — Eval wipe + spec retune + apply
- [X] **P3** — ABC run — recall@1 **0.50 → 0.80 → 1.00** (strict)
- [X] **P4** — Product-story hybrid_stress retune + trace + ABC re-run — recall@1 **0.50 → 0.80 → 1.00** (strict)

---

<h2 id="6-acceptance" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Acceptance</h2>

- No references to `rrf_weighted` / `rrf_weighted_boosted` in product code or tests.
- ABC reports under `tmp/simulated_data/reports/`.
- **Ladder:** strict **A &lt; B &lt; C** on recall@1 **or** documented soft fallback per **T5**.
