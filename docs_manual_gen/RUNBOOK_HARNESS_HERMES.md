<h1 id="hermes-runbook-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Runbook: Hermes harness</h1>

**Hub (shared):** [`SECOND_BRAIN_RUNBOOK.md`](./SECOND_BRAIN_RUNBOOK.md) — corpus, LLM Wiki, MCP catalog, `setup-local.sh`, verify.  
**Scripts (canonical):** `scripts/brain/adapters/hermes/`  
**Set in stack:** `active_harness: hermes` in `config/brain-stack.yaml`.

<h2 id="hermes-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Automated harness setup](#hermes-auto) — `setup-harness.sh` / `setup-local.sh`.
2. [P3 — CLI + Desktop install](#hermes-p3) — doctor, Desktop DMG.
3. [P4 — MCP wiring](#hermes-p4) — catalog merge, skills.
4. [Desktop smoke](#hermes-smoke) — integrated prompts.
5. [Messaging](#hermes-messaging) — Telegram / WhatsApp.

---

<h2 id="hermes-auto" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Automated harness setup</h2>

From repo root (**operator entry:** `scripts/brain/agent.sh`):

```bash
./scripts/brain/agent.sh setup    # full bootstrap (includes setup-local → setup-harness)
# adapter-only repair (internal):
./scripts/brain/adapters/hermes/setup-harness.sh
```

---

<h2 id="hermes-p3" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. P3 — CLI + Desktop install</h2>

```bash
./scripts/brain/agent.sh start --install
./scripts/brain/agent.sh start --provider gemini -m gemini-3.0-flash
```

**P3 exit (HG-3):** `hermes doctor` clean. **Stop Desktop:** `./scripts/brain/agent.sh stop`

**Keys:** `~/.hermes/.env` for chat; sync via `./scripts/brain/apply-stack-config.sh`. See hub runbook §6.

---

<h2 id="hermes-p4" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. P4 — MCP wiring</h2>

```bash
./scripts/brain/adapters/hermes/setup-hermes-mcp.sh
```

Uses shared **`config/second-brain.mcp-servers.yaml`** via **`merge-hermes-wiring.py`**. Skills: **`setup-hermes-skills.sh`**. Templates: **`harness/adapters/hermes/`**.

**Smoke (harness-neutral):** `./scripts/brain/mcp-smoke-read.sh`

---

<h2 id="hermes-smoke" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Desktop smoke</h2>

```bash
./scripts/brain/adapters/hermes/smoke-integrated.sh
RUN_BRAIN_ACCEPTANCE=1 ./scripts/brain/setup-local.sh
# or:
./scripts/brain/adapters/hermes/acceptance-automated.sh
```

Manual Desktop prompts: LLM Wiki on **`brain/`** project; Gateway ready; MCP **`llm_wiki`** + **`second_brain_fs`**. Bring the desktop app up with **`./scripts/brain/llm-wiki.sh start`** (skill **`local-llm-wiki`**). Query skill: **`harness/second-brain/skills/query-brain/SKILL.md`**.

---

<h2 id="hermes-messaging" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Messaging (Telegram / WhatsApp)</h2>

```bash
./scripts/brain/adapters/hermes/setup-hermes-messaging.sh
```

Env keys: **`messaging.sync_env_keys`** in brain-stack. **`platforms:`** shape: **`harness/adapters/hermes/platforms.example.yaml`**. Official: [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) · [WhatsApp](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp).
