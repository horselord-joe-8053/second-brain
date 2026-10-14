---
name: query-retail-brain
description: Query Samsung Australia retail brain (RETAIL_MARKET=AU) — FRU sidecar tickets + LLM Wiki manuals at brain/retail.
---

# query-retail-brain

## Preconditions

1. **`local-llm-wiki`** `status`, then `start` if down. **`llm_wiki_set_project`** → absolute path `…/second_brain/brain/retail`.
2. Retail FRU sidecar or Postgres tools configured (`RETAIL_SIDECAR_URL` / `retail_pg` MCP for dev).

## Routing

1. `item_number` / `ticket_id` → SQL (read-only).
2. Customer troubleshooting → sidecar **`semantic_search`** on **resolved** tickets, then **`llm_wiki_search`** on retail wiki (manuals only).
3. Manager metrics → **`generate_sql`** / **`execute_sql`**; cite counts.
4. No resolution without tool output; escalate if ticket + wiki both fail.

## Domain boundary

Do not search legacy `brain/` wiki for retail customer flows unless the user explicitly asks for personal corpus.
