<h1 id="execute-unified" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Execute bootstrap (unified)</h1>

**Human says:**

- **`Run bootstrap/EXECUTE_GEN.md`**
- **`Run bootstrap/EXECUTE_GEN.md implementing docs_manual_gen/<plan>.md`** (or **`docs/<plan>.md`** when the brief lives under **`docs/`**)
- **`Run bootstrap/EXECUTE_GEN.md for the following project: …`**
- **`Run bootstrap/EXECUTE_GEN.md profile: webapp for …`**
- **`delivery-resumimpl docs/plans/<feature>-plan.md`** (resume from first **`[ ]`**)

**`KIT`** = `bootstrap/`.

<h3 id="agent-mandate" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">Agent mandate (human interaction)</h3>

Carry out §0–§4 **autonomously**. **Only** stop to prompt the human when:

1. A spec/plan **`HG-*`** or **`desktop-install`** step requires action outside the repo (install app, paste key into `~/.hermes` or LLM Wiki UI, OAuth, Telegram bot).
2. A command needs **secrets** the agent cannot invent.
3. **`AskQuestion`** is required by ANALYZE and the answer blocks ACs.

When stopping: give **numbered steps**, **what to confirm** (e.g. “reply HG-2 done”), and **what you will do next**. Record confirmations in spec **`## Decisions`**. Do **not** ask for approval of test seams, TDD order, or kit mechanics.

<h3 id="delivery-progress" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">Delivery progress (checklists)</h3>

Human-visible progress lives in **`docs/plans/<feature>-plan.md`** (**`[ ]` / `[X]`** under **Execution checklist**), not in the long architecture **`PLAN_*.md`**. Before Part B work (or on any resume), open the spec’s **`<!-- plan: docs/plans/… -->`** file and continue from the **first `[ ]`**. After each phase exit, update checkboxes and **`<!-- delivery-status: new|wip|completed -->`**. Rule: **`.cursor/rules/delivery-resumimpl.mdc`** · template: **`docs/templates/implementation-plan.md`**.

## Document outline

0. [Analyze](#analyze) · 1. [Decide phase](#decide) · 2. [Phase 1](#p1) · 3. [Gate](#gate) · 4. [Phase 2](#p2)

---

<h2 id="analyze" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">0. Analyze</h2>

| Condition | Action |
|-----------|--------|
| **`implementing docs_manual_gen/PLAN_*.md`** (or **`docs/PLAN_*.md`**) and **`specific/`** empty or **`plan_source`** mismatch | **`modules/second-brain/ANALYZE_FROM_PLAN.md`** or **`ANALYZE_SPECIFIC.md`** |
| Web app brief | **`modules/webapp/ANALYZE_WEBAPP.md`**, **`profile: webapp`** |
| Other brief | **`ANALYZE_SPECIFIC.md`** |
| Valid **`specific/bootstrap.md`** already matches the request | Skip analyze |

Also read **`architecture_doc:`** from bootstrap meta when set. Stop analyze on failure.

**Webapp:** **`profile: webapp`** → **`modules/webapp/bootstrap-webapp.md`**.

---

<h2 id="decide" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Decide phase</h2>

No **`./scripts/verify.sh`** or core harness missing → §2. Else if verify green → §4.

---

<h2 id="p1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Phase 1</h2>

**`core/bootstrap-core.md` Part A** with **`BOOTSTRAP_PROFILE`** from **`specific/bootstrap.md`**. Apply **`phase1_modules`**.

---

<h2 id="gate" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Gate</h2>

**`./scripts/verify.sh`** green (may be minimal before specs exist).

---

<h2 id="p2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phase 2</h2>

**`seed-product.sh`** then **`core/bootstrap-core.md` Part B** (or **`bootstrap-webapp.md` Part B**). Implement delivery **P1, P2, …** in order from the linked **`docs/plans/*-plan.md`** checklists. **`apply-module`** for phase tags. Pause only on **HG-*** per mandate above. Maintain plan **`[X]`** ticks via **`implement-feature`** + **`delivery-resumimpl`**.
