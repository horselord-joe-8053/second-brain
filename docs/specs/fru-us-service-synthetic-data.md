<h1 id="spec-fru-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Spec: FRU US aftersales synthetic data and eval</h1>

**Status:** active (default corpus **`fru_us_1k`**)  
**Plan:** [`REFACTOR_FRU_US_SERVICE_BRAIN.md`](../docs_manual_gen/ref_plan/completed/REFACTOR_FRU_US_SERVICE_BRAIN.md) · **Product:** [`REFACTOR_FRU_RETAIL_SERVICE_BRAIN.md`](../docs_manual_gen/ref_plan/new/REFACTOR_FRU_RETAIL_SERVICE_BRAIN.md) · **Phone archive spec:** [`samsung-retail-synthetic-data.md`](./samsung-retail-synthetic-data.md)

<h2 id="spec-fru-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Scope](#1-scope) — SKUs, market, customers.
2. [Schema](#2-schema) — CSV columns.
3. [Manifest and eval](#3-manifest) — JSONL contracts.
4. [ABC ladder](#4-abc) — promotion gate.
5. [Config](#5-config) — env and YAML.

---

<h2 id="1-scope" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Scope</h2>

- **Models:** `RF28K9070SG`, `GNE27JYMFS`, `KRFF507HPS` (US fridge SKUs).
- **Market:** `RETAIL_MARKET=US` (default for prep scripts after FRU pivot).
- **Customers:** 150-row committed seed (`sim_data/seed/fru_customers.jsonl`); **`customer_id`** on CSV rows only — never in query text.
- **Fault codes:** `FRU-E###` via `RETAIL_FAULT_CODE_PREFIX` and `config/fru_us_service.yaml`.
- **Profile:** `fru_us_1000_100` directory; env id **`fru_us_1k`**.

---

<h2 id="2-schema" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Schema</h2>

`service_queries.csv` columns include **`customer_id`**, ticket fields, timestamps, **`customer_query_text`**, **`resolution_text`**. Postgres migration: `schema/004_customer_id.sql`.

Sidecar **`ticket_manifest.jsonl`** stores **`issue_key`** and **`fault_code`** for eval-only regen (no ticket-id arithmetic).

---

<h2 id="3-manifest" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Manifest and eval</h2>

- **Historical:** 1000 rows, natural generation (frozen seed).
- **Eval:** 100 rows — **50** paraphrase / **30** hybrid_stress / **20** code_in_query.
- **Gold:** `expected_ticket_ids[0] == source_ticket_id`; gold status **resolved**; queries must not verbatim-match gold body.
- **Validator:** `scripts/retail/seed/validate_llm_corpus.py --corpus-dir …/fru_us_1000_100`.

---

<h2 id="4-abc" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. ABC ladder</h2>

Operator reports under `profiles/fru_us_1000_100/reports/` must pass **`scripts/retail/eval/check_abc_ladder.py`**: overall recall@1 **A &lt; B &lt; C**; hybrid_stress **B &gt; A**; code_in_query **C &gt; B**; `lexical_backend=tantivy`, `total=100`.

---

<h2 id="5-config" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Config</h2>

```bash
export RETAIL_SIM_DATA_PROFILE=fru_us_1k
export RETAIL_MARKET=US
export RETAIL_FAULT_CODE_PREFIX=FRU-E
export RETAIL_LEXICAL_BACKEND=tantivy
```

Company profile: `scripts/retail/config/fru_us_service.yaml`.
