# Hermes adapter (internal)

**Operators:** use **`../../agent.sh`** (`start` | `stop` | `restart` | `setup`). Do not run **`start-hermes.sh`** or **`setup-hermes.sh`** directly unless debugging this adapter.

## Delegate entrypoints (called by agent.sh)

| File | Role |
|------|------|
| `start.sh` | → `start-hermes.sh` |
| `stop.sh` | → `stop-hermes.sh` |
| `setup-harness.sh` | → `setup-hermes.sh`, messaging, MCP |

## Setup chain (from setup-harness.sh)

`setup-hermes.sh` → `setup-hermes-messaging.sh` → `setup-hermes-mcp.sh` (when LLM Wiki app-state exists)

Other **`setup-*.sh`** files are steps invoked by the chain above or by **`agent.sh start --install`**.
