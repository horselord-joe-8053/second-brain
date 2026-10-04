<h1 id="mod-second-brain" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Module: second-brain</h1>

**When:** Hermes + Nashsu LLM Wiki + `brain/` corpus (`profile: general`, plan **`docs/PLAN_SECOND_BRAIN_HERMES_V1.md`**).

**Agent:** Implement **in-repo** work (tree, docs, `harness/`, scripts). **Never** commit secrets. **Stop** on **HG-*** with **`human-gate.md`**-style instructions; continue only after human confirms (record in **## Decisions**). Tick **`docs/plans/*-plan.md`** **Execution checklist** after each exit (**`delivery-resumimpl`**).

**Apply:** `bash bootstrap/core/scripts/apply-module.sh <repo> second-brain` — installs **`scripts/verify-local.sh`** template if missing.

**Analyze:** If **`specific/`** is empty but human said **`implementing docs/PLAN_…`**, run **`ANALYZE_FROM_PLAN.md`** first.
