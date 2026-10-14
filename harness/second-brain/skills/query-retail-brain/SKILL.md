---
name: query-retail-brain
description: Query Fridges R Us US retail brain (RETAIL_MARKET=US) — ticket hybrid search + LLM Wiki fridge manuals at brain/retail.
---

# query-retail-brain

## Preconditions

1. **`local-llm-wiki`** `status`, then `start` if down. **`llm_wiki_set_project`** → absolute path `…/second_brain/brain/retail`.
2. Retail sidecar or Postgres tools configured (`RETAIL_SIDECAR_URL` / `retail_pg` MCP for dev).
3. Default corpus: **`RETAIL_SIM_DATA_PROFILE=fru_us_1k`**, **`RETAIL_MARKET=US`**, **`RETAIL_FAULT_CODE_PREFIX=FRU-E`**.

## Routing

1. `item_number` / `ticket_id` → SQL (read-only) → fridge **SKU** (`RF28K9070SG`, `GNE27JYMFS`, `KRFF507HPS`).
2. Customer troubleshooting → **`semantic_search`** on **resolved** tickets (hybrid modes in production), then **`llm_wiki_search`** on retail wiki under the matching **`fridge-docs/<brand>_<model>/`** compile tree.
3. Manager metrics → **`generate_sql`** / **`execute_sql`**; cite counts.
4. No resolution without tool output; escalate if ticket + wiki both fail.

## Domain boundary

Do not search legacy `brain/` wiki for retail customer flows unless the user explicitly asks for personal corpus.

Phone-era AU corpus remains under `sim_data/profiles/data_*` for regression only.
