<h1 id="p1000" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Profile `data_1000_100`</h1>

**Env:** `RETAIL_SIM_DATA_PROFILE=rrf_data_llm_gen_1k` (**default** on scale branch)

**1000** historical + **100** ABC teaching eval (50 paraphrase / 30 hybrid_stress / 20 code_in_query).

Regenerate:

```bash
PYTHONPATH=scripts/retail python3 -m sim_data.generation.cli --profile data_1000_100
python3 scripts/retail/seed/validate_llm_corpus.py --corpus-dir scripts/retail/sim_data/profiles/data_1000_100
```
