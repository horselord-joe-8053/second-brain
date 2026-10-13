<h1 id="sim-data-readme" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">LLM simulated retail corpus (`rrf_data_llm_gen`) v2</h1>

**Profile:** `RETAIL_SIM_DATA_PROFILE=rrf_data_llm_gen` (default in `.env.example`)

| File | Role |
|------|------|
| `service_queries.csv` | 60 historical tickets → Postgres |
| `ticket_manifest.jsonl` | Provenance sidecar |
| `ticket_retrieval.jsonl` | 10 eval intakes + gold ids |
| `prompt_v2.txt` | Author instructions (external LLM or reference) |
| `prompt_v1_archived.txt` | Previous prompt (artificial twin / tech-line rules) |
| `reports/` | A/B/C/D JSON for this profile only |

<h2 id="sim-gen" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Regenerate</h2>

```bash
python3 scripts/retail/seed/generate_llm_corpus_v2.py
python3 scripts/retail/seed/validate_llm_corpus.py
```

Or paste `prompt_v2.txt` into ChatGPT and replace the three data files manually, then validate.

<h2 id="sim-op" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Operator (Postgres A/B/C/D)</h2>

```bash
export RETAIL_SIM_DATA_PROFILE=rrf_data_llm_gen
bash cursor_gen/retail_v11_prep/03_pg_up_and_load.sh   # TRUNCATE → load → embed
bash cursor_gen/retail_v11_prep/05_run_abcd_postgres.sh
```

Embed policy (P3): **`SAM-E###` kept** in vectors; strip only `RETAIL_EMBED_STRIP_PHRASES` (default `Case ref ITM-`). Re-run **03** after changing embed policy or corpus.

<h2 id="sim-v2-rules" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">v2 data rules</h2>

- ~50% historical rows include SAM-E; no duplicate bodies; no twin cloning.
- Eval: natural mix — when gold has SAM-E, ~half of queries mention it.
- Plan: [`REFACTOR_RETAIL_LLM_CORPUS_V2_NATURAL.md`](../../docs_manual_gen/ref_plan/completed/REFACTOR_RETAIL_LLM_CORPUS_V2_NATURAL.md) · hybrid eval stress: [`REFACTOR_RETAIL_LLM_GEN_HYBRID_EVAL_STRESS.md`](../../docs_manual_gen/ref_plan/completed/REFACTOR_RETAIL_LLM_GEN_HYBRID_EVAL_STRESS.md)
