<h1 id="p6010" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Profile `data_60_10`</h1>

**Env:** `RETAIL_SIM_DATA_PROFILE=rrf_data_llm_gen_60_10` (alias: `rrf_data_llm_gen`)

Frozen **60** historical + **10** ABC teaching eval (P4 `abcd_demo_eval_spec` intakes). Regeneration skipped by `sim_data.generation.cli` (`skip_regen`).

Refresh eval only:

```bash
python3 scripts/retail/seed/apply_abcd_demo_eval.py \
  --corpus-dir scripts/retail/sim_data/profiles/data_60_10
```
