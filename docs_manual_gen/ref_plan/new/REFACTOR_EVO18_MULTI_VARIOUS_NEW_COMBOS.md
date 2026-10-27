<h1 id="evo18-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor plan — evo-18 multi-dimensional manual RAG combos (T0 + D2 + D7)</h1>

**Parent (only):** [`REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md`](./REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md) — minor **M10** (Lane B PG hybrid + bundled B20 experiment matrix).  
**Depends on:** [`REFACTOR_RETAIL_PRODUCT_SCOPE_BRAND_MODEL.md`](./REFACTOR_RETAIL_PRODUCT_SCOPE_BRAND_MODEL.md) (**M9**) — brand + OEM filters on both legs (code landed; this minor adds **SQL-first pool** + **manual Tantivy** + chunk/orchestration experiments).  
**Branch:** `feature/evo-18-multi-various-new-combos`.  
**Status:** **wip** — **`qimpltdd`** / **`aciubtdd`** / **`implreftdd`**.  
**last_aligned:** 2026-10-27 — user: one-Δ combos; **k_tickets=2** fixed; **D2.page_pack** only when **D2=page_heading**; promote **T0 → D2 page_heading → page_pack A/B → D7**; record **B20 + T100 + M90** + latency per combo vs frozen baseline.

**Goal:** Ship **T0 baseline fixes** (not A/B), then add **run profiles** for **D2 chunk policy**, **D2.page_pack**, and **D7 query decomposition**, each with operator **regression trio** and **`TEST_ANALYSIS_*`** comparison to the **20261027 baseline**.

<h2 id="evo18-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Decisions](#evo18-decisions) — dimensions and promotion.
2. [Frozen baseline (pre-T0)](#evo18-baseline) — B20, T100, M90 + performance.
3. [Run profile registry](#evo18-profiles) — combo IDs and one-Δ rule.
4. [Phase P0 — Plan + logging contract](#evo18-p0) — resolved profile + neatlog.
5. [Phase P1 — T0 baseline fixes](#evo18-p1) — SQL pool + manual Tantivy.
6. [Phase P2 — D2 chunk re-ingest](#evo18-p2) — `fixed_2k` vs `page_heading`.
7. [Phase P3 — D2.page_pack](#evo18-p3) — sub-knob when `page_heading`.
8. [Phase P4 — D7 decomposition](#evo18-p4) — bundled + M90 hooks.
9. [Phase P5 — Operator matrix + analysis docs](#evo18-p5) — per-combo trio.
10. [TDD bar](#evo18-tdd) — strict vs operator smoke.
11. [Quality bar](#evo18-quality) — cdcm, neatlog, analysis.
12. [Execution checklist](#evo18-checklist).
13. [Deferred](#evo18-deferred).

---

<h2 id="evo18-decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Decisions</h2>

| ID | Decision |
|----|----------|
| **E18-D1** | **Baseline label** = **PRE-T0** profile **`MANUAL_B_RAW_PG_HYBRID`**: M9 brand+OEM filter **in Python after `LIMIT 200` pool**, manual lexical = **in-process overlap** (`raw_lexical.rank_chunks_lexical`). Frozen run-ids **20261027** (table §2). |
| **E18-D2** | **T0** (merge without A/B): **SQL `WHERE lane_id AND brand AND oem_model`** before pool cap; manual lexical = **Tantivy BM25** index keyed by **`manual_chunk_id`** (separate directory from ticket Tantivy). |
| **E18-D3** | **D2** top-level: **`fixed_2k`** (current) vs **`page_heading`** (re-ingest). **D2.page_pack** only when **D2=page_heading**: **`global_top5`** (default) vs **`page_top5`**. |
| **E18-D4** | **D7**: **`none`** vs **`decompose`** (sub-queries for manual leg; ticket leg unchanged in P4). |
| **E18-D5** | **k_tickets=2**, **k_manuals=5** — not matrix dimensions. |
| **E18-D6** | **One-Δ per operator run:** change exactly one of {T0 lexical/SQL, D2, D2.page_pack, D7} vs previous promoted profile; log **`resolved_run_profile`** JSON on every harness row. |
| **E18-D7** | **Acceptance (non-worse vs PRE-T0):** T100 mode **C** recall@1 **≥ 0.54**; M90 **`MANUAL_B_RAW_PG_HYBRID`** answerable **≥ 33/60**; B20 **≥ 14/20** judge and **0** empty manual legs — unless analysis doc records **intentional trade** with manual-leg recall gain on **b20-customer-six**. |
| **E18-D8** | **Analysis home:** per-combo sections in [`TEST_ANALYSIS_BUNDLED_MANUAL_TICKET_QA.md`](../../artifacts/TEST_ANALYSIS_BUNDLED_MANUAL_TICKET_QA.md) (B20), [`TEST_ANALYSIS_A2_MANUAL_RAG_PG.md`](../../artifacts/TEST_ANALYSIS_A2_MANUAL_RAG_PG.md) (M90), [`TEST_ANALYSIS_A3_TICKET_RAG.md`](../../artifacts/TEST_ANALYSIS_A3_TICKET_RAG.md) (T100); registry row in [`REALIGNMENT_DIMENSIONS.md`](../../artifacts/aggregated/REALIGNMENT_DIMENSIONS.md) §Experiment registry. |

---

<h2 id="evo18-baseline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Frozen baseline (PRE-T0, 20261027)</h2>

**Git head (runs):** `277b0f2bcdffb945e063ee783ac33bf41ae27f0f` · **Env:** `RETAIL_SIM_DATA_PROFILE=fru_us_1k`, `RETAIL_LEXICAL_BACKEND=tantivy` (tickets only), manual leg overlap lexical, M9 filters active.

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Suite</th><th>Run ID</th><th>Headline metric</th><th>Performance (median ms per question)</th><th>Artifact</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>B20</strong> bundled</td><td><code>b20-brand-model-20261027</code></td><td>Judge pass <strong>14/20</strong>; ticket-in-packet <strong>10/20</strong>; manual non-empty <strong>20/20</strong></td><td>manual_retrieval <strong>456</strong>; answer <strong>1504</strong>; judge <strong>1743</strong></td><td><code>ops/runs/retail-bundled-qa/b20-brand-model-20261027/</code></td></tr>
<tr><td style="background:#e3f2fd"><strong>B20</strong> six customer</td><td><code>b20-customer-six-20261027</code></td><td>Judge <strong>0/6</strong> (manual ranking failures; gate for D7/D2)</td><td>same harness fields as B20</td><td><code>ops/runs/retail-bundled-qa/b20-customer-six-20261027/</code></td></tr>
<tr><td style="background:#e3f2fd"><strong>T100</strong> tickets</td><td><code>fru-ticket-brand-model-20261027</code></td><td>Mode <strong>C</strong> recall@1 <strong>0.54</strong> (paraphrase 0.56, hybrid_stress 0.43, code_in_query 0.65)</td><td>Retrieval-only suite (no answer/judge latency in <code>c.json</code>)</td><td><code>ops/runs/fru-ticket-brand-model-20261027/c.json</code></td></tr>
<tr><td style="background:#e3f2fd"><strong>M90</strong> manual PG hybrid</td><td><code>m90-brand-model-20261027</code></td><td>Overall pass <strong>63/90</strong>; answerable (60) <strong>33/60</strong></td><td>retrieval <strong>444</strong>; answer <strong>1131</strong>; judge <strong>1282</strong>; E2E ~<strong>3127</strong></td><td><code>ops/runs/retail-lane-abcd-raw/m90-brand-model-20261027/</code></td></tr>
</tbody>
</table>

**Copy-forward rule:** Each new combo run appends a row to §Experiment registry and a **Comparison vs PRE-T0** subsection in the three TEST_ANALYSIS docs (metrics + latency deltas + failure class notes).

---

<h2 id="evo18-profiles" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Run profile registry</h2>

| Profile ID | Δ vs prior | D2 chunk | D2.page_pack | Manual lexical | D7 | Default suite |
|------------|------------|----------|------------|----------------|-----|---------------|
| **PRE-T0** (baseline) | — | `fixed_2k` | n/a | overlap | `none` | recorded 20261027 |
| **EVO18-T0** | SQL pool + Tantivy | `fixed_2k` | n/a | **tantivy** | `none` | P5 trio |
| **EVO18-D2-PAGE** | chunk policy | **`page_heading`** | `global_top5` | tantivy | `none` | P5 trio |
| **EVO18-D2-PAGE-PACK-PAGE** | page_pack | `page_heading` | **`page_top5`** | tantivy | `none` | P5 trio |
| **EVO18-D7-DECOMPOSE** | orchestration | promoted D2 | promoted pack | tantivy | **`decompose`** | B20 six + trio |

**Harness mapping:** Extend [`tests/retail_multi_profiles/data/run-config.yaml`](../../../tests/retail_multi_profiles/data/run-config.yaml) and [`RUN_PROFILES.md`](../../../tests/retail_multi_profiles/docs/RUN_PROFILES.md) with **`evo18_*`** fields mirrored in **`resolved_run_profile`** (`d2_chunk`, `d2_page_pack`, `d7`, `manual_lexical_backend`).

---

<h2 id="evo18-p0" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phase P0 — Plan + logging contract</h2>

- [X] Author this minor (**M10**) + main hierarchy row.
- [X] Freeze PRE-T0 baseline table (§2).
- [X] **`resolved_run_profile`**: emit **evo18** dimension fields on M90 + B20 result rows (`config_snapshot.evo18`).
- [ ] **Neatlog** paths documented for long runs (`logs/ops/retail-*`).

---

<h2 id="evo18-p1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Phase P1 — T0 baseline fixes</h2>

- [X] **`manual_pg_db.list_manual_chunks` / `knn_manual_chunks`**: optional **`brand` + `oem_model`** SQL predicates (index-friendly).
- [X] **`ManualTantivyLexicalIndex`**: `chunk_id`, `body`, `brand`, `oem_model`; rebuild from PG lane rows; path **`tmp/retail_lexical/manual_tantivy`** (or `RETAIL_MANUAL_LEXICAL_INDEX_PATH`).
- [X] **`manual_pg_search`**: `RETAIL_MANUAL_LEXICAL_BACKEND=tantivy|overlap`; wire Tantivy leg; stop loading unfiltered **200** row pool when product filter active.
- [X] Rebuild hook after **`manual_pg_ingest`** (lane fresh) or **`scripts/retail/rebuild_manual_lexical_index.py`**.
- [X] Tests: SQL filter contract; Tantivy ranks gold chunk above overlap on stopword-heavy query (H10-style fixture).
- [X] **`./scripts/verify.sh`** green.

---

<h2 id="evo18-p2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Phase P2 — D2 chunk re-ingest</h2>

- [X] **`raw_chunking`**: implement **`page_heading`** policy (page/heading boundaries from Markdown structure).
- [X] Ingest flag **`RETAIL_MANUAL_D2_CHUNK`**: re-embed Lane B (**592** chunks); version **`v2-page-heading-max2000`**.
- [X] Operator **M90 + B20** — `m90-evo18-d2-page-20261028`, `b20-evo18-d2-page-20261028`.
- [X] Update **TEST_ANALYSIS** comparison vs **EVO18-T0** and PRE-T0.

---

<h2 id="evo18-p3" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Phase P3 — D2.page_pack</h2>

- [X] When **D2=page_heading**, fusion step **`global_top5`** vs **`page_top5`** (cap chunks per source page before RRF).
- [X] Operator **`m90-evo18-d2-pack-page-20261028`**, **`b20-evo18-d2-pack-page-20261028`** (page_top5 wins M90 vs global).

---

<h2 id="evo18-p4" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. Phase P4 — D7 decomposition</h2>

- [X] Wire minimal **D7** path: **`RETAIL_D7=decompose`** + `manual_query_decompose.split_query_units` on manual hybrid leg.
- [X] **b20-evo18-d7-six-20261028** **3/6** judge (was **0/6** PRE-T0 six); full **`b20-evo18-d7-20261028`**, **`m90-evo18-d7-20261028`** recorded.

---

<h2 id="evo18-p5" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">9. Phase P5 — Operator matrix + analysis docs</h2>

**Env (each combo):** `set -a && source .env && set +a`; `PYTHONPATH=$PWD/scripts/retail`; `RETAIL_SIM_DATA_PROFILE=fru_us_1k`; PG migrated + backfill; ticket Tantivy rebuilt.

| Combo | T100 | M90 | B20 | Run-id suffix |
|-------|------|-----|-----|----------------|
| **EVO18-T0** | `fru-ticket-evo18-t0-YYYYMMDD/c.json` | `m90-evo18-t0-YYYYMMDD` | `b20-evo18-t0-YYYYMMDD` | `evo18-t0` |
| **EVO18-D2-PAGE** | same mode C | `m90-evo18-d2-page-*` | `b20-evo18-d2-page-*` | `evo18-d2-page` |
| **EVO18-D2-PAGE-PACK-PAGE** | — | `m90-evo18-d2-pack-page-*` | `b20-evo18-d2-pack-page-*` | `evo18-d2-pack-page` |
| **EVO18-D7-DECOMPOSE** | optional | `m90-evo18-d7-*` | `b20-evo18-d7-*` + **six** | `evo18-d7` |

- [X] **EVO18-T0** trio recorded + TEST_ANALYSIS § comparison.
- [X] **D2 / page_pack / D7** rows per promotion order (registry §11 updated).
- [X] **`last_aligned`** 2026-10-28 — promote **page_heading + page_top5 + Tantivy**; keep **T0** ticket path; B20 full best **14/20** on D2 (matches PRE-T0).

---

<h2 id="evo18-tdd" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">10. TDD bar</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Phase</th><th>TDD mode</th><th>Test-first artifact</th><th>Green gate</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">P1 T0</td><td style="background:#e8f5e9">strict-TDD</td><td><code>tests/retail/test_manual_pg_db_product_sql.py</code>, <code>tests/retail/test_manual_tantivy_lexical.py</code></td><td><code>pytest tests/retail/test_manual_pg*.py tests/retail/test_manual_tantivy_lexical.py</code></td></tr>
<tr><td style="background:#e3f2fd">P2 D2</td><td style="background:#e8f5e9">strict-TDD</td><td><code>tests/retail_multi_profiles/test_raw_chunking_page_heading.py</code></td><td>chunk boundary unit tests + ingest smoke</td></tr>
<tr><td style="background:#e3f2fd">P3 page_pack</td><td style="background:#e8f5e9">strict-TDD</td><td><code>tests/retail/test_manual_page_pack.py</code></td><td>fusion cap tests</td></tr>
<tr><td style="background:#e3f2fd">P4 D7</td><td style="background:#e8f5e9">strict-TDD</td><td>decomposition contract tests (manual leg)</td><td>pytest + bundled smoke</td></tr>
<tr><td style="background:#e3f2fd">P5 Operator</td><td style="background:#fff8e1">smoke-after-delete</td><td>—</td><td>E18-D7 metrics + analysis docs</td></tr>
</tbody>
</table>

---

<h2 id="evo18-quality" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">11. Quality bar</h2>

- **cdcm:** file headers + doc line on new modules (`ManualTantivyLexicalIndex`, SQL helpers, chunk policies).
- **neatlog:** B20/M90 full runs log under `logs/ops/`.
- **onlyref:** no production code in this plan file; checklist only.

---

<h2 id="evo18-checklist" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">12. Execution checklist</h2>

- [X] P0 logging contract
- [X] P1 T0 SQL + manual Tantivy
- [X] P5 EVO18-T0 operator trio + TEST_ANALYSIS deltas
- [X] P2 D2 page_heading + P5 run
- [X] P3 page_pack + P5 run
- [X] P4 D7 + P5 run (incl. customer-six)
- [X] Main plan M10 row + REALIGNMENT experiment registry complete

---

<h2 id="evo18-deferred" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">13. Deferred</h2>

- **D2.enrich** (metadata vs LLM augment) — separate minor after D2 stable.
- **Synonym expansion** — not dimensionized.
- **k_tickets** experiments — fixed at 2.
