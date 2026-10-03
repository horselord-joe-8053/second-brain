<h1 id="execute-gen-general" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Execute bootstrap (general project)</h1>

**Human says (pick one):**

- **`Run bootstrap_general/EXECUTE_GEN.md`** — harness only; **`project_specific/`** must already be valid.
- **`Run bootstrap_general/EXECUTE_GEN.md for the following project: <description>`** — ANALYZE + bootstrap (§0 → §1–§4).
- **`Run bootstrap_general/EXECUTE_GEN.md implementing docs/<plan>.md`** — treat that plan as the brief for §0 ANALYZE (break into specs/plans), then continue.

**Workspace:** repo root (parent of **`bootstrap_general/`**). **`KIT`** = `bootstrap_general/`.

<h3 id="agent-mandate" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">For the coding agent</h3>

Follow this file **in order**. Run kit scripts yourself. **Stop with clear human instructions** for **HG-*** gates (install GUI apps, OAuth, paste keys into external tools). Do not commit secrets.

Phase 1 seeds **`docs/PROJECT-TDD.md`**, **`check-ac-tests.py`**, and general agent skills. Optional **`utils/`** copy when repo root has none.

## Document outline

0. [Analyze project (conditional)](#analyze)
1. [Decide starting phase](#decide)
2. [Phase 1 — harness](#phase1)
3. [Gate](#gate)
4. [Phase 2 — delivery](#phase2)

---

<h2 id="analyze" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">0. Analyze project (conditional)</h2>

**If** the message includes **`for the following project:`**, **`for project:`**, or **`implementing docs/`** with a plan path:

1. Run **`KIT/ANALYZE_PROJECT_SPECIFIC.md`** using that description or plan.
2. **Gate:** proceed only if ANALYZE reports success.
3. On failure or blocked questions, **stop**.

**If** no new description and **`project_specific/`** is empty or missing **`bootstrap.md`**, **stop** — run ANALYZE or use the **“for the following project:”** form.

---

<h2 id="decide" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Decide starting phase</h2>

| Condition | Start at |
|-----------|----------|
| No `./scripts/verify.sh` or harness docs | [§2 Phase 1](#phase1) |
| `./scripts/verify.sh` green and `docs/PROJECT-TDD.md` present | [§3 Gate](#gate) then [§4 Phase 2](#phase2) |

---

<h2 id="phase1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Phase 1 — harness</h2>

Execute **`KIT/project_agnostic/bootstrap_general.md`** **Part A only** (§A1–§A4 STOP).

---

<h2 id="gate" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Gate</h2>

**`./scripts/verify.sh` must pass** before phase 2.

---

<h2 id="phase2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phase 2 — delivery</h2>

1. Read **`KIT/project_specific/bootstrap.md`** and plans under **`KIT/project_specific/plans/`**.
2. Execute **`bootstrap_general.md`** **Part B** (§B1–§B5) in delivery-phase order.
3. Pause on **HG-***; continue only after human confirmation recorded in spec **Decisions**.

Done when §B5 checklist satisfied and **`./scripts/verify.sh`** is green.
