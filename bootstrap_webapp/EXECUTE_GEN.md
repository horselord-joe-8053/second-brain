<h1 id="execute-gen-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Execute bootstrap (single entry)</h1>

**Human says (pick one):**

- **`Run bootstrap_webapp/EXECUTE_GEN.md`** — bootstrap only; **`app_specific/`** must already be valid.  
- **`Run bootstrap_webapp/EXECUTE_GEN.md for the following app: <description>`** (or **`for webapp:`**) — analyze + author **`app_specific/`**, then bootstrap (§0 → §1–§4).

**Workspace:** app repo root (parent of **`bootstrap_webapp/`**). **`KIT`** = `bootstrap_webapp/`.

<h3 id="agent-mandate" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">For the coding agent</h3>

Follow this file **in order**. Do **not** open other app repos for specs or code. Run kit scripts yourself. After **`seed-dev-env.sh`**, **prompt the human** to paste their OpenAI (or compatible) key into **`backend/.env`** as **`LLM_API_KEY`** — never commit it.

Phase 1 seeds **TDD enforcement**: **`check-ac-tests.py`**, **`.cursor/rules/tdd-ac-enforcement.mdc`**, and **`docs/WEBAPP-TDD.md`**. It also copies kit **`utils/`** to the project root when `<repo-root>/utils` is absent.

Product specs from ANALYZE must include **`<!-- ac-tests: enforced -->`**, **`<!-- delivery-phase: P1 … -->`**, and **`<!-- plan: docs/plans/<file> -->`**. Each spec has a matching plan under **`app_specific/plans/`** (seeded to **`docs/plans/`**). Implement with **`test_ac_*`** red → green per AC, in delivery-phase order. Delivery phases (`P1`, `P2`, …) are product increments; they are not factory phase 1 / product phase 2.

## Document outline

0. [Analyze app (conditional)](#analyze)
1. [Decide starting phase](#decide)
2. [Phase 1 — factory](#phase1)
3. [Gate](#gate)
4. [Phase 2 — product](#phase2)

---

<h2 id="analyze" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">0. Analyze app (conditional)</h2>

**If and only if** the human message includes **`for the following app:`** or **`for webapp:`** with an app description:

1. Execute **`KIT/ANALYZE_APP_SPECIFIC.md`** using that description (same rules as a standalone ANALYZE run).  
2. **Gate:** proceed to §1 only if ANALYZE reports **success** (§5 checklist in ANALYZE doc).  
3. If ANALYZE fails or is blocked on human answers, **stop**—do **not** run phase 1 or phase 2.

**If** the human did **not** supply a new app description, skip §0. Assume existing **`KIT/app_specific/`** is authoritative; if missing or empty, tell the human to run ANALYZE first or use the **“for the following app:”** form.

---

<h2 id="decide" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Decide starting phase</h2>

Run **`./scripts/verify.sh`** from the workspace root if it exists.

| Condition | Start at |
|-----------|----------|
| No `backend/` + `frontend/` scaffold, or verify fails on phase-1 scope (health + homepage only) | [§2 Phase 1](#phase1) |
| **`./scripts/verify.sh` already green** and phase-1 harness present (`docs/WEBAPP-TDD.md`, **`scripts/check-ac-tests.py`**, **`.cursor/rules/tdd-ac-enforcement.mdc`**, UI factory docs, project-root **`utils/`**) | [§3 Gate](#gate) then [§4 Phase 2](#phase2) |

If unsure, run phase 1 first; do not skip to product features on an empty repo.

---

<h2 id="phase1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Phase 1 — factory</h2>

Read and execute **`KIT/app_agnostic/bootstrap_webapp.md`** **Part A only** (§A2 through §A6 **STOP**). Do **not** run Part B in this step.

---

<h2 id="gate" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Gate</h2>

**`./scripts/verify.sh` must pass** before phase 2. Fix failures and re-run until green.

---

<h2 id="phase2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phase 2 — product</h2>

1. Read **`KIT/app_specific/bootstrap.md`** (mission, tickets, kit meta) and the plans under **`KIT/app_specific/plans/`**.  
2. Read and execute **`KIT/app_agnostic/bootstrap_webapp.md`** **Part B** (§B2 through §B6), using values from **`app_specific/bootstrap.md`**. Implement delivery phases in plan order.

**Part B is not complete** after API/UI behavior alone. You **must** run **§B5 UI-CHOOSE** end-to-end (**`ui-choose-look`**: ui-ux-pro-max searches → **`-ui-options.md`** → production mock → **user choice** → **`-ui-decision.md`**) and then **apply** the chosen layout/tokens in `frontend/src/**`. Ticket order in **`app_specific/bootstrap.md`** is mandatory unless the human explicitly waives UI-CHOOSE in chat (record in `-ui-decision.md`).

Done when §B6 checklist is satisfied **including** UI options/decision (when applicable) **and** **`./scripts/verify.sh`** is green.
