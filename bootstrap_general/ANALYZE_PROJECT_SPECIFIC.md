<h1 id="analyze-project-specific" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Analyze project and author `project_specific/`</h1>

**Human says:** run **`bootstrap_general/ANALYZE_PROJECT_SPECIFIC.md`** **for the following project:** *&lt;description&gt;*  
Or: **implementing `docs/PLAN_….md`** — treat that file as the primary brief.

**Workspace:** repo root. **`KIT`** = `bootstrap_general/`.

<h3 id="agent-mandate" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">For the coding agent</h3>

Produce **`KIT/project_specific/bootstrap.md`**, **`specs/<spec_file>`**, and **`plans/<plan_file>`** for **`EXECUTE_GEN.md`**. **Author kit files only** unless the human asks to implement.

**Stack:** not assumed to be React/FastAPI. Declare tools, verify commands, and **HG-*** human gates in specs (Hermes, desktop apps, OAuth, etc.).

Use **AskQuestion** for material ambiguity. **One batch** of questions when possible.

## Document outline

1. [Inputs](#inputs)
2. [Research](#research)
3. [Clarifications](#clarify)
4. [Author artifacts](#author)
5. [Validation](#validate)

---

<h2 id="inputs" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Inputs</h2>

| Source | Why |
|--------|-----|
| Human brief or **`docs/PLAN_*.md`** | Primary intent |
| **`KIT/project_agnostic/bootstrap_general.md`** Part B | Phase 2 expectations |
| **`docs/templates/feature-spec.md`**, **`implementation-plan.md`** | Spec/plan shape |
| **`docs/PROJECT-TDD.md`** (after phase 1) or kit copy | Verification policy |
| Existing **`docs/*architecture*.md`** | Durable design (e.g. Second Brain) |

---

<h2 id="research" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Research</h2>

Fill gaps (install paths, CLI commands, human vs automatable steps). Prefer **testable ACs** and explicit **HG-*** for external tools.

---

<h2 id="clarify" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Clarifications</h2>

Ask when auth, hosting, or MVP scope would materially change ACs. If unanswered, **stop**.

---

<h2 id="author" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Author artifacts</h2>

Under **`KIT/project_specific/`** only:

**`bootstrap.md`** — kit meta:

```text
feature_id: <kebab-id>-v1
spec_file: <name>.md
plan_file: <name>-plan.md
env_append: none
done_display_name: <Human name>
```

- **Mission**, **Ticket slices** (aligned with P1/P2…), **Glossary / AGENTS**
- No UI-CHOOSE tickets unless the brief includes a substantial **web** UI (then consider `bootstrap_webapp` instead)

**`specs/<spec_file>`** — use general feature template; **`ac-tests: enforced`** or **`optional`**; **HG-*** for human steps; link **`<!-- plan: docs/plans/... -->`**

**`plans/<plan_file>`** — phases with **Exit** verify commands or waivers

`mkdir -p KIT/project_specific/specs KIT/project_specific/plans`

---

<h2 id="validate" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Validation</h2>

- [ ] `bootstrap.md` meta parses
- [ ] Spec + plan exist and cross-link
- [ ] Human gates named for non-automatable steps
- [ ] `bash KIT/project_agnostic/scripts/seed-product.sh <repo-root>` succeeds (after phase 1 harness exists)

**Success:** list files written; human may run **`bootstrap_general/EXECUTE_GEN.md`**.
