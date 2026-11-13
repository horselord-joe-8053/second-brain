<h1 id="raw-rag-doc" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Raw-sources RAG benchmark</h1>

Main plan: [`REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md`](../../../../docs_manual_gen/ref_plan/new/REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md) Phase 1 · vector baseline minor **M2** [`REFACTOR_RETAIL_RAW_SOURCES_RAG_ABCD_COMPARE.md`](../../../../docs_manual_gen/ref_plan/completed/REFACTOR_RETAIL_RAW_SOURCES_RAG_ABCD_COMPARE.md).

**Run profiles (D3 vs D5, config SSOT):** [`RUN_PROFILES.md`](RUN_PROFILES.md).

<h2 id="raw-rag-commands" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Commands</h2>

```bash
# Lane B manual corpus — Postgres (default after P5 cutover)
bash scripts/retail/ops/pg_up_and_load.sh   # once per dev DB
python -m tests.retail_multi_profiles --ingest-manual-pg --lanes B
# Logs: logs/ops/retail-manual-pg-ingest-<run_id>.log · ops/runs/retail-manual-pg-ingest/<run_id>/ingest_progress.jsonl

# Ingest lanes B,C,D (same Postgres path; one run_id for operator logs)
python -m tests.retail_multi_profiles --ingest-manual-pg --lanes B,C,D --run-id lane-bcd-ingest-v1

# Smoke / full Lane B — omit --profile → default_run_profile (MANUAL_B_RAW_PG_HYBRID_RERANK)
python -m tests.retail_multi_profiles --smoke --retrieval-mode raw_rag
python -m tests.retail_multi_profiles --full --retrieval-mode raw_rag --run-id my-lane-b-run

# Explicit profiles (fair D5 compare, vector baseline, hybrid D5.0)
python -m tests.retail_multi_profiles --full --profile MANUAL_B_RAW_VECTOR --run-id abcd-raw-full-openai-v1
python -m tests.retail_multi_profiles --smoke --profile MANUAL_B_RAW_HYBRID --lanes B
python -m tests.retail_multi_profiles --full --profile MANUAL_B_RAW_HYBRID --run-id a2-hybrid-rrf-b-v2
python -m tests.retail_multi_profiles --full --profile MANUAL_B_RAW_HYBRID_RERANK --run-id a2-hybrid-rerank-b-v2

# Legacy interim v1 (invalid D5 compare — see TEST_ANALYSIS_A2 § Interim):
# python -m tests.retail_multi_profiles --full --profile MANUAL_B_RAW_HYBRID_RERANK --lanes B --raw-agentic

# Compare to wiki baseline
python -m tests.retail_multi_profiles --compare-wiki-raw \
  --raw-results ops/runs/retail-lane-abcd-raw/<run_id>/results.json
```

<h2 id="raw-rag-logs" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Logs</h2>

| Run | Log file | JSONL |
|-----|----------|-------|
| Q&A | `logs/ops/retail-lane-abcd-raw-<run_id>.log` | `ops/runs/retail-lane-abcd-raw/<run_id>/results.jsonl` |
| Manual PG ingest | `logs/ops/retail-manual-pg-ingest-<run_id>.log` | `ingest_progress.jsonl` |

Set **`NEAT_LOGGER_DEBUG=1`** for top-k paths and embed batch details.

<h2 id="raw-rag-index" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Index location</h2>

**All raw_rag lanes (B,C,D):** dense store **`manual_chunks`** in Postgres (`RETAIL_DATABASE_URL`); per-lane freshness metadata `brain/<lane>/.retail-raw-rag/manual_pg_meta.json`. Requires **`OPENAI_API_KEY`** for live embed (same model as `retail_raw_rag.embedding` in run-config). Historical Lance implementation lives on branch **`feature/evo-16-multi-embed-unified-pg`** only.
