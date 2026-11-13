# Retail domain — Fridges R Us (US) service brain

Brain-profile **`retail`** (default `BRAIN_PROFILE`). Answers new FRU aftersales tickets from two kinds of evidence:

1. **Historical tickets** — synthetic **United States** aftersales tickets for three fridge SKUs in Postgres (default corpus **`RETAIL_SIM_DATA_PROFILE=fru_us_1k`**, market **`RETAIL_MARKET=US`**, fault codes `FRU-E###`).
2. **Manuals** — user and repair guides under `brain/retail/raw/sources/fridge-docs/`, compiled into `wiki/` by LLM Wiki.

Every answer is one **`retail_answer.v1`** JSON bundle: the top-2 similar resolved tickets (with similarity scores) **and** manual evidence, each manual hit cited to its raw PDF path and page. Callers may render or summarize the bundle but must keep those citations.

Phone-era Samsung AU corpora remain under `scripts/retail/sim_data/profiles/data_*` for archive and regression.
