<h1 id="ops-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Retail operator scripts (repeat use)</h1>

**Canonical location** for Postgres + Docker prep used by CI live tier, A/B runs, and local dev.

| Script | Purpose |
|--------|---------|
| [`docker_ensure.sh`](docker_ensure.sh) | Docker CLI + daemon ready |
| [`pg_up_and_load.sh`](pg_up_and_load.sh) | Compose up → schema → load `RETAIL_SIM_DATA_PROFILE` CSV → Gemini embed → lexical rebuild |

**Env:** `RETAIL_DATABASE_URL` and `RETAIL_SIM_DATA_PROFILE` in repo **`.env`** (see `.env.example`). Scripts **do not** invent a default DSN if `.env` is missing the key.

**Legacy:** [`cursor_gen/retail_v11_prep/`](../../../cursor_gen/retail_v11_prep/) keeps thin wrappers and one-off prep docs; new work should call **`scripts/retail/ops/`** directly.

**Live answer E2E:** see [`tests/support/retail/RETAIL_ANSWER_LEGS.md`](../../../tests/support/retail/RETAIL_ANSWER_LEGS.md).
