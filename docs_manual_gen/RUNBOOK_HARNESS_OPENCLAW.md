<h1 id="openclaw-runbook-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Runbook: OpenClaw harness (skeleton)</h1>

**Hub (shared):** [`SECOND_BRAIN_RUNBOOK.md`](./SECOND_BRAIN_RUNBOOK.md)  
**Adapter:** [`harness/adapters/openclaw/README.md`](../harness/adapters/openclaw/README.md) · `scripts/brain/adapters/openclaw/`  
**Set in stack:** `active_harness: openclaw` (default remains **`hermes`** until channels are wired).

<h2 id="openclaw-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Phases (mirror Hermes)](#openclaw-phases) — same checklist, TBD steps marked.
2. [What works today](#openclaw-today) — catalog load stub.

---

<h2 id="openclaw-phases" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Phases (mirror Hermes)</h2>

| Phase | Hermes equivalent | OpenClaw status |
|-------|-------------------|-----------------|
| Install harness | P3 CLI/Desktop | <span style="background:#fff9c4;padding:2px 4px">TBD</span> upstream install doc |
| Wire MCP | P4 `setup-hermes-mcp.sh` | Shared catalog only — **`merge-openclaw-wiring.py`** stub |
| Contract skills | `external_dirs` | Same **`harness/second-brain/skills/`** |
| Messaging | §16 Telegram/WA | <span style="background:#fff9c4;padding:2px 4px">TBD</span> channel schema |
| Smoke | `acceptance-automated.sh` | Not in CI |

---

<h2 id="openclaw-today" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. What works today</h2>

```bash
# brain-stack.yaml: active_harness: openclaw
./scripts/brain/setup-local.sh          # runs adapters/openclaw/setup-harness.sh
./scripts/brain/adapters/openclaw/merge-openclaw-wiring.py
```

Shared MCP: **`config/second-brain.mcp-servers.yaml`**. Messaging env names match Hermes via **`messaging.sync_env_keys`**.
