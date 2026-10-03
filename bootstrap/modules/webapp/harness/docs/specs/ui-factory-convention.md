<h1 id="ui-factory-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">UI factory convention (Web app)</h1>

Short harness rule: **when a feature touches the web UI, polish and accessibility are part of the factory**, not an optional afterthought.

## Document outline

1. [When this applies](#when-applies) — trigger.
2. [Lifecycle hooks](#lifecycle) — SPEC → UI-CHOOSE → TICKET → IMPLEMENT → VERIFY → EVALUATE.
3. [UI-CHOOSE (look and feel)](#ui-choose) — mocks, 1–3 options, decision file.
4. [Design system](#design-system) — MASTER vs ui-ux-pro-max.
5. [Tickets](#tickets) — dedicated slice vs folded into vertical slices.

---

<h2 id="when-applies" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. When this applies</h2>

- Any approved spec that includes **UI & layout** and **Accessibility** sections (`docs/templates/feature-spec.md`).
- Any change under **`frontend/src/**`** even if the spec is silent — agents should still run the IMPLEMENT UI step in `AGENTS.md` and avoid behavior drift.

Backend-only work skips UI polish. Trivial UI tweaks may waive **UI-CHOOSE** (document reason in ticket/spec).

---

<h2 id="lifecycle" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Lifecycle hooks</h2>

| Phase | UI factory action |
|-------|-------------------|
| **SPEC** | Fill UI & a11y sections; behavior ACs stay separate. |
| **UI-CHOOSE** | Substantial UI: run **`ui-choose-look`** (`.agents/skills/ui-choose-look/SKILL.md`) — 1–3 directions, one mock file, user picks, write `-ui-decision.md`. |
| **TICKET** | Optional **UI-CHOOSE** ticket blocked by spec; **UI implement** blocked by decision file. Or fold UI+a11y into each frontend slice. |
| **IMPLEMENT** | Apply chosen look + **ui-ux-pro-max** (or `design-system/*/MASTER.md`); no `frontend/src` layout work before **UI-CHOOSE** when required. |
| **VERIFY** | `./scripts/verify.sh` (required). |
| **EVALUATE** | `/code-review` Spec axis checks UI/a11y + decision doc when present. |

---

<h2 id="ui-choose" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. UI-CHOOSE (look and feel)</h2>

**Skill:** `ui-choose-look` (user-invoked: `/ui-choose-look` when Cursor lists it, or instruct agent to follow the skill path).

**Steps (precise):**

| Step | Agent action |
|------|----------------|
| 1 | Read spec/ticket, current UI, ui-ux-pro-max; summarize constraints. |
| 2 | Run **1–3** ui-ux-pro-max design-system searches; **only viable** distinct directions (not always three). |
| 3 | Write `docs/specs/<feature>-ui-options.md` from `docs/templates/ui-choose-options.md`. |
| 4 | **Mocks — one file:** Fidelity comes from the **feature spec** (sections, flows, density), not from another repo or screenshot. **Cursor:** `.canvas.tsx` via **`canvas`** skill. **Not Cursor:** `docs/mocks/<feature>-ui-options.html`. No wireframe-only placeholders. |
| 5 | User selects A/B/C (or mix); **Cursor** may use AskQuestion. |
| 6 | Write `docs/specs/<feature>-ui-decision.md`; update spec UI section. |
| 7 | **IMPLEMENT** applies tokens/layout to `App.tsx` + `styles.css`; behavior unchanged unless spec says so. |

**Clear-cut case:** one obvious direction → one option in `-ui-options.md`, note **waived multi-mock**, still record `-ui-decision.md`, skip multi-option AskQuestion.

---

<h2 id="design-system" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Design system</h2>

- **Persisted:** `design-system/<project-slug>/MASTER.md` from ui-ux-pro-max `--persist` is the preferred source of colors, type, and checklist across sessions.
- **Ad hoc:** Run ui-ux-pro-max search at implement time when no MASTER exists; optional persist after human approval.
- **Stack:** Plain CSS in `frontend/src/styles.css` is the default; do not add Tailwind/shadcn unless a spec or ADR says so.

---

<h2 id="tickets" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Tickets</h2>

**Option A (default for small features):** Each tracer-bullet that touches the UI includes UI layout + a11y in its “done when”.

**Option B:** Functional tickets land first; **UI-CHOOSE** then **UI polish** tickets (see §3 blocking).

Both options must end with green `verify.sh` and unchanged behavior unless the spec changed it.
