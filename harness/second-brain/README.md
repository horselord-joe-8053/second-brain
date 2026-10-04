# Second Brain harness (Hermes adapters)

Thin skills and docs for the **Second-Brain contract v1**: capture → `brain/raw/sources/` → Nashsu compiles → query via MCP.

- **P3 (HG-3):** `./scripts/brain/setup-local.sh` (or `setup-hermes.sh`) — idempotent official install + `hermes doctor`. Record in spec **Decisions** when clean. See runbook §10.
- **P4 (HG-4):** Wire MCP from [`docs/harness/hermes-mcp.example.yaml`](../../docs/harness/hermes-mcp.example.yaml); disable bundled Hermes `llm-wiki` compiler skill; install Nashsu **llm-wiki** agent skill (read/MCP, not compile).
- **P6:** ingest skill + manifest example land here.
- **P6+:** `skills/query-brain/SKILL.md` — MCP search+read patterns; see [`MORE_SECOND_BRAIN_QUERY_HERMES_MCP.md`](../../docs_manual_gen/MORE_SECOND_BRAIN_QUERY_HERMES_MCP.md).

**Compiler:** Nashsu LLM Wiki only — never run Hermes bundled `llm-wiki` skill as a second compiler.

**Delivery ledger:** [`docs/plans/second-brain-hermes-v1-plan.md`](../../docs/plans/second-brain-hermes-v1-plan.md) (resume at first `[ ]`).
