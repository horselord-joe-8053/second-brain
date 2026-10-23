<h1 id="a2-analysis-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">TEST_ANALYSIS — A2 Manual RAG (Lane B)</h1>

**Status:** Awaiting operator **§17.2** judged runs after Phase 1 code merge.

| Field | Value |
|-------|--------|
| **profile_id** | `MANUAL\|M\|D2.B\|D3.R-H+RR\|D5.R+V+A\|D6.M90` (update per run) |
| **Prior baseline** | Raw vector `abcd-raw-full-openai-v1` (**28/60** answerable); wiki hybrid B **9/60** (`abcd-full-openai-v2`) |
| **Promotion rule** | **R14** — `hybrid_rrf_rerank` **≥ 30/60** and mean retrieval **&lt; 2 s** |

**Operator commands (after index fresh on Lane B):**

```bash
python -m tests.retail_multi_profiles --smoke --profile MANUAL_B_RAW_HYBRID --lanes B
python -m tests.retail_multi_profiles --full --profile MANUAL_B_RAW_HYBRID --lanes B --run-id a2-hybrid-rrf-b-v1
python -m tests.retail_multi_profiles --full --profile MANUAL_B_RAW_HYBRID_RERANK --lanes B --raw-agentic --run-id a2-hybrid-rerank-b-v1
```

Fill **run_id**, delta table, latency mean/p95, and promotion yes/no after runs complete.
