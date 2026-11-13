<h1 id="plans-readme" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Delivery plans (`docs/plans/`)</h1>

<h2 id="plans-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Live ledger](#plans-live) — where progress lives.
2. [Optional archive folders](#plans-archive) — wip / completed copies.
3. [How to run](#plans-run) — EXECUTE_GEN and resume.

---

<h2 id="plans-live" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Live ledger</h2>

Each feature has **`seed_grow/plans/<feature>-plan.md`**, linked from the spec via **`<!-- plan: seed_grow/plans/… -->`**. Optional snapshots may live under **`docs/plans/wip/`** or **`docs/plans/completed/`**.

- **`[ ]` / `[X]`** under **Execution checklist** = shared progress bar (human + agent).
- **`<!-- delivery-status: new|wip|completed -->`** at top of the plan file.

Do **not** move the only copy of a plan into subfolders; the spec link must stay valid.

---

<h2 id="plans-archive" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Optional archive folders</h2>

| Folder | Purpose |
|--------|---------|
| **`wip/`** | Optional dated snapshot while work is mid-flight (copy, not move). |
| **`completed/`** | Optional snapshot when **`delivery-status: completed`**. |

---

<h2 id="plans-run" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. How to run</h2>

```text
Run .cursor/skills/fabrication/references/EXECUTE_GEN.md implementing docs_manual_gen/PLAN_….md
delivery-resumimpl seed_grow/plans/<feature>-plan.md
```

See **`.cursor/skills/fabrication/references/EXECUTE_GEN.md`**, **`.cursor/rules/delivery-resumimpl.mdc`**, and **`docs/templates/implementation-plan.md`**.
