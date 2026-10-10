<h1 id="spec-samsung-retail-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Spec: Samsung Australia retail synthetic data and eval</h1>

**Status:** draft for implementation  
**Plan:** [`docs_manual_gen/REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md`](../docs_manual_gen/REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md)

<h2 id="spec-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Scope](#1-scope) — models and LGPD.
2. [Schema](#2-schema) — CSV columns and enums.
3. [Manifest and eval](#3-manifest) — JSONL contracts.
4. [Holdout and strata](#4-holdout) — A/B validity.
5. [Embedding and threshold](#5-embedding) — frozen baselines.

---

<h2 id="1-scope" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Scope</h2>

- **Models:** Galaxy A15 5G, A16 5G, A25 5G only.
- **Geography:** Australia nationwide (city + state on rows; default **NSW/VIC/QLD** rotation).
- **Market knob:** `RETAIL_MARKET=AU` (default) or `BR` — one env var drives seed copy, eval paraphrases, and Postgres full-text config via `retail_brain/market.py` (`en-AU` → `english` FTS; `pt-BR` → `portuguese` FTS).
- **Privacy:** Synthetic names, phones, and addresses only; no real customer PII.
- **Volume target:** ~100k service rows in full corpus; tests use **small fixed seed** (e.g. 500 rows) for CI.

---

<h2 id="2-schema" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Schema</h2>

**Service queries (`service_queries.csv`):**

```text
ticket_id, item_number, store_id, city, state, model,
status, customer_query_text, resolution_text,
opened_at, updated_at, closed_at
```

**`status` enum:** `received` | `resolving` | `resolved` | `resolution_rejected`

**Sales (`retail_sales.csv`):** `store_id`, `city`, `state`, `model`, `units`, `revenue`, `sale_date`

---

<h2 id="3-manifest" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Manifest and eval</h2>

**`ticket_manifest.jsonl`** — one JSON object per ticket: `ticket_id`, `model`, `status`, `seed`, `customer_query_text` (for provenance only; not copied into eval queries).

**`ticket_retrieval.jsonl`** — eval gold:

```text
eval_id, query, model_filter, expected_ticket_ids, stratum, source_ticket_id
  [, acceptable_ticket_ids] [, gold_rationale]   # optional — offline LLM author only
```

- **`expected_ticket_ids`:** **Strict D6 gold** — default generator sets **`[source_ticket_id]`** only. Each ticket has **unique** `customer_query_text` (case ref in seed) so recall@1 is discriminative.
- **`acceptable_ticket_ids`:** Optional secondary set from **offline** `seed/llm_author_gold.py` (not runtime). Harness reports `acceptable_recall_at_1` when present; **D6 promotion uses strict `recall_at_1` only**.
- **Pipeline:** `generate_tickets` → `generate_eval_from_manifest` → (optional) `llm_author_gold.py` → commit JSONL → A/B harness. Re-run full chain when `SEED`/`COUNT` changes.
- **`stratum`:** `paraphrase` | `literal_token` | `sql_routed`
- **Anti-leakage:** `query` must not equal manifest `customer_query_text` for `source_ticket_id`. Paraphrase **strips** the seed’s `Case ref ITM-… / T-…` suffix so the exam question does not copy the unique cabinet key (stored tickets still include it).

**Gold authorship (D8):** The **data author** sets `query`, `expected_ticket_ids`, and `stratum` from manifest provenance (generators or human holdout). The **implementor** only runs the harness that compares ranker output to that preset gold — never copies top‑k ids back into JSONL. See refactor plan [§8.2](../docs_manual_gen/REFACTOR_SAMSUNG_RETAIL_SERVICE_BRAIN.md#8-2-gold-roles).

---

<h2 id="4-holdout" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Holdout and strata</h2>

- Eval ids are **disjoint** from any set used to tune similarity threshold `T_high`.
- Minimum CI fixture: **≥20** eval rows across **≥2** strata; full corpus target **hundreds+** at operator regen.
- **`sql_routed`:** excluded from semantic A/B aggregates (labeled separately).

---

<h2 id="5-embedding" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Embedding and threshold</h2>

- **Operator A/B (D10):** repo `.env` `GEMINI_API_KEY` + `EMBEDDING_MODEL` (e.g. `gemini-embedding-2`); `utils/retail_fru/embeddings.py` — **no mock fallback**. Embed each ticket **once** in PG (`vector(768)`); caveats: [war story 2](../../war_stories/WAR_STORIES.md#war-story-2).
- **Tests:** pytest stubs `embed_text` only; production always calls Gemini or fails fast.
- **`RETAIL_TICKET_HYBRID_SEARCH`:** `0` = vector-only (V1); `1` = tsvector + RRF (V1.1).
- Promotion to default `1` only per plan D6 after A/B on that frozen cabinet.
- **Until Samsung V4:** one agent may author gold and implement search; do not set `expected_ticket_ids` from neighbor lists.

<h2 id="decisions" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Decisions</h2>

**last_aligned:** 2026-10-10

- **Q1 → Market parameter:** `RETAIL_MARKET` with profiles **AU** (default, en-AU copy, Postgres `english`) and **BR** (pt-BR copy, Postgres `portuguese`); invalid values fail fast.
- **Q2 → Default corpus:** Regenerate committed fixtures and operator shakedown data as **AU / English**; Brazil remains available by flipping env for future runs.
- **Q3 → Product domain:** Still Samsung Galaxy A15/A16/A25 service retail; geography and language follow `RETAIL_MARKET`, not a separate product rename.
- **Q4 → Eval gold:** Strict single-id CI gold; unique per-ticket seed text; optional offline LLM `acceptable_ticket_ids` before promotion-scale A/B (V2/V4 governance).
