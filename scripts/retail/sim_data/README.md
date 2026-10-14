<h1 id="sim-data-root" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Retail simulated data (`sim_data`)</h1>

**Profiles** (committed CSV + eval JSONL): `profiles/data_60_10/`, `profiles/data_1000_100/`.

**Generation** (shared logic): `generation/` — catalog, historical tickets, ABC eval ladder.

```bash
# Regenerate a profile (deterministic seed from profiles.py)
PYTHONPATH=scripts/retail python3 -m sim_data.generation.cli --profile data_1000_100

# Validate
python3 scripts/retail/seed/validate_llm_corpus.py \
  --corpus-dir scripts/retail/sim_data/profiles/data_1000_100
```

**Env:** `RETAIL_SIM_DATA_PROFILE=rrf_data_llm_gen_1k` (default on scale branch) or `rrf_data_llm_gen_60_10`.

Legacy shim: `scripts/retail/seed/generate_llm_corpus_v2.py`.
