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
2. Customer troubleshooting (a new ticket) → build the **`retail_answer.v1`** evidence bundle:

   ```bash
   scripts/py scripts/retail/answer/answer_ticket.py --query "<ticket text>" [--model <SKU>] --postgres --json
   ```

   The bundle always holds **both** legs: `tickets.hits` (top-2 resolved tickets, same model, each with
   `cosine_similarity` + `fused_score`) and `manuals.hits` (wiki excerpt **or** raw ``.txt`` search, each with
   `raw_origin.doc_path` and optional `archive_pdf_path`; `pages` is empty until Phase 2). Use `--md` for a
   deterministic human view; `--no-wiki` if LLM Wiki is down (falls back to SKU ``.txt`` search in `diagnostics.notes`).
3. Manager metrics → **`generate_sql`** / **`execute_sql`**; cite counts.
4. No resolution without tool output; escalate if ticket + wiki both fail.

## Summarizing a bundle

- Keep every reference: `ticket_id` with its cosine similarity, and every manual hit as `doc_path`
  (also `wiki_path` when `source = wiki`). Never drop `raw_origin`, even when the wiki text is quoted.
- Do not invent a confidence verdict — the bundle has none by design; report the scores as given.
- Empty `tickets.hits` = no prior ticket for this model; answer from the manual hits alone.

## Domain boundary

Do not search the `brain/personal/` wiki for retail customer flows unless the user explicitly asks for personal corpus.

Phone-era AU corpus remains under `sim_data/profiles/data_*` for regression only.
