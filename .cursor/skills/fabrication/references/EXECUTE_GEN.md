<h1 id="execute-unified" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Execute bootstrap (unified)</h1>

**Human says:**

- **`Run .cursor/skills/fabrication/references/EXECUTE_GEN.md`**
- **`Run .cursor/skills/fabrication/references/EXECUTE_GEN.md implementing <project general description file path>`**
- **`Run .cursor/skills/fabrication/references/EXECUTE_GEN.md for the following project: …`**
- **`Run .cursor/skills/fabrication/references/EXECUTE_GEN.md profile: webapp for …`**
- **`delivery-resumimpl seed_grow/plans/<feature>-plan.md`** (resume from first **`[ ]`**)

**`KIT`** = `.cursor/skills/fabrication/`. A run **must not** create or edit any file under **`.cursor/skills/fabrication/`** (read-only kit). Project writes go to **`seed_grow/`** (zone 2) and product tree (zone 3).

<h3 id="agent-mandate" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">Agent mandate (human interaction)</h3>

Carry out §0–§4 **autonomously**. **Only** stop to prompt the human when:

1. A spec/plan **`HG-*`** or **`desktop-install`** step requires action outside the repo (install app, paste key into **`<tool config dir>`** or app UI, OAuth, messaging bot).
2. A command needs **secrets** the agent cannot invent.
3. **`AskQuestion`** is required by ANALYZE and the answer blocks ACs.

When stopping: give **numbered steps**, **what to confirm**, and **what you will do next**. Record confirmations in spec **`## Decisions`**.

<h3 id="delivery-progress" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">Delivery progress (checklists)</h3>

Human-visible progress lives in **`seed_grow/plans/<feature>-plan.md`** (**`[ ]` / `[X]`** under **Execution checklist**). Rule: **`.cursor/rules/delivery-resumimpl.mdc`** · template: **`docs/templates/implementation-plan.md`**.

## Document outline

0. [Analyze](#analyze) · 1. [Decide phase](#decide) · 2. [Phase 1](#p1) · 3. [Gate](#gate) · 4. [Phase 2](#p2)

---

<h2 id="analyze" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">0. Analyze</h2>

| Condition | Action |
|-----------|--------|
| **`implementing <project general description file path>`** and **`seed_grow/`** empty or **`plan_source`** mismatch | **`ANALYZE_SPECIFIC.md`** only |
| Web app brief | **`modules/webapp/ANALYZE_WEBAPP.md`**, **`profile: webapp`** |
| Other brief | **`ANALYZE_SPECIFIC.md`** |
| Valid **`seed_grow/bootstrap.md`** already matches the request | Skip analyze |

Also read **`architecture_doc:`** from bootstrap meta when set.

**Webapp:** **`profile: webapp`** → **`modules/webapp/bootstrap-webapp.md`**.

---

<h2 id="decide" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Decide phase</h2>

No **`./scripts/verify.sh`** or core harness missing → §2. Else if verify green → §4.

---

<h2 id="p1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Phase 1</h2>

**`core/bootstrap-core.md` Part A** with **`BOOTSTRAP_PROFILE`** from **`seed_grow/bootstrap.md`**. Apply **`phase1_modules`**.

---

<h2 id="gate" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Gate</h2>

**`./scripts/verify.sh`** green (may be minimal before specs exist). Then record the gate: **`bash .cursor/skills/fabrication/scripts/append-checkpoint.sh <repo-root> verify-gate done gate`** (or the same path under **`.cursor/skills/fabrication/scripts/`** after the kit move).

---

<h2 id="p2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phase 2</h2>

**`seed-product.sh`** then **`core/bootstrap-core.md` Part B** (or **`bootstrap-webapp.md` Part B**). Implement delivery **P1, P2, …** from **`seed_grow/plans/*-plan.md`**. **`apply-module`** for phase tags. Pause only on **HG-*** per mandate above.
