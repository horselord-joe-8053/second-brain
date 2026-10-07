# Second Brain harness (Hermes adapters)

Thin skills and docs for the **Second-Brain contract v1**: capture → `brain/raw/sources/` → Nashsu compiles → query via MCP.

- **P3 (HG-3):** `./scripts/brain/setup-local.sh` (or `setup-hermes.sh`) — idempotent official install + `hermes doctor`. Record in spec **Decisions** when clean. See runbook §10.
- **P4 (HG-4):** `./scripts/brain/setup-hermes-mcp.sh` — MCP + token sync + `skills.disabled: [llm-wiki]` + `external_dirs` → this folder.
- **Skills here:** `ingest-to-brain/`, `query-brain/`, `nashsu-mcp-read/`; manifest example in `manifests/example-ingest.yaml`.
- **P5 (HG-5):** `./scripts/brain/setup-obsidian.sh` (brew cask; in `setup-local.sh`); vault **`brain/wiki/`**.
- **P7:** `./scripts/brain/backup.sh`.

**Compiler:** Nashsu LLM Wiki only — never run Hermes bundled `llm-wiki` skill as a second compiler.

**Delivery ledger:** [`seed_grow/plans/second-brain-hermes-v1-plan.md`](../../seed_grow/plans/second-brain-hermes-v1-plan.md) (resume at first `[ ]`).
