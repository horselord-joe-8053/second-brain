# Second Brain contract v1

Thin skills and docs for **capture → `brain/raw/sources/` → Nashsu compiles → query via MCP**. **Hermes** and **OpenClaw** are install targets for the same contract — not duplicate compilers or corpora.

- **P3 (HG-3):** `./scripts/brain/setup-local.sh` (or `./scripts/brain/adapters/hermes/setup-hermes.sh`) — idempotent official install + `hermes doctor`. See runbook §10.
- **P4 (HG-4):** `./scripts/brain/adapters/hermes/setup-hermes-mcp.sh` — shared MCP catalog + token sync + `skills.disabled: [llm-wiki]` + `external_dirs` → this folder.
- **Skills here:** `ingest-to-brain/`, `query-brain/`, `nashsu-mcp-read/`; manifest example in `manifests/example-ingest.yaml`.
- **P5 (HG-5):** `./scripts/brain/setup-obsidian.sh` (brew cask; in `setup-local.sh`); vault **`brain/wiki/`**.
- **P7:** `./scripts/brain/backup.sh`.

**MCP (harness-agnostic):** [`config/second-brain.mcp-servers.yaml`](../../config/second-brain.mcp-servers.yaml). **Hermes adapter:** [`harness/adapters/hermes/`](../adapters/hermes/). **OpenClaw adapter (skeleton):** [`harness/adapters/openclaw/`](../adapters/openclaw/).

**Compiler:** Nashsu LLM Wiki only — never run Hermes bundled `llm-wiki` skill as a second compiler. Contract skills use MCP + filesystem paths only (no Hermes-only ingest/query APIs).

**Delivery ledger:** [`seed_grow/plans/second-brain-hermes-v1-plan.md`](../../seed_grow/plans/second-brain-hermes-v1-plan.md) (resume at first `[ ]`).
