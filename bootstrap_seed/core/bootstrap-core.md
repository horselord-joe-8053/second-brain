<h1 id="bootstrap-core" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Bootstrap core (phase 1 + phase 2)</h1>

**`CORE`** = `bootstrap_seed/core/`. **`KIT`** = `bootstrap_seed/`. Product artifacts: **`KIT/specific/`**.

Read **`specific/bootstrap.md`** meta (`profile`, `phase1_modules`, `phase2_modules`, `env_append`).

| `profile` | Phase 1 + 2 factory doc |
|-----------|-------------------------|
| **general** | This file (§A1–A5, §B1–B5) |
| **webapp** | **`modules/webapp/bootstrap-webapp.md`** (full factory — execute **instead of** generic §A/B below) |

Per-phase: `<!-- module: … -->` in specs/plans.

## Document outline

**Part A (general profile)** A1 [Mission](#a1) · A2 [Setup](#a2) · A3 [Harness](#a3) · A4 [Modules](#a4) · A5 [STOP](#a5)  
**Part B (general profile)** B1–B5 below

---

<h2 id="a1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">A1. Mission (phase 1)</h2>

Process harness + verify. **`profile: webapp`** → follow **`modules/webapp/bootstrap-webapp.md` Part A** end-to-end.

---

<h2 id="a2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">A2. Setup</h2>

**general:** `bash "$CORE/scripts/install-agent-skills.sh" <repo>`  
**webapp:** `bash "$KIT/modules/webapp/scripts/install-agent-skills.sh" <repo>` (see bootstrap-webapp §A2)

---

<h2 id="a3" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">A3. Harness</h2>

```bash
eval "$(bash "$CORE/scripts/parse-bootstrap-meta.sh" "$KIT/specific/bootstrap.md")"
bash "$CORE/scripts/seed-harness.sh" <repo> "<Name>" "<Desc>" "${BOOTSTRAP_PROFILE:-general}"
bash "$CORE/scripts/seed-scaffold-scripts.sh" <repo> "${BOOTSTRAP_PROFILE:-general}"
```

**webapp:** also §A2 env + kit-utils + agent scaffold per **`bootstrap-webapp.md` §A3–A6**.

---

<h2 id="a4" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">A4. Phase 1 modules</h2>

For each **`phase1_modules`** token: `bash "$CORE/scripts/apply-module.sh" <repo> <token>`.

---

<h2 id="a5" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">A5. STOP</h2>

`./scripts/verify.sh` green → Part B.

---

<h2 id="b1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">B1. Mission (phase 2)</h2>

**webapp:** **`bootstrap-webapp.md` Part B**. **general:** deliver **`specific/`**; **HG-*** + **`modules/*/MODULE.md`**.

---

<h2 id="b2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">B2. Seed product</h2>

`bash "$CORE/scripts/seed-product.sh" <repo>`

---

<h2 id="b3" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">B3–B5. Tickets, implement, done</h2>

**general:** delivery phases + **`implement-feature`** (core) + **`PROJECT-TDD.md`**. Progress ledger: **`docs/plans/<feature>-plan.md`** (**`[ ]`/`[X]`** checklists; **`delivery-resumimpl`** / **`EXECUTE_GEN.md`** delivery-progress).  
**webapp:** §B3–B6 in **`bootstrap-webapp.md`**.

**<project name> / HG-heavy:** pause per **`EXECUTE_GEN.md` agent mandate**; never simulate external installs.
