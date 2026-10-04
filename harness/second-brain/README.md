# Second Brain harness (Hermes adapters)

Thin skills and docs for the **Second-Brain contract v1**: capture → `brain/raw/sources/` → Nashsu compiles → query via MCP.

- **P3 (HG-3):** Install Hermes CLI on the Mac host (Topology A). Run `hermes doctor` until clean; record in spec **Decisions**. Commands: [`SECOND_BRAIN_RUNBOOK.md`](../../docs_manual_gen/SECOND_BRAIN_RUNBOOK.md) §10 and [`PLAN_SECOND_BRAIN_HERMES_V1.md`](../../docs_manual_gen/PLAN_SECOND_BRAIN_HERMES_V1.md) §7.
- **P4 (HG-4):** Wire MCP from [`docs/harness/hermes-mcp.example.yaml`](../../docs/harness/hermes-mcp.example.yaml); disable bundled Hermes `llm-wiki` compiler skill; install Nashsu **llm-wiki** agent skill (read/MCP, not compile).
- **P6:** ingest skill + manifest example land here.
- **P6+:** `skills/query-brain/SKILL.md` — MCP search+read patterns; see [`MORE_SECOND_BRAIN_QUERY_HERMES_MCP.md`](../../docs_manual_gen/MORE_SECOND_BRAIN_QUERY_HERMES_MCP.md).

**Compiler:** Nashsu LLM Wiki only — never run Hermes bundled `llm-wiki` skill as a second compiler.

**Delivery ledger:** [`docs/plans/second-brain-hermes-v1-plan.md`](../../docs/plans/second-brain-hermes-v1-plan.md) (resume at first `[ ]`).
