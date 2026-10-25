<h1 id="raw-rag-doc" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Raw-sources RAG benchmark</h1>

Plan: [`REFACTOR_FURTHER_ENHANCEMENT_GPT.md`](../../../../docs_manual_gen/ref_plan/new/REFACTOR_FURTHER_ENHANCEMENT_GPT.md) Phase 1 · vector baseline [`REFACTOR_RETAIL_RAW_SOURCES_RAG_ABCD_COMPARE.md`](../../../../docs_manual_gen/ref_plan/wip/REFACTOR_RETAIL_RAW_SOURCES_RAG_ABCD_COMPARE.md).

**Run profiles (D3 vs D5, config SSOT):** [`RUN_PROFILES.md`](RUN_PROFILES.md).

<h2 id="raw-rag-commands" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Commands</h2>

```bash
# Build indexes (lanes B,C,D) — auto refresh when raw files change
python -m tests.retail_multi_profiles --index-raw --lanes B,C,D

# Smoke / full Lane B — omit --profile → default_run_profile (HG-P1: MANUAL_B_RAW_HYBRID_RERANK)
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
| Index only | `logs/ops/retail-lane-abcd-raw-index-<run_id>.log` | `index_progress.jsonl` |

Set **`NEAT_LOGGER_DEBUG=1`** for top-k paths and embed batch details.

<h2 id="raw-rag-index" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Index location</h2>

Per lane project: `brain/<lane>/.retail-raw-rag/` (Lance + manifest). Requires **`OPENAI_API_KEY`** for live embed (same model as `retail_raw_rag.embedding` in run-config).
