<h1 id="hybrid-eval-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor: A/B/C/D demo eval for `rrf_data_llm_gen` (Tantivy hybrid ladder)</h1>

**Status:** **completed** (2026-10-14) — demo eval + operator A/B/C/D on Tantivy  
**Profile:** `RETAIL_SIM_DATA_PROFILE=rrf_data_llm_gen` → `tmp/simulated_data/`  
**Parent:** [`REFACTOR_RETAIL_LLM_CORPUS_V2_NATURAL.md`](../completed/REFACTOR_RETAIL_LLM_CORPUS_V2_NATURAL.md)  
**Depends on:** [`REFACTOR_RETAIL_LEXICAL_BACKENDS.md`](../completed/REFACTOR_RETAIL_LEXICAL_BACKENDS.md) (`RETAIL_LEXICAL_BACKEND=tantivy` default)  
**Execute with:** `qimpltdd docs_manual_gen/ref_plan/completed/REFACTOR_RETAIL_LLM_GEN_HYBRID_EVAL_STRESS.md` (done)  
**Article:** [`ABOUT_SEARCH_RRF.md`](../../artifacts/ABOUT_SEARCH_RRF.md) §13

<h2 id="hybrid-eval-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Problem](#1-problem) — vector-only 1.0/10 does not demo hybrid.
2. [Goal](#2-goal) — teaching ladder A→B→C→D = V1→V1.3.
3. [Decisions](#3-decisions) — aligned 2026-10-14.
4. [A/B/C/D mapping](#4-abcd) — modes vs product labels.
5. [Eval design table](#5-design) — ten rows, `demo_lift` intent.
6. [Phases](#6-phases) — eval JSONL, validator, operator run.
7. [Execution checklist](#7-checklist) — progress.
8. [Acceptance](#8-acceptance) — soft monotonic recall + honesty rules.

---

<h2 id="1-problem" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Problem</h2>

On the current ten eval intakes, **vector-only** often scores **recall@1 = 1.0** while **hybrid** arms add little ([§13.3](../../artifacts/ABOUT_SEARCH_RRF.md#13-3-llm-v2)). That under-teaches the **A/B/C/D** ladder operators run via `05_run_abcd_postgres.sh`.

---

<h2 id="2-goal" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Goal</h2>

Replace **only** `ticket_retrieval.jsonl` (ten eval rows). Keep **60** historical `service_queries.csv` rows unchanged. Author intakes so that, with **Tantivy BM25** + frozen gold:

- **Aggregate recall@1** rises **soft-monotonically** A ≤ B ≤ C ≤ D (1–2 row regressions OK if documented by `demo_lift` stratum).
- **Primary audience:** demo / teaching narrative (not D6 promotion gate).
- **No** post-hoc edits to `expected_ticket_ids` after seeing scores.

---

<h2 id="3-decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Decisions</h2>

**last_aligned:** 2026-10-14

| ID | Decision |
|----|----------|
| **H1** | **Eval-only:** replace `ticket_retrieval.jsonl`; **do not** regen 60 historical rows. Archive prior eval as `ticket_retrieval_v2_archived.jsonl`. |
| **H2** | **Ten eval rows** (unchanged count). |
| **H3** | **Demo goal** — show each V1.x layer adding value on **some** rows; not a promotion checklist. |
| **H4** | **Soft monotonicity** — prefer recall@1(D) ≥ recall@1(C) ≥ recall@1(B) ≥ recall@1(A); allow 1–2 documented regressions between adjacent arms. |
| **H5** | **`demo_lift`** optional field on each eval row: first mode expected to hit gold (`vector_only` \| `rrf_normal` \| `rrf_weighted` \| `rrf_weighted_boosted`) for authoring QA — not used by harness scoring. |
| **H6** | **Embed + lexical policy unchanged** (SAM-E in embed; Tantivy on `search_text_for_fts`). |
| **H7** | **Authoring source of truth:** `scripts/retail/seed/abcd_demo_eval_spec.py` → applied by `apply_abcd_demo_eval.py`. |
| **H8** | v2 validator rules remain; add optional check that `demo_lift` values are valid enums. |

---

<h2 id="4-abcd" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. A/B/C/D mapping</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Arm</th><th><code>RETAIL_TICKET_SEARCH_MODE</code></th><th>Product</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>A</strong></td><td style="background:#f5f5f5"><code>vector_only</code></td><td style="background:#e8f5e9">V1</td></tr>
<tr><td style="background:#e3f2fd"><strong>B</strong></td><td style="background:#f5f5f5"><code>rrf_normal</code></td><td style="background:#fff3e0">V1.1 equal RRF</td></tr>
<tr><td style="background:#e3f2fd"><strong>C</strong></td><td style="background:#f5f5f5"><code>rrf_weighted</code></td><td style="background:#fff3e0">V1.2 70/30</td></tr>
<tr><td style="background:#e3f2fd"><strong>D</strong></td><td style="background:#f5f5f5"><code>rrf_weighted_boosted</code></td><td style="background:#ede7f6">V1.3 + code λ</td></tr>
</tbody>
</table>

---

<h2 id="5-design" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Eval design table (authoring intent)</h2>

Implemented in `scripts/retail/seed/abcd_demo_eval_spec.py`. Pattern: **neighbor bait** (intake wording overlaps wrong ticket’s story) + **gold evidence** (SAM-E / city / symptom terms) for lexical + λ.

| eval_id | Gold | demo_lift (intent) | Pattern |
|---------|------|-------------------|---------|
| eval-0001 | T-0042-000000 | `rrf_weighted_boosted` | Sydney A15: 5G-handover wording + **SAM-E100** (vector bait → 000042; λ lifts gold) |
| eval-0002 | T-0042-000005 | `vector_only` | NFC Canberra — easy semantic hit |
| eval-0003 | T-0042-000020 | `rrf_weighted_boosted` | A25 black screen Brisbane + **SAM-E110** |
| eval-0004 | T-0042-000015 | `vector_only` | Speaker Perth — paraphrase |
| eval-0005 | T-0042-000030 | `rrf_weighted_boosted` | Ghost-touch bait → 000012; **SAM-E115** + λ → gold 000030 |
| eval-0006 | T-0042-000025 | `vector_only` | NFC Melbourne — paraphrase |
| eval-0007 | T-0042-000010 | `rrf_weighted_boosted` | Adelaide fingerprint + **SAM-E105** |
| eval-0008 | T-0042-000035 | `rrf_normal` | Canberra A25 speaker crackle |
| eval-0009 | T-0042-000002 | `rrf_normal` | Brisbane 5G drop + **SAM-E101** |
| eval-0010 | T-0042-000040 | `rrf_weighted_boosted` | A16 black screen Adelaide + **SAM-E120** |

---

<h2 id="6-phases" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Phases</h2>

<h3 id="6-p1" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">6.1 P1 — Spec + apply script</h3>

- `abcd_demo_eval_spec.py` + `apply_abcd_demo_eval.py`; archive prior JSONL.
- **TDD:** `tests/test_retail_abcd_demo_eval.py` — spec validates, apply writes 10 lines, `validate_llm_corpus` passes.
- **Exit:** `./scripts/verify.sh` green.

<h3 id="6-p2" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">6.2 P2 — Operator A/B/C/D (Tantivy)</h3>

- `export RETAIL_LEXICAL_BACKEND=tantivy`; `05_run_abcd_postgres.sh` (PG already loaded; eval path picks new JSONL).
- Record recall@1 A/B/C/D in `phase6_operator_log.md`; optional `RETAIL_EVAL_TRACE_LEGS=1` on one arm.
- **Exit:** soft-monotonic table recorded; [§8](#8-acceptance) analysis if not met.

<h3 id="6-p3" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">6.3 P3 — Docs</h3>

- Update ABOUT §13.3 or add §13.4 with A/B/C/D ladder results + “demo eval” disclaimer.

---

<h2 id="7-checklist" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Execution checklist</h2>

- [X] **P1** — Spec, apply script, archive, tests, validator `demo_lift`
- [X] **P2** — A/B/C/D run + operator log (recall@1: **0.80 → 0.80 → 0.80 → 1.00**)
- [X] **P3** — ABOUT §13.4 + operator log; plan → `completed/`

<h3 id="7-results" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">7.1 Operator results (Tantivy, 2026-10-14)</h3>

| Arm | recall@1 | lexical_nonempty |
|-----|----------|------------------|
| A `vector_only` | **0.80** (8/10) | — |
| B `rrf_normal` | **0.80** | 10/10 |
| C `rrf_weighted` | **0.80** | 10/10 |
| D `rrf_weighted_boosted` | **1.00** (10/10) | 10/10 |

**Misses on A:** `eval-0001`, `eval-0005` (neighbor bait wins dense leg; gold at vector rank ~3). **D-only fixes:** V1.3 SAM-E λ in query; equal/70-30 RRF does not reorder top-1 on these rows.

**Follow-up (not blocking demo):** Author **B/C lift** rows without SAM-E in query (lexical rank 1–2, vector rank ≥3) or add historical soft-neighbor tickets so equal RRF wins before λ.

**TDD mode:** P1 **strict-TDD**; P2 **smoke-after-delete** (operator).

---

<h2 id="8-acceptance" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. Acceptance</h2>

- **Data:** `validate_llm_corpus.py` OK; no verbatim eval = gold body.
- **Demo ladder:** recall@1 non-decreasing across A→B→C→D **or** gap explained in operator log with per-row trace.
- **Lexical:** `lexical_nonempty ≥ 7/10` on **B** with Tantivy.

**Execute:** completed 2026-10-14 (`qimpltdd` on this plan).
