<h1 id="ref-plan-index" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor plans (second_brain / retail)</h1>

**Layout:** same lifecycle as `cursor_gen/refactor_plans/` — **`new/`** (not started), **`wip/`** (partial), **`completed/`** (done).

Retail and Samsung service-brain plans live here instead of scattered under `docs_manual_gen/REFACTOR_*.md` or duplicate `cursor_gen/refactor_plans/` copies.

| Folder | Use |
|--------|-----|
| [`new/`](./new/) | **`onlyref`** — all implementable items **`[ ]`**. |
| [`wip/`](./wip/) | **`implref`** / **`resumimpl`** — some **`[X]`**, not finished. |
| [`completed/`](./completed/) | All implementable phases **`[X]`** (or waived). |

<h2 id="main-vs-minor" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Main vs minor (single umbrella)</h2>

**Naming:** main plans → **`REFACTOR_PLAN_MAIN_<seq>_<slug>.md`** (retail umbrella = **seq 1**). Minors → **`REFACTOR_<topic>.md`** with **`Parent (only):`** pointing at the main file.

| Role | Plan | Path |
|------|------|------|
| **Main (only one)** | [`REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md`](./new/REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md) | `new/` |
| **Minor execution order** | [§0 in main plan](./new/REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md#gpt-hierarchy) | M1 → M8 + cross-cutting **M∥** |

Every **minor** declares **`Parent (only):`** → the main plan. **No dual parents.** Completed minors remain children of the main plan for history.

**Execute Phase 3 (A1 wiki → HG-P3):** `qimpltdd docs_manual_gen/ref_plan/new/REFACTOR_A1_WIKI_HG_P3.md`  
**Execute umbrella / other phases:** `qimpltdd docs_manual_gen/ref_plan/new/REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md`  
**Execute any minor:** `qimpltdd` on that minor’s path (see main §0 table).

<h2 id="active-index" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Active minors (by main-plan sequence)</h2>

| Seq | Plan | Folder | Notes |
|-----|------|--------|--------|
| **M1** | [`REFACTOR_RETAIL_MANUAL_INGEST_ABCD_BENCHMARK.md`](./new/REFACTOR_RETAIL_MANUAL_INGEST_ABCD_BENCHMARK.md) | **new** | TYPE_A_M90 four-lane wiki benchmark |
| **M2** | [`REFACTOR_RETAIL_RAW_SOURCES_RAG_ABCD_COMPARE.md`](./completed/REFACTOR_RETAIL_RAW_SOURCES_RAG_ABCD_COMPARE.md) | **completed** | Raw vector baseline |
| **M3** | [`REFACTOR_UNIFIED_PG_MANUAL_EMBEDDINGS.md`](./completed/REFACTOR_UNIFIED_PG_MANUAL_EMBEDDINGS.md) | **completed** | PG manual cutover |
| **M4** | [`REFACTOR_BUNDLED_MANUAL_TICKET_QA.md`](./new/REFACTOR_BUNDLED_MANUAL_TICKET_QA.md) | **new** | B0 bundled 5+2 concat + TYPE_B_B20 |
| **M11** | [`REFACTOR_A1_WIKI_HG_P3.md`](./new/REFACTOR_A1_WIKI_HG_P3.md) | **new** | **Active:** P3.2–P3.6 one-shot qimpltdd |
| **M5** | [`REFACTOR_LEARNED_SECTION_COPY_PLUS_CARDS.md`](./new/REFACTOR_LEARNED_SECTION_COPY_PLUS_CARDS.md) | **new** | Lane D `nu_llm_wiki` (parallel) |
| **M6** | [`REFACTOR_BRAIN_PROFILES_AND_RETAIL_ANSWER.md`](./wip/REFACTOR_BRAIN_PROFILES_AND_RETAIL_ANSWER.md) | **wip** | `retail_answer.v1` |
| **M7** | [`REFACTOR_FRU_RETAIL_SERVICE_BRAIN.md`](./wip/REFACTOR_FRU_RETAIL_SERVICE_BRAIN.md) | **wip** | Product V2–V5 after M6 |
| **M8** | [`REFACTOR_BRAIN_AGENT_ENTRYPOINT.md`](./wip/REFACTOR_BRAIN_AGENT_ENTRYPOINT.md) | **wip** | `scripts/brain/agent.sh` |
| **M∥** | [`REFACTOR_MULTI_PROFILE_AGENT_OPS.md`](./new/REFACTOR_MULTI_PROFILE_AGENT_OPS.md) | **new** | Hermes multi-profile compile |

**Articles (not plans):** [`../artifacts/aggregated/REALIGNMENT_DIMENSIONS.md`](../artifacts/aggregated/REALIGNMENT_DIMENSIONS.md) (D1–D6 benchmarks) · [`../artifacts/ABOUT_SEARCH_RRF_FRU.md`](../artifacts/ABOUT_SEARCH_RRF_FRU.md) · [`../artifacts/aggregated/REALIGNMENT_REFACTOR_GOALS.md`](../artifacts/aggregated/REALIGNMENT_REFACTOR_GOALS.md) · [`../artifacts/aggregated/ABOUT_FURTHER_ENHANCEMENT_GPT.md`](../artifacts/aggregated/ABOUT_FURTHER_ENHANCEMENT_GPT.md).

**Legacy pointer:** `cursor_gen/refactor_plans/` may hold stubs; canonical retail plans are under this tree.
