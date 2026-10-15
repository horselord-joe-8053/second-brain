<h1 id="fru-product-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor: FRU US retail service Second Brain (product path)</h1>

**Status:** **wip** — V3 prep docs **`[X]`**; V2 / platform / V4 / V5 **`[ ]`**  
**Execute order:** (1) `qimpltdd docs_manual_gen/ref_plan/wip/REFACTOR_BRAIN_PROFILES_AND_RETAIL_ANSWER.md` (Platform phase); (2) manual HG-P2 + HG-2; (3) `qimpltdd docs_manual_gen/ref_plan/wip/REFACTOR_FRU_RETAIL_SERVICE_BRAIN.md` for V2 → V4 → V5.

**Goal:** When a **new aftersales ticket** arrives, the agent finds the right **historical resolved ticket** (Postgres + hybrid search) and, **always alongside** (brain-profiles **E2**), the right **user/repair manual** passages cited to PDF path + page (LLM Wiki over fridge PDFs) — same architecture as the Samsung phone prototype, **US market + three fridge SKUs**.

**Prerequisites (done elsewhere):**

| Prerequisite | Plan |
|--------------|------|
| Ticket search A/B/C on FRU 1k corpus | [`REFACTOR_FRU_US_SERVICE_BRAIN.md`](../completed/REFACTOR_FRU_US_SERVICE_BRAIN.md) (**completed**) |
| Phone-era search stack + sidecar V1 | [`REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md`](../completed/REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md) phases 0–7 |
| Sim-data scale patterns | [`REFACTOR_RETAIL_SIM_DATA_SCALE_1K.md`](../completed/REFACTOR_RETAIL_SIM_DATA_SCALE_1K.md) |

**Article:** [`ABOUT_SEARCH_RRF_FRU.md`](../../artifacts/ABOUT_SEARCH_RRF_FRU.md) (close **`TBD-P10`** in corpus pivot plan P10).

<h2 id="outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Scope](#1-scope) — in / out; two planes.
2. [Decisions](#2-decisions) — grill + inherited D1–D13 (FRU wording).
3. [Architecture](#3-architecture) — routing: tickets → wiki.
4. [Phases](#4-phases) — V2 → platform → V3 → V4 → V5 (full stack order).
5. [Quality bar](#5-quality) — tests and operator gates.
6. [Checklist](#6-checklist) — progress.
7. [Acceptance](#7-acceptance) — product demo bar.
8. [Deferred](#8-deferred) — sales join, fourth SKU.

---

<h2 id="1-scope" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Scope</h2>

**In scope**

- **Structured plane:** `service_queries` in Postgres; default corpus **`fru_us_1k`**; search modes **`vector_only` / `rrf_normal` / `rrf_term_boosted`**; Tantivy lexical leg; **`FRU-E###`** term boost; **`customer_id`** join key (column only — never in query text).
- **Unstructured plane:** 6 PDFs under `brain/retail/raw/sources/fridge-docs/` compiled to `brain/retail/wiki/` via Hermes **`llm_wiki`** (model-scoped paths: `samsung_RF28K9070SG`, `ge_GNE27JYMFS`, `kitchenaid_KRFF507HPS`).
- **Product routing:** `query-retail-brain` skill — resolved-ticket reuse first (**D2**), then manual search; optional manager SQL path in **V5**.
- **Operator docs:** split Cursor prep vs Hermes wiki runbooks (**V3**).
- **Agent loop:** HTTP sidecar with **`semantic_search`**, **`generate_sql`**, **`execute_sql`**, wiki tool calls (**V5**).

**Out of scope (this plan)**

- Merging ultra-fru **sales** DB into Postgres (separate analytics project; only **`customer_id`** continuity here).
- Replacing Gemini embeddings or RRF constants (frozen per FRU corpus pivot **F8**).

---

<h2 id="2-decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Decisions</h2>

**last_aligned:** 2026-10-15 — **grillnow** (plan ledger + product scope).

| ID | Decision | Rationale |
|----|----------|-----------|
| **G1** | Corpus pivot plan stays **`wip/`** until P10–P12 closeout. | Article + specs still open. |
| **G2** | Phone scale plan → **`completed/`** as archive. | Default profile is **`fru_us_1k`**. |
| **G3** | Samsung master → **`completed/`**; V2–V5 continue here. | Avoid two “master” wips. |
| **G4** | **Full stack** order: **V2 → platform (optional) → V3 → V4 → V5**. | Matches phone plan dependency order. |
| **P1** | **Market US**; manuals + tickets use FRU SKUs and **`RETAIL_FAULT_CODE_PREFIX=FRU-E`**. | Aligns with committed corpus. |
| **P2** | ~~**D2 routing:** `semantic_search` on **resolved** tickets above threshold → else **`llm_wiki_search`**.~~ **Superseded 2026-10-15** by [brain-profiles plan **E2**](./REFACTOR_BRAIN_PROFILES_AND_RETAIL_ANSWER.md#bp-2-decisions): always run both legs; return `retail_answer.v1` JSON (top-2 tickets + manual hits with raw PDF page). | User: always both, deterministic JSON. |
| **P3** | **D12 model scope:** resolve **`model`** (fridge SKU) from open ticket via SQL before search; eval already uses **`model_filter`**. | Prevents cross-SKU reuse mistakes. |
| **P4** | **D9 / D11:** Cursor runs repo scripts + PG A/B; Hermes runs **`llm_wiki_*`** for product manual path. | Copy PDFs ≠ ingest. |
| **P5** | **D13:** migrate **`utils/retail_fru/`** → **`utils/pg_rag/`** during **V5** (domain-agnostic loop). | Samsung plan D13, FRU naming. |

Inherited detail: see [Samsung plan sections 16–20](../completed/REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md#16-deferred-v5) (wording still says “Samsung”; implement for **FRU** paths and copy).

---

<h2 id="3-architecture" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Architecture</h2>

```mermaid
graph TD
  T[Incoming ticket text] --> R{Resolved ticket hit?}
  R -->|yes| A[Reuse resolution from PG]
  R -->|no| W[llm_wiki_search scoped by SKU]
  W --> M[Manual passages + repair steps]
  PG[(Postgres service_queries)] --> S[semantic_search + hybrid modes]
  S --> R
  PDF[fridge-docs PDFs] --> H[Hermes llm_wiki compile]
  H --> Wiki[brain/retail/wiki]

  style T fill:#e3f2fd,stroke:#1976d2,stroke-width:1px,font-size:9px
  style PG fill:#ede7f6,stroke:#5e35b1,stroke-width:1px,font-size:9px
  style Wiki fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,font-size:9px
  style A fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,font-size:9px
  style M fill:#fff3e0,stroke:#e65100,stroke-width:1px,font-size:9px
```

---

<h2 id="4-phases" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phases</h2>

<h3 id="4-v2" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.1 V2 — Wiki automation and derived exports (optional themes)</h3>

- [ ] Theme clustering on FRU ticket text → `brain/retail/raw/sources/db-exports/` → wiki playbooks (no OLTP mirror into Nashsu wiki for raw tickets).
- [ ] Sales summary MD exports (stub or FRU-shaped columns) when sales join is ready.
- [ ] Watermark + `flock` + cron; rescan wiki after export batch.
- [ ] `scripts/retail/export/service_themes.py` (or equivalent) with FRU issue keys from YAML.

**Exit:** one playbook MD compiled into wiki; `./scripts/verify.sh` green.

<h3 id="4-platform" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.2 Platform — brain-profiles (required)</h3>

- [X] Delivered by [`REFACTOR_BRAIN_PROFILES_AND_RETAIL_ANSWER.md`](./REFACTOR_BRAIN_PROFILES_AND_RETAIL_ANSWER.md) P1–P3 (`brain/personal` + `brain/retail`, `BRAIN_PROFILE` default retail); its P4–P8 deliver the answer bundle + E2E tests that **V5** consumes.

**Exit:** dual-domain layout documented; retail paths unchanged under `brain/retail/`.

<h3 id="4-v3" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.3 V3 — Operator harness (Cursor vs Hermes)</h3>

- [X] Split prep into **`CURSOR_PREP_RUNBOOK.md`** + **`HERMES_WIKI_OPERATOR.md`** (FRU PDF paths, **`fru_us_1k`** env block).
- [ ] Hermes smoke: `llm_wiki_set_project` → `brain/retail`; rescan **`fridge-docs`**; one ice-maker search + read (**HG-2**, **manual**, scheduled **after** brain-profiles plan P1–P9 + HG-P2 — see its [section 7](./REFACTOR_BRAIN_PROFILES_AND_RETAIL_ANSWER.md#bp-7-gates)).
- [X] Runbooks cite embed-once protocol and FRU ABC path (`SECOND_BRAIN_RUNBOOK.md` §16).

**Exit:** operator checklist recorded; ticket A/B remains on **`03`/`05`** scripts, not Hermes.

<h3 id="4-v4" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.4 V4 — Eval governance (author vs search coder)</h3>

- [X] New spec **`docs/specs/fru-us-service-synthetic-data.md`**; banner on phone spec.
- [ ] CI or review rule: no combined diff on **`ticket_retrieval.jsonl`** generators + **`hybrid_search`** without explicit override.
- [ ] Held-out eval seed documented for D6-style promotion.

**Exit:** governance checklist in spec; `./scripts/verify.sh` green.

<h3 id="4-v5" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.5 V5 — FRU agent harness (SQL + ticket RAG + wiki ReAct)</h3>

- [ ] **`utils/pg_rag/`** extract from **`utils/retail_fru/`** (embeddings, lexical helpers, SQL guardrails, loop orchestration).
- [ ] FastAPI sidecar: **`semantic_search`**, **`generate_sql`**, **`execute_sql`** (read-only DB role).
- [ ] ReAct loop: customer path (ticket → wiki); manager path (SQL aggregates) per Samsung [section 7](../completed/REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md#7-routing).
- [ ] **D12:** ticket id → SQL → **`model`** → **`model_filter`** on search; wiki queries scoped by SKU folder.
- [ ] Sidecar returns the brain-profiles **`retail_answer.v1`** bundle (`build_answer_bundle`); reuse its `answer_e2e.jsonl` instead of the old `query → ticket_hit | wiki_paths[]` shape; expand **`sql_routed`** stratum tests.
- [ ] Update **`query-retail-brain`** skill + MCP catalog for sidecar URL.

**Exit:** local sidecar demo on FRU corpus; skill routes customer flow end-to-end; verify green.

---

<h2 id="5-quality" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Quality bar</h2>

| Phase | Tests / gates |
|-------|----------------|
| V2 | Export script unit tests; wiki file layout test |
| V3 | Doc smoke only + optional `test_llm_wiki_ctl` ice-maker query (**HG-2**) |
| V4 | Spec lint / CI rule if added |
| V5 | Sidecar contract tests; mock-LLM loop test; SQL guardrail tests |

**Comments:** **cdcm** on new modules; file headers on sidecar and export scripts.

---

<h2 id="6-checklist" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Execution checklist</h2>

- [ ] **V2** — themes / exports / cron
- [X] **Platform** — brain-profiles + answer bundle ([plan](./REFACTOR_BRAIN_PROFILES_AND_RETAIL_ANSWER.md); code P1–P9 done 2026-10-15, HG-P2 / HG-2 pending)
- [X] **V3** — Cursor + Hermes runbooks (wiki smoke HG-2 open)
- [ ] **V4** — eval governance CI / held-out seed
- [ ] **V5** — sidecar + skill + E2E eval JSONL

---

<h2 id="7-acceptance" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Acceptance</h2>

1. **Incoming ticket demo:** paraphrase intake on a known FRU eval row retrieves gold ticket at rank 1 in mode **B** or **C** via sidecar (not CSV harness only).
2. **Manual evidence:** every query's bundle carries manual hits cited to the correct SKU PDF path + page (wiki excerpt or raw-PDF fallback), per brain-profiles **E2/E4**.
3. **Hermes path:** documented rescan + search smoke on fridge PDFs.
4. **`./scripts/verify.sh`** green after **V5** merge.
5. Corpus pivot plan P10–P12 complete (article numbers, runbooks, specs).

---

<h2 id="8-deferred" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. Deferred</h2>

| Item | Notes |
|------|-------|
| Frigidaire SKU + PDFs | Fourth manual folder; extend YAML + customer pool |
| Unified sales + service agent | Join on **`customer_id`** after analytics merge |
| OpenClaw live channels | Same MCP pattern as Hermes when available |
