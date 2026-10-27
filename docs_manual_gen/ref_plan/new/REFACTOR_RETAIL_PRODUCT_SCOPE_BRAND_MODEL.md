<h1 id="ps-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor plan — retail product scope: brand + OEM model (no POS SKU filter)</h1>

**Parent (only):** [`REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md`](./REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md) — minor **M9** (cross-cutting **D1** metadata; unblocks **M4** B20 regression).  
**Status:** **new** — all implementable items **`[ ]`**.  
**Execute:** **`qimpltdd`** this file → **`aciubtdd`** / **`implreftdd`**.  
**last_aligned:** 2026-10-27 — user: drop synthetic SKU as retrieval filter; **brand + model** on ticket and manual legs; regression **T100** (tickets), **M90** (manual PG hybrid), **B20** (bundled).

**Problem:** Postgres has no **products** table. Tickets expose **`service_queries.model`** (OEM code); manuals expose **`manual_chunks.model_id`** (ingest folder slug, e.g. `ge_GNE27JYMFS`). Callers that treat those as one “SKU” caused **B20 manual leg empty** (see [`TEST_ANALYSIS_BUNDLED_MANUAL_TICKET_QA.md`](../../artifacts/TEST_ANALYSIS_BUNDLED_MANUAL_TICKET_QA.md) §4).

**Goal:** One **ProductScope** at the query boundary: **`brand`** + **`oem_model`** for **both** retrieval legs. Keep **`model_id`** on manual rows as **ingest path key only** (not the filter contract). **No** new POS SKU / products table in this minor (defer variant catalog to **M7**).

<h2 id="ps-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Decisions](#ps-decisions) — scope and naming.
2. [Target schema](#ps-schema) — columns and indexes.
3. [Phase 1 — Contract + schema](#ps-p1) — TDD + SQL migration.
4. [Phase 2 — Load and backfill](#ps-p2) — CSV load + PG backfill.
5. [Phase 3 — Retrieval wiring](#ps-p3) — tickets, manual PG, bundled, M90 path.
6. [Phase 4 — Unit and harness tests](#ps-p4) — pytest gates.
7. [Phase 5 — Operator regression trio](#ps-p5) — T100, M90, B20 + analysis docs.
8. [TDD bar](#ps-tdd) — per-phase modes.
9. [Execution checklist](#ps-checklist).
10. [Deferred](#ps-deferred).

---

<h2 id="ps-decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Decisions</h2>

| ID | Decision |
|----|----------|
| **PS-D1** | **Filter contract** = `(brand, oem_model)` on **ticket** and **manual** search. Same values on both legs for one incident. |
| **PS-D2** | **No `products` / retail SKU table** in M9. Source of truth for the sim remains **`fru_us_service.yaml`** (`brand` + `sku` field = OEM model + `docs_folder`). |
| **PS-D3** | **`manual_chunks.model_id`** retained for ingest lineage; **SQL filters** use **`brand` + `oem_model`** after backfill. |
| **PS-D4** | Deprecate retrieval use of **`catalog_sku`** / **`manual_filter` → slug**; keep **`ingest_key`** (optional) in JSON metadata for one release. |
| **PS-D5** | **Regression acceptance (non-worse):** T100 mode **C** recall@1 **≥ 0.54** + `check_abc_ladder.py` **OK**; M90 **`MANUAL_B_RAW_PG_HYBRID`** answerable judge **≥ 35/60**; B20 **ticket-in-packet ≥ 18/20** and **manual hits non-empty on all 20 rows** after scope fix. |
| **PS-D6** | Operator runs **after** schema backfill + reload on **`fru_us_1k`** profile (same env as P2.6 / B20 baselines). |

---

<h2 id="ps-schema" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Target schema</h2>

**New migration:** `scripts/retail/schema/006_product_brand_model.sql`

| Table | Add | Index |
|-------|-----|--------|
| `service_queries` | `brand TEXT NOT NULL DEFAULT ''` | `(brand, model)` where `model` = OEM code |
| `manual_chunks` | `brand TEXT NOT NULL DEFAULT ''`, `oem_model TEXT NOT NULL DEFAULT ''` | `(lane_id, brand, oem_model)` |

**Backfill:** SQL or `scripts/retail/ops/backfill_product_brand_model.py` driven by `CompanyProfile` (`brand` + `sku` ↔ `docs_folder`).

---

<h2 id="ps-p1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Phase 1 — Contract + schema</h2>

- [X] Extend **`CompanyProfile`**: mapping via **`product_for_oem`** / **`product_for_ingest_key`** on YAML models list.
- [X] Refactor **`ProductScope`**: **`brand`**, **`oem_model`**, **`ingest_key`**; **`manual_filter`** / **`ticket_filter`** → **`ProductFilter`**.
- [X] Add **`006_product_brand_model.sql`**.
- [X] Red-first: **`tests/retail/test_product_scope.py`** — GE + GNE27JYMFS on both legs.

---

<h2 id="ps-p2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phase 2 — Load and backfill</h2>

- [X] **`load_service_queries.py`**: set **`brand`** from profile when inserting CSV rows.
- [X] **`manual_pg_ingest` / upsert**: populate **`brand`**, **`oem_model`** from YAML via **`model_id`**.
- [X] **Backfill script** — **`scripts/retail/ops/backfill_product_brand_model.py`**.
- [ ] **`fru_tickets.py` / CSV generator** (optional): emit **`brand`** column in CSV for clarity.

---

<h2 id="ps-p3" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Phase 3 — Retrieval wiring</h2>

- [X] **`pg_search.py`**: **`brand_filter`** + **`model_filter`** on vector leg; model-only fallback if brand empty.
- [X] **Tantivy / lexical**: **model-only** (OEM codes unique in sim; vector leg uses brand+model).
- [X] **`manual_pg_search` / `filter_chunks_by_product`**: brand + OEM on PG pool.
- [X] **`bundled_runner.py`**, **`answer_tickets.py`**, M90 **`runner.py`**: **`resolve_product_scope`** → **`ProductFilter`**.
- [ ] Update **`TEST_ANALYSIS_BUNDLED_MANUAL_TICKET_QA.md`** §4.1 prose to **brand+model** (after P5 operator run).

---

<h2 id="ps-p4" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Phase 4 — Unit and harness tests</h2>

- [X] **`test_bundled_manual_filter.py`**, **`test_manual_pg_search.py`** product filter.
- [ ] **`tests/retail/test_pg_search*.py`** or hybrid tests: product filter narrows ids (optional).
- [X] **`./scripts/verify.sh`** green.

---

<h2 id="ps-p5" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Phase 5 — Operator regression trio</h2>

**Env (all three):** `set -a && source .env && set +a`; `PYTHONPATH=$PWD/scripts/retail`; `RETAIL_LEXICAL_BACKEND=tantivy`; `RETAIL_SIM_DATA_PROFILE=fru_us_1k`; PG up + backfill applied.

| Run | Command (summary) | Artifact |
|-----|-------------------|----------|
| **T100 tickets** | `RETAIL_TICKET_SEARCH_MODE=rrf_term_boosted` `./scripts/py scripts/retail/eval/eval_ticket_search.py --postgres --report ops/runs/fru-ticket-brand-model-YYYYMMDD/c.json`; copy reports for **`check_abc_ladder.py`** if full ABC rerun | Update **`TEST_ANALYSIS_A3_TICKET_RAG.md`** |
| **M90 manual only** | `python -m tests.retail_multi_profiles --full --profile MANUAL_B_RAW_PG_HYBRID --run-id m90-brand-model-YYYYMMDD --retrieval-mode raw_rag` | Update **`TEST_ANALYSIS_A2_MANUAL_RAG_PG.md`** headline |
| **B20 bundled** | `./scripts/py tests/retail_multi_profiles/run_bundled_qa.py --full --run-id b20-brand-model-YYYYMMDD` | Update **`TEST_ANALYSIS_BUNDLED_MANUAL_TICKET_QA.md`** |

- [X] Run **T100** mode **C** — `ops/runs/fru-ticket-brand-model-20261027/c.json` recall@1 **0.54** (meets **PS-D5**).
- [X] Run **M90** — `ops/runs/retail-lane-abcd-raw/m90-brand-model-20261027/` (**63/90** overall; **33/60** answerable judge pass).
- [X] B20 **smoke** — `b20-brand-model-smoke-20261027` (BND-E01: **5** manual chunks, judge pass).
- [X] Run **B20 full 20** — `b20-brand-model-20261027`: **14/20** judge, **10/20** ticket-in-packet, **0** empty manual legs.
- [ ] Record **`last_aligned`** on this plan; tick checklist.

**Neatlog:** `logs/ops/retail-*` per **neatlog** rule on B20 and M90 long runs.

---

<h2 id="ps-tdd" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. TDD bar</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Phase</th><th>TDD mode</th><th>Test-first artifact</th><th>Red case</th><th>Green gate</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">P1 Contract</td><td style="background:#e8f5e9">strict-TDD</td><td><code>tests/retail/test_product_scope.py</code></td><td>Scope expects GE+GNE27JYMFS filters before impl</td><td><code>pytest tests/retail/test_product_scope.py</code></td></tr>
<tr><td style="background:#e3f2fd">P2 Load</td><td style="background:#e8f5e9">strict-TDD</td><td><code>tests/retail/test_load_service_queries_brand.py</code> (new) or extend loader test</td><td>Loaded row missing brand fails</td><td>pytest loader tests</td></tr>
<tr><td style="background:#e3f2fd">P3 Retrieval</td><td style="background:#e8f5e9">strict-TDD</td><td><code>tests/retail/test_product_filter_pg.py</code>, <code>test_bundled_manual_filter.py</code></td><td>Manual filter by slug only fails</td><td>pytest retail + bundled filter tests</td></tr>
<tr><td style="background:#e3f2fd">P4 Harness</td><td style="background:#e8f5e9">strict-TDD</td><td>Existing suite tests unchanged count</td><td>—</td><td><code>./scripts/verify.sh</code></td></tr>
<tr><td style="background:#e3f2fd">P5 Operator</td><td style="background:#fff8e1">smoke-after-delete</td><td>—</td><td>—</td><td>PS-D5 metrics + analysis docs updated</td></tr>
</tbody>
</table>

---

<h2 id="ps-checklist" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">9. Execution checklist</h2>

- [X] P1 — ProductScope + schema **006**
- [X] P2 — Load + backfill
- [X] P3 — pg_search + manual PG + bundled/M90 wiring
- [X] P4 — verify.sh
- [ ] P5 — T100 + M90 + B20 operator + TEST_ANALYSIS updates

---

<h2 id="ps-deferred" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">10. Deferred</h2>

| Item | Owner |
|------|--------|
| **`products` / POS SKU / color / bundle / region** tables | **M7** FRU product ops |
| B20 JSON migration to explicit **`brand`** field | Optional; resolver + YAML sufficient for sim |
| Rename YAML key **`sku`** → **`oem_model`** | Docs-only follow-up |
