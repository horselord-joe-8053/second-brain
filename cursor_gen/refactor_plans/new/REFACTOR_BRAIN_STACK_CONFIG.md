<h1 id="refactor-brain-stack" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">REFACTOR: brain-stack config overlay</h1>

**Goal:** Single repo **`config/brain-stack.yaml`** (non-secrets) + **`.env`** (secrets) → apply script syncs Hermes env/MCP paths; LLM Wiki token pull unchanged; Obsidian vault path hint.

<h2 id="phases" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Phases</h2>

### P1 — Stack schema + loader

- [X] `config/brain-stack.example.yaml` + optional `config/brain-stack.yaml` (operator copy; gitignore local overrides)
- [X] `scripts/brain/brain_stack.py` — load, env `${VAR}` expand, paths resolve from repo root
- **Exit:** unit tests green

### P2 — apply-stack-config

- [X] `scripts/brain/apply-stack-config.sh` — upsert `hermes.sync_env_keys` from repo `.env` → `~/.hermes/.env`; export MCP path; call existing merge + `sync-llm-wiki-token.sh`
- [X] `setup-local.sh` invokes apply when stack file present
- **Exit:** `./scripts/verify.sh`

### P3 — Docs

- [X] Runbook §14 — stack file + apply; Hermes UI start pointer
- **Exit:** verify green
