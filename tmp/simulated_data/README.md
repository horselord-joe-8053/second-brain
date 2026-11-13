<h1 id="sim-legacy" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Legacy path (`tmp/simulated_data`)</h1>

**Corpus moved** to [`scripts/retail/sim_data/profiles/`](../scripts/retail/sim_data/README.md):

- **`data_60_10`** — 60 + 10 (teaching ABC mini corpus)
- **`data_1000_100`** — 1000 + 100 (default on scale branch)

This directory may still hold **operator reports** from local ABC runs (`reports/`). Point `RETAIL_SIM_DATA_PROFILE` at a profile id — reports write to that profile’s `reports/` dir.
