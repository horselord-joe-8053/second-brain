# OpenClaw adapter (skeleton)

Install target for the same **Second Brain contract v1** skills under [`harness/second-brain/skills/`](../../second-brain/skills/).

- **Shared MCP catalog:** [`config/second-brain.mcp-servers.yaml`](../../../config/second-brain.mcp-servers.yaml)
- **Architecture:** [`docs_manual_gen/second-brain-llm-wiki-architecture.md`](../../../docs_manual_gen/second-brain-llm-wiki-architecture.md) §8

**Status:** config shape and channel merge are **TBD** upstream. Use [`scripts/brain/adapters/openclaw/merge-openclaw-wiring.py`](../../../scripts/brain/adapters/openclaw/merge-openclaw-wiring.py) stub to validate catalog load only — no live Telegram/WhatsApp in CI.

Set `active_harness: openclaw` in `config/brain-stack.yaml` when this adapter is ready; until then keep **`hermes`**.
