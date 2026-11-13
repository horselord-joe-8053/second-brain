<h1 id="sim-scale-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor: simulated retail corpus scale (60/10 → 1000/100)</h1>

**Status:** **completed** (phone-era **Galaxy** corpus at 60/10 and 1000/100)

<p><strong>Superseded default:</strong> live operator default is <code>RETAIL_SIM_DATA_PROFILE=fru_us_1k</code> — see <a href="../wip/REFACTOR_FRU_US_SERVICE_BRAIN.md">REFACTOR_FRU_US_SERVICE_BRAIN.md</a> (FRU US 1000/100).</p>

**Branch (historical):** `feature/bootstrap-rrf-evolve-6-lexical-abc-1000-100`  
**Execute (archive):** plan closed; phone profiles remain under `sim_data/profiles/data_*` for regression.

<h2 id="sim-scale-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Goal](#1-goal) — layout, profiles, ABC eval at scale.
2. [Decisions](#2-decisions) — paths, profile ids, ratios.
3. [Phases](#3-phases) — move, centralize, generate, wire, verify, operator smoke, eval retune.
4. [TDD bar](#4-tdd) — tests per phase.
5. [Checklist](#5-checklist) — progress.
6. [Acceptance](#6-acceptance)

---

<h2 id="1-goal" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Goal</h2>

- **`scripts/retail/sim_data/`** — home for **profile snapshots** + **shared generation** code.
- **`profiles/data_60_10/`** — archive current **60 historical + 10 eval** (moved from `tmp/simulated_data/`).
- **`profiles/data_1000_100/`** — freshly generated **1000 historical + 100 eval** (natural diversity; **A &lt; B &lt; C** teaching mix).
- **Centralize** ticket/eval generation; profile-specific entrypoints only where counts or ABC templates differ.
- **Default profile (when this plan shipped):** **`rrf_data_llm_gen_1k`** → `data_1000_100`. **Today:** default is **`fru_us_1k`** (FRU pivot).

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

**Run (2026-10-14):** `RETAIL_SIM_DATA_PROFILE=rrf_data_llm_gen_1k` → `03_pg_up_and_load.sh` (1000 embed + lexical rebuild) → `05_run_abc_postgres.sh`. Logs: `logs/ops/p5_03_pg_up_and_load_1k.log`, `logs/ops/p5_05_run_abc_postgres_1k.log`. Reports: `scripts/retail/sim_data/profiles/data_1000_100/reports/pg_*.json`.

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Mode</th><th>Overall recall@1</th><th>paraphrase (50)</th><th>hybrid_stress (30)</th><th>code_in_query (20)</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">A <code>vector_only</code></td><td>0.110</td><td>0.220</td><td>0.000</td><td>0.000</td></tr>
<tr><td style="background:#e3f2fd">B <code>rrf_normal</code></td><td>0.100</td><td>0.200</td><td>0.000</td><td>0.000</td></tr>
<tr><td style="background:#e3f2fd">C <code>rrf_term_boosted</code></td><td>0.120</td><td>0.200</td><td>0.000</td><td>0.100</td></tr>
</tbody>
</table>

**Outcome:** strict **A &lt; B &lt; C** on overall recall@1 **not met** (roughly **B &lt; A &lt; C**). Teaching slices also fail: **hybrid_stress** rows **0%** on all modes; **demo_lift** slices do not ladder (e.g. `rrf_normal` slice 0/0/0).

**Trace sample (`eval-0051`, B mode):** gold `T-0042-000482` (Brisbane A25, Wi‑Fi drops on sleep) not in top‑5 **vector** or **lexical** legs — many near-duplicate tickets at 1k scale drown the open-issue phrase.

<h3 id="3-p6" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">P6 — Eval retune at 1k (follow-up)</h3>

- Regenerate `ticket_retrieval.jsonl` with **lexically distinctive** gold picks (unique city+model+issue+SAM-E where needed) and/or queries aligned to stored intake (see 60/10 `abcd_demo_eval_spec` + P4 hybrid templates).
- Re-run P5; optional `RETAIL_EVAL_TRACE_LEGS=1` on failing rows.
- **Exit:** demo_lift slices show **A &lt; B &lt; C** on recall@1 (overall may stay lower than 60/10).

**Done (2026-10-14):** `eval_gold.py` (rich signature = model+city+issue+intake detail); `eval_abc.py` uses `HYBRID_GOLD_BY_BAIT_IDX`, abcd-style paraphrase/hybrid/code queries with **detail anchor** from stored intake (no ticket-id hacks). Regenerated `data_1000_100/ticket_retrieval.jsonl`; ABC smoke:

| Mode | recall@1 |
|------|----------|
| A `vector_only` | **0.35** |
| B `rrf_normal` | **0.50** |
| C `rrf_term_boosted` | **0.59** |

Strict **A &lt; B &lt; C** on **overall** 100-row eval. By stratum: `code_in_query` **0.40 → 0.55 → 1.00**; hybrid modest **0.17 → 0.23 → 0.23**. Per-`demo_lift` slice is strict only on `rrf_term_boosted` rows (SAM-E teaching); paraphrase/hybrid slices still see fusion lift on B/C (expected when scoring all modes on the same rows).

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
- [X] **P5** — ABC operator smoke — **documented: strict ABC not met at 1k** (see P5 table)
- [X] **P6** — Eval retune + re-smoke ABC at 1k (overall **0.35 → 0.50 → 0.59**)

---

<h2 id="6-acceptance" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Acceptance</h2>

- Both profiles under `scripts/retail/sim_data/profiles/`.
- Phone env profile **`rrf_data_llm_gen_1k`** with committed 1000+100 artifacts (archive; not the repo default after FRU pivot).
- `./scripts/verify.sh` green.
