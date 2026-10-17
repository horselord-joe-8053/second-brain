# Brain scripts — operator entry

## Use this first

```bash
./scripts/brain/agent.sh setup      # once per machine / after pull (full bootstrap)
./scripts/brain/agent.sh start      # apply stack + launch active harness
./scripts/brain/agent.sh stop
./scripts/brain/agent.sh restart
./scripts/brain/agent.sh status
./scripts/brain/agent.sh help
```

**Harness selection:** `active_harness` in `config/brain-stack.yaml` (`hermes` | `openclaw`). Default **`hermes`**.

**Start options:**

- `--ensure-setup` — if probe fails, run `adapters/<harness>/setup-harness.sh` only (not full setup-local).
- `--install` — Hermes: install Desktop app if missing (`setup-hermes-desktop.sh`).

**Separate entry (not the agent harness):** LLM Wiki process — `./scripts/brain/llm-wiki.sh start|stop|restart`.

## Warning

Do **not** call delegate scripts directly for daily work (`adapters/hermes/start-hermes.sh`, `setup-hermes.sh`, etc.). Use **`agent.sh`**. Delegates exist for adapter maintenance and are invoked by **`agent.sh`**.

## Call stacks

| Operator command | Script chain |
|------------------|--------------|
| `agent.sh setup` | `setup-local.sh` → `apply-stack-config.sh` → `adapters/HARNESS/setup-harness.sh` → … → `setup-obsidian.sh` |
| `agent.sh start` | `apply-stack-config.sh` → `adapters/HARNESS/start.sh` → (Hermes) `start-hermes.sh` |
| `agent.sh stop` | `adapters/HARNESS/stop.sh` → (Hermes) `stop-hermes.sh` |
| `agent.sh restart` | stop chain → `apply-stack-config.sh` → start chain |

`HARNESS` = `active_harness` from `brain_stack.active_harness()`.

## See also

- `harness/second-brain/README.md` — contract (MCP, compiler)
- `docs_manual_gen/RUNBOOK_HARNESS_HERMES.md` / `RUNBOOK_HARNESS_OPENCLAW.md`
