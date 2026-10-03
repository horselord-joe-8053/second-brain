<h1 id="bootstrap-webapp-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Bootstrap prompt: web app (phase 1 + phase 2)</h1>

**Canonical web factory:** `bootstrap/modules/webapp/bootstrap-webapp.md` (wired from **`bootstrap/core/bootstrap-core.md`** when **`profile: webapp`**).

<h3 id="agent-instructions" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">For the coding agent</h3>

1. **Read this file.** **`KIT`** = `bootstrap/`. **`CORE`** = `bootstrap/core/`. **`WEBAPP`** = `bootstrap/modules/webapp/`.
2. **Workspace** = app repo root.
3. **Part A (phase 1):** execute §A2–§A6; use **`$CORE/scripts/`** and **`$WEBAPP/scripts/`**. Pre-approved: `npm install -g ui-ux-pro-max-cli` when needed.
4. **STOP after §A6** until `./scripts/verify.sh` is green. **Part B (phase 2):** read **`specific/bootstrap.md`**, then §B2–§B6.

## Document outline

**Part A — factory (phase 1)**  
A1. [Mission](#a-mission)  
A2. [Agent-run setup](#a-setup)  
A3. [Scaffold](#a-scaffold)  
A4. [UI factory built-in](#a-ui-factory)  
A5. [Homepage](#a-homepage)  
A6. [Done / STOP](#a-done)

**Part B — product features (phase 2)**  
B1. [Mission](#b-mission)  
B2. [Spec and glossary](#b-spec)  
B3. [Tickets](#b-tickets)  
B4. [Implementation](#b-implement)  
B5. [UI polish](#b-ui)  
B6. [Done](#b-done)

---

<h2 id="a-mission" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">A1. Mission (phase 1)</h2>

Git-ready repo: FastAPI `GET /health`, React **homepage placeholder**, **UI factory** harness (UI-CHOOSE machinery only), **`./scripts/verify.sh` green**. **No product features** in phase 1.

---

<h2 id="a-setup" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">A2. Agent-run setup</h2>

| Step | Command |
|------|---------|
| Skills | `bash "$WEBAPP/scripts/install-agent-skills.sh" <repo-root>` |
| Env | `bash "$WEBAPP/seed-dev-env.sh" <repo-root>` — `backend/.env` (includes **LLM_***) + `frontend/.env` |

After env seed: **prompt the human once** to set **`LLM_API_KEY`** in `backend/.env` (OpenAI or compatible). Do not commit real keys. Apps assume server-side AI is available when the key is set.

Requires **Python 3** for ui-ux-pro-max search scripts.

---

<h2 id="a-scaffold" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">A3. Scaffold</h2>

```bash
bash "$CORE/scripts/seed-harness.sh" <repo-root> "<App Name>" "<One-line description>" webapp
bash "$CORE/scripts/seed-scaffold-scripts.sh" <repo-root> webapp
bash "$CORE/scripts/apply-module.sh" <repo-root> kit-utils
```

`seed-harness.sh` (profile **webapp**) applies the **webapp module** → **`docs/WEBAPP-TDD.md`**, ui-factory, **ui-choose-look**, web **implement-feature** skill.  
`seed-scaffold-scripts.sh` (profile **webapp**) copies factory **`verify.sh`**, **`dev.sh`**, and web **`check-ac-tests.py`**.

**Project-root utils** (when absent):

```bash
bash "$CORE/scripts/apply-module.sh" <repo-root> kit-utils
```

Copies **`bootstrap/utils/`** to **`<repo-root>/utils/`** without overwriting an existing tree.

The copied tree includes **`neat_logger/`** (Python), **`neat_logger_ts/`** (TypeScript), and **`playwright_e2e/`**. Read their HOWTO files before product implementation. Templates **`dev.sh`** and **`verify.sh`** put the repo root on **`PYTHONPATH`** so backend code can `from utils.neat_logger import logger`.

Then agent-generated: `backend/`, `frontend/`, CI, `.gitignore`, `README.md`. Default ports **8900** / **5973** (`APP_*_PORT` in `dev.sh`). `.gitignore` must include **`logs/`** (neat_logger file mirror). Frontend `package.json` should depend on the copied packages when product code needs them:

```json
"@floor35/neat-logger-ts": "file:../utils/neat_logger_ts",
"@floor35/playwright-e2e": "file:../utils/playwright_e2e"
```

`@floor35/playwright-e2e` is a dev dependency; add `@playwright/test` beside it when a smoke test is in scope.

Then re-run skills + env seed commands from §A2.

---

<h2 id="a-ui-factory" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">A4. UI factory (built-in)</h2>

Phase 1: seed **`ui-factory-convention.md`**, **`ui-choose-look`**, templates — **no product mocks**.

**Generality:** Process only; no fixed visual target. Product **UI-CHOOSE** runs in phase 2 from the seeded feature spec.

**Homepage waiver:** write **`docs/specs/homepage-ui-decision.md`** (mocks deferred until product spec).

---

<h2 id="a-homepage" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">A5. Homepage</h2>

Backend health + pytest; frontend title placeholder + Vitest smoke test.

---

<h2 id="a-done" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">A6. Done / STOP (phase 1)</h2>

- [ ] `./scripts/verify.sh` passes (runs **`check-ac-tests.py`** first)
- [ ] **`scripts/check-ac-tests.py`** present
- [ ] **`.cursor/rules/tdd-ac-enforcement.mdc`** present
- [ ] ui-ux-pro-max, Matt skills, `ui-choose-look` present
- [ ] `docs/specs/ui-factory-convention.md`, `homepage-ui-decision.md`
- [ ] Project-root **`utils/neat_logger/`**, **`utils/neat_logger_ts/`**, and **`utils/playwright_e2e/`** exist (copied by **`seed-utils.sh`** or already present)

**STOP.** Do not run Part B until verify is green. Then read **`specific/bootstrap.md`** and continue with §B2 below.

---

<h2 id="b-mission" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">B1. Mission (phase 2)</h2>

Build the product described in **`specific/bootstrap.md`** (Mission). Primary ACs live in **`docs/specs/<spec_file>`** (seeded from the kit). **`./scripts/verify.sh` green**.

If `backend/.env` is missing, run **`bash "$WEBAPP/seed-dev-env.sh" <repo-root>`**. Ensure **`LLM_API_KEY`** is set in `backend/.env` when the product uses server-side AI (default kit assumption).

If `<repo-root>/utils` is missing, run **`bash "$CORE/scripts/apply-module.sh" <repo-root> kit-utils`** before implementation.

---

<h2 id="b-spec" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">B2. Spec and glossary</h2>

**Copy product spec from kit (do not invent ACs from memory):**

```bash
bash "$CORE/scripts/seed-product.sh" "$REPO_ROOT"
```

`seed-product.sh` copies **`specific/specs/*.md`** to **`docs/specs/`** and **`specific/plans/*.md`** to **`docs/plans/`**. Each seeded spec’s **`<!-- plan: docs/plans/… -->`** marker must match a file that landed in **`docs/plans/`**.

Then update **`GLOSSARY.md`**, **`docs/PRODUCT.md`**, and **`AGENTS.md`** per **Glossary / AGENTS** in `specific/bootstrap.md`. Link **`docs/WEBAPP-TDD.md`**, the seeded feature spec, and its plan.

**Test seams:** feature spec table + **`docs/WEBAPP-TDD.md`** **as written** — do not ask the human to confirm.

---

<h2 id="b-tickets" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">B3. Tickets</h2>

**`/to-tickets`:** use **Ticket slices** in `specific/bootstrap.md`. Keep the same **`P1` / `P2`** order as **`docs/plans/<plan_file>`**. Include **UI-CHOOSE** (`feature_id`) then **UI implement** blocked by `docs/specs/<feature_id>-ui-decision.md` when UI polish applies. No final layout polish until the UI implement ticket. Do not start a later delivery phase before the earlier phase’s exit in the plan.

---

<h2 id="b-implement" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">B4. Implementation</h2>

**`implement-feature` skill:** for each **`**AC-*:**`** in the seeded spec (with `<!-- ac-tests: enforced -->`), in **delivery-phase order** from the linked plan, **red** (`test_ac_*` failing) → **green** → **`./scripts/verify.sh`**. Finish a phase’s exit (logging, smoke or waiver) before the next phase. Mock external HTTP/LLM at spec seams. No human seam approval. Optional **`/code-review`**.

**Logging (unless impractical for that module):**

- Backend logic: **`utils/neat_logger/`**. `from utils.neat_logger import logger`, then `info` / `step` / `warning` / `error` at transitions. Long or quiet work (HTTP, LLM, batches) uses `with logger.Heartbeat("short label"):`. Default heartbeat interval comes from **`neat_logger_fallback_config.yaml`** (20s).
- Frontend logic: **`utils/neat_logger_ts/`**. `NeatLoggerFactory.frontendMonitor()` from `@floor35/neat-logger-ts`. Quiet async work uses `await log.withHeartbeat("short label", async () => { ... })` (same role as Python `with logger.Heartbeat(...)`). Default interval is **`heartbeat_interval_sec`** (20s). The timer runs on the event loop, so it ticks during `await`, not inside a tight synchronous loop.
- Do not log secrets or full user source text.

**Playwright smoke (where the phase has a user-visible path):** add one smoke under **`frontend/e2e/`** using **`utils/playwright_e2e/`** (`resolvePlaywrightBaseURL` with the app’s frontend port, `getJson` / `postJson` / `pollUntil`, `createProxyMockRouter` when a live LLM would make the test flaky). The smoke must actually run against a local stack. Do not call **`skipUnlessExternalPlaywrightStack`** for it (that helper only skips unless a human pre-started the stack). Run with a timeout and keep going only if it passes, for example:

```bash
cd frontend && npx playwright test e2e --timeout=120000
```

Set the Playwright project test timeout to **60s** unless the plan says otherwise. If a browser smoke is impractical, record a one-sentence waiver in that phase’s **Exit** / **Smoke** lines and do not pretend the command ran.

---

<h2 id="b-ui" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">B5. UI polish (UI-CHOOSE)</h2>

Follow **§A4** and **`.agents/skills/ui-choose-look/SKILL.md`**:

1. **ui-ux-pro-max** `scripts/search.py` per direction → **`docs/specs/<feature_id>-ui-options.md`**
2. One **production-density** mock (Canvas or **`docs/mocks/<feature_id>-ui-options.html`**)
3. **AskQuestion** — A / B / C or mix
4. **`docs/specs/<feature_id>-ui-decision.md`**
5. Implement UI + **`./scripts/verify.sh`**

Use **UI mock notes** in `specific/bootstrap.md` when present.

---

<h2 id="b-done" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">B6. Done (phase 2)</h2>

All ACs met; verify green; README updated (**done_display_name** in bootstrap kit block).

**Do not stop after functional UI.** When the product has a user-visible screen (see ticket slices in `specific/bootstrap.md`), §B5 UI-CHOOSE + token/layout implement are **required** here unless explicitly waived in chat.

- [ ] **`-ui-options.md`**, linked mock, **`-ui-decision.md`**, human choice recorded
- [ ] Chosen direction applied in `frontend/src/**`; verify still green
- [ ] Each seeded spec has a plan in **`docs/plans/`**; ACs were implemented in delivery-phase order
- [ ] Backend paths use **`utils/neat_logger`** (with **`Heartbeat`** on quiet work); frontend paths use **`utils/neat_logger_ts`** (with **`withHeartbeat`** on quiet async work)
- [ ] Each phase with a user-visible path has a Playwright smoke that was run with a timeout, or a waiver written in the plan
