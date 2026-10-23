<h1 id="ref-plan-index" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor plans (second_brain / retail)</h1>

**Layout:** same lifecycle as `cursor_gen/refactor_plans/` — **`new/`** (not started), **`wip/`** (partial), **`completed/`** (done).

Retail and Samsung service-brain plans live here instead of scattered under `docs_manual_gen/REFACTOR_*.md` or duplicate `cursor_gen/refactor_plans/` copies.

| Folder | Use |
|--------|-----|
| [`new/`](./new/) | **`onlyref`** — all implementable items **`[ ]`**. |
| [`wip/`](./wip/) | **`implref`** / **`resumimpl`** — some **`[X]`**, not finished. |
| [`completed/`](./completed/) | All implementable phases **`[X]`** (or waived). |

**Execute:** `qimpltdd docs_manual_gen/ref_plan/new/REFACTOR_….md` (or **`wip/`** path when resuming).

| Active plan | Folder | Role |
|-------------|--------|------|
| [`REFACTOR_MULTI_PROFILE_AGENT_OPS.md`](./new/REFACTOR_MULTI_PROFILE_AGENT_OPS.md) | **new** | Hermes compile, delete, and rename on either brain profile without that project on screen |
| [`REFACTOR_RETAIL_MANUAL_INGEST_ABCD_BENCHMARK.md`](./new/REFACTOR_RETAIL_MANUAL_INGEST_ABCD_BENCHMARK.md) | **new** | A/B/C/D retail manual ingest lanes + 90-Q benchmark harness (`eval/retail_manual_qa/`), tiered scoring, industry scan |
| [`REFACTOR_RETAIL_RAW_SOURCES_RAG_ABCD_COMPARE.md`](./wip/REFACTOR_RETAIL_RAW_SOURCES_RAG_ABCD_COMPARE.md) | **wip** | Raw `sources/**` vector-only RAG (lanes B/C/D) vs LLM Wiki baseline; extend `tests/retail_multi_profiles/` |
| [`REFACTOR_FURTHER_ENHANCEMENT_GPT.md`](./new/REFACTOR_FURTHER_ENHANCEMENT_GPT.md) | **new** | A2→A3→A1→B COS; **§7–10** full checklists; **Lane B** primary benchmark; code gated HG-P1… |
| [`REFACTOR_LEARNED_SECTION_COPY_PLUS_CARDS.md`](./new/REFACTOR_LEARNED_SECTION_COPY_PLUS_CARDS.md) | **wip** | Prompt C **v4** shards + `full-copy` + service-manual cards (`nu_llm_wiki`); P6 operator doc done |
| [`REFACTOR_BRAIN_AGENT_ENTRYPOINT.md`](./wip/REFACTOR_BRAIN_AGENT_ENTRYPOINT.md) | **wip** | Single **`scripts/brain/agent.sh`** entry; docs + delegate call stacks |
| [`REFACTOR_FRU_US_SERVICE_BRAIN.md`](./completed/REFACTOR_FRU_US_SERVICE_BRAIN.md) | **completed** | FRU corpus + ABC (1k / Tantivy ladder) |
| [`REFACTOR_FRU_RETAIL_SERVICE_BRAIN.md`](./wip/REFACTOR_FRU_RETAIL_SERVICE_BRAIN.md) | **wip** | Product path: wiki + operator + agent loop (V2–V5) |
| [`REFACTOR_BRAIN_PROFILES_AND_RETAIL_ANSWER.md`](./wip/REFACTOR_BRAIN_PROFILES_AND_RETAIL_ANSWER.md) | **wip** | `brain/personal` + `brain/retail` profiles; `retail_answer.v1` JSON + E2E tests |
| [`REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md`](./completed/REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md) | **completed** | Phone-era master (phases 0–7); reference for V2–V5 |
| [`REFACTOR_RETAIL_SIM_DATA_SCALE_1K.md`](./completed/REFACTOR_RETAIL_SIM_DATA_SCALE_1K.md) | **completed** | Phone 60/10 → 1000/100 archive |

**Articles (not plans):** [`../artifacts/aggregated/REALIGNMENT_DIMENSIONS.md`](../artifacts/aggregated/REALIGNMENT_DIMENSIONS.md) (D1–D6 benchmarks) · [`../artifacts/ABOUT_SEARCH_RRF_FRU.md`](../artifacts/ABOUT_SEARCH_RRF_FRU.md) · [`../artifacts/aggregated/REALIGNMENT_REFACTOR_GOALS.md`](../artifacts/aggregated/REALIGNMENT_REFACTOR_GOALS.md) · [`../artifacts/aggregated/ABOUT_FURTHER_ENHANCEMENT_GPT.md`](../artifacts/aggregated/ABOUT_FURTHER_ENHANCEMENT_GPT.md).

**Legacy pointer:** `cursor_gen/refactor_plans/` may hold stubs; canonical retail plans are under this tree.
