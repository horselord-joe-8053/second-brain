<h1 id="analyze-from-plan" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Analyze from `docs/PLAN_*.md`</h1>

**Trigger:** **`EXECUTE_GEN.md implementing docs/<plan>.md`** and **`specific/bootstrap.md`** missing or stale.

**Inputs:** the plan file, **`docs/second-brain-llm-wiki-architecture.md`**, **`core/harness/docs/templates/`**.

**Output:** **`KIT/specific/bootstrap.md`**, **`specs/*.md`**, **`plans/*.md`**.

## Rules

- **`profile: general`**, **`phase2_modules: desktop-install, second-brain`**
- Map plan **Phase 0…7** → delivery **P1…P8** (one plan file; HG-heavy phases use **`<!-- ac-tests: optional -->`** or mixed AC + HG)
- Seed **`plans/<plan_file>`** with **`<!-- delivery-status: new -->`**, per-phase **Execution checklist** **`[ ]`** bullets per **`docs/templates/implementation-plan.md`**
- **Automated ACs** only for repo-verifiable work (tree, gitignore, harness skills, backup scripts, pytest)
- **HG-*** for LLM Wiki `.dmg`, Hermes install, API token in app, Obsidian vault, Telegram, acceptance tests that need running apps
- Do **not** ask human to confirm test seams; **do** stop on HG with clear steps per **`human-gate.md`**

**Success:** same checklist as **`ANALYZE_SPECIFIC.md`** + `plan_source:` line in bootstrap meta matches the plan path.
