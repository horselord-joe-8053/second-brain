<h1 id="sim-scale-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor: simulated retail corpus scale (60/10 → 1000/100)</h1>

**Status:** **wip**  
**Branch:** `feature/bootstrap-rrf-evolve-6-lexical-abc-1000-100`  
**Execute:** `qimpltdd docs_manual_gen/ref_plan/new/REFACTOR_RETAIL_SIM_DATA_SCALE_1K.md`

<h2 id="sim-scale-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Goal](#1-goal) — layout, profiles, ABC eval at scale.
2. [Decisions](#2-decisions) — paths, profile ids, ratios.
3. [Phases](#3-phases) — move, centralize, generate, wire, verify.
4. [TDD bar](#4-tdd) — tests per phase.
5. [Checklist](#5-checklist) — progress.
6. [Acceptance](#6-acceptance)

---

<h2 id="1-goal" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Goal</h2>

- **`scripts/retail/sim_data/`** — home for **profile snapshots** + **shared generation** code.
- **`profiles/data_60_10/`** — archive current **60 historical + 10 eval** (moved from `tmp/simulated_data/`).
- **`profiles/data_1000_100/`** — freshly generated **1000 historical + 100 eval** (natural diversity; **A &lt; B &lt; C** teaching mix).
- **Centralize** ticket/eval generation; profile-specific entrypoints only where counts or ABC templates differ.
- **Default profile** on this branch: **`rrf_data_llm_gen_1k`** → `data_1000_100`.

---

<h2 id="2-decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Decisions</h2>

**last_aligned:** 2026-10-14

| ID | Decision |
|----|----------|
| **S1** | Profile dirs: `scripts/retail/sim_data/profiles/data_60_10`, `…/data_1000_100`. |
| **S2** | Profile env ids: `rrf_data_llm_gen_60_10`, `rrf_data_llm_gen_1k`; **`rrf_data_llm_gen`** aliases **60_10** for backward compat; default **`rrf_data_llm_gen_1k`**. |
| **S3** | Eval mix (100 rows): **50** `paraphrase` / **30** `hybrid_stress` / **20** `code_in_query`; `demo_lift` **50** `vector_only` / **30** `rrf_normal` / **20** `rrf_term_boosted`. |
| **S4** | Hybrid/code intakes reuse **P4 product-story** templates (closed/mis-route bait + open issue; SAM-E on C rows only). |
| **S5** | `generate_llm_corpus_v2.py` → thin shim to `sim_data.generation.cli`. |
| **S6** | Reports stay under each profile’s `reports/` (not committed except operator snapshots as today). |

---

<h2 id="3-phases" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Phases</h2>

<h3 id="3-p1" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">P1 — Layout + move 60/10</h3>

- Create `sim_data/` tree; **git mv** CSV/manifest/eval/prompts into `profiles/data_60_10/`.
- Copy frozen **`abcd_demo_eval_spec`** apply output into profile eval JSONL if needed.
- **Exit:** files present; README in `sim_data/`.

<h3 id="3-p2" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">P2 — Shared generation (strict-TDD)</h3>

- Extract catalog + historical writer from `generate_llm_corpus_v2.py` → `sim_data/generation/`.
- **`eval_abc_ladder.py`** — programmatic 100-row ladder; **`profiles.py`** — 60/10 vs 1000/100 counts/seeds.
- **Exit:** `tests/test_retail_sim_data_generation.py` green.

<h3 id="3-p3" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">P3 — Generate 1000/100 + validate</h3>

- CLI: `python -m retail.sim_data.generation.cli --profile data_1000_100`.
- `validate_llm_corpus.py --corpus-dir …/data_1000_100`.
- **Exit:** 1000 CSV rows, 100 eval lines, validator OK.

<h3 id="3-p4" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">P4 — Wire profiles + shims</h3>

- `sim_data_profile.py` registry; update prep scripts/tests/docs pointers.
- **Exit:** `./scripts/verify.sh` green.

<h3 id="3-p5" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">P5 — Operator smoke (optional HG)</h3>

- Reload PG + `05_run_abc_postgres.sh` on **1k** profile; record recall@1 in operator log if embed API available.
- **Exit:** strict **A &lt; B &lt; C** preferred or documented.

---

<h2 id="4-tdd" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. TDD bar</h2>

| Phase | Test-first contract |
|-------|---------------------|
| P2 | Generation module imports; 60-ticket deterministic snapshot hash or row counts |
| P3 | 1000/100 file counts; eval strata/demo_lift counts |
| P4 | `test_retail_sim_data_profile.py` paths for both profiles |

---

<h2 id="5-checklist" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Checklist</h2>

- [X] **P1** — Move `data_60_10`
- [X] **P2** — Shared `sim_data/generation`
- [X] **P3** — Generate `data_1000_100`
- [X] **P4** — Profile registry + verify
- [ ] **P5** — ABC operator smoke (best effort — run after PG reload + embed)

---

<h2 id="6-acceptance" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Acceptance</h2>

- Both profiles under `scripts/retail/sim_data/profiles/`.
- Default env profile **`rrf_data_llm_gen_1k`** with committed 1000+100 artifacts.
- `./scripts/verify.sh` green.
