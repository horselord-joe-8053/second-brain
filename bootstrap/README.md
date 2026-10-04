<h1 id="bootstrap-unified" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Unified bootstrap kit</h1>

One workflow (ANALYZE → **`specific/`** → EXECUTE → **`docs/specs`**), **DRY core** + **composable modules**.

## Document outline

1. [Layout](#layout) · 2. [Profiles vs modules](#profiles) · 3. [Legacy kits](#legacy) · 4. [Usage](#usage)

---

<h2 id="layout" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Layout</h2>

| Path | Role |
|------|------|
| **`core/`** | Harness, scripts, **`bootstrap-core.md`**, verify templates |
| **`modules/*/`** | **`MODULE.md`** + optional scripts (webapp, logging-neat, desktop-install) |
| **`specific/`** | Product **`bootstrap.md`**, specs, plans |
| **`utils/`** | Shared kit libraries (seeded to repo root when needed) |
| **`EXECUTE_GEN.md`** / **`ANALYZE_SPECIFIC.md`** | Single entrypoints |

---

<h2 id="profiles" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Profiles vs modules</h2>

- **`profile`** — **`general`** (harness only) or **`webapp`** (full factory: **`modules/webapp/bootstrap-webapp.md`**, factory verify/dev, ui-ux-pro-max, UI-CHOOSE).
- **`phaseN_modules`** — optional capabilities applied via **`apply-module.sh`** (utils copy, logging HOWTO, OS-aware desktop gates, UI-CHOOSE).
- Spec/plan **`<!-- module: foo -->`** — attach a capability to one delivery phase without polluting unrelated tickets.

---

<h2 id="legacy" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Self-contained</h2>

**`bootstrap/`** does not read **`bootstrap_webapp/`** or **`bootstrap_general/`** at runtime. Older kits in this repo are optional parallels, not dependencies.

---

<h2 id="usage" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Usage</h2>

```text
Run bootstrap/ANALYZE_SPECIFIC.md implementing docs/PLAN_SECOND_BRAIN_HERMES_V1.md
Run bootstrap/EXECUTE_GEN.md implementing docs/PLAN_SECOND_BRAIN_HERMES_V1.md
delivery-resumimpl docs/plans/<feature>-plan.md
```

Progress: **`docs/plans/<feature>-plan.md`** checklists (**`[ ]`/`[X]`**). See **`docs/plans/README.md`** and **`.cursor/rules/delivery-resumimpl.mdc`**.

Second Brain example meta: **`profile: general`**, **`phase2_modules: desktop-install`**.
