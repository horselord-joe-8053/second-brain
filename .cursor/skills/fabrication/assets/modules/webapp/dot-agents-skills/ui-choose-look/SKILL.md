---
name: ui-choose-look
description: "Factory step UI-CHOOSE: after spec/ticket context, propose 1–3 distinct look-and-feel directions via ui-ux-pro-max, mock them in one artifact (Cursor Canvas or portable HTML), ask the user to pick, record docs/specs/<feature>-ui-decision.md, then hand off to IMPLEMENT. Use for substantial UI creation or layout refactor; skip for trivial CSS tweaks."
disable-model-invocation: true
---

# ui-choose-look (UI-CHOOSE)

Human-in-the-loop **look and feel** gate before editing `frontend/src/**` for **substantial** UI work. Procedure is **harness-portable**; **mock delivery** is harness-specific (see step 4).

## When to run

**Run** when a spec or ticket includes **UI & layout** (or will change layout / visual hierarchy), and the change is **not** a trivial tweak (single property, copy-only, test-selector fix).

**Skip** when:

- Only backend changes, or
- UI change is explicitly marked **UI-CHOOSE: waived** in the ticket/spec with reason, or
- One viable direction is obvious (spec already pins tokens/layout) — proceed with **one** option documented in `-ui-decision.md` as "single direction (waived multi-mock)".

## Inputs

- Approved spec (or ticket) + `docs/specs/ui-factory-convention.md`
- Current `frontend/src/App.tsx`, `frontend/src/styles.css`, optional `design-system/*/MASTER.md`
- **ui-ux-pro-max:** `.agents/skills/ui-ux-pro-max/SKILL.md` and `scripts/search.py`

## Process

### 1. Synthesize context

Summarize (for yourself, brief): product goal, existing layout, spec UI/a11y bullets, constraints (single page, no marketing sections, behavior frozen unless spec says otherwise).

### 2. Propose 1–3 directions (ui-ux-pro-max)

- Run **`.agents/skills/ui-ux-pro-max/scripts/search.py --design-system`** (separate queries per direction). Record output in `-ui-options.md` — installing the skill is **not** enough.
- Use **separate** `--design-system` searches (or style/color/typography domains) so directions differ in **structure or mood**, not only hex tweaks.
- Offer **as many options as are genuinely viable**, **minimum 1, maximum 3**. Do not pad to three.
- For each option record: **id** (A/B/C), **name**, **2–3 sentence rationale**, **STYLE / COLORS / TYPOGRAPHY** (ignore landing PATTERN).

### 3. Write options doc

Create or update:

`docs/specs/<feature-slug>-ui-options.md`

Use `docs/templates/ui-choose-options.md` as shape. Link to the mock artifact from step 4.

### 4. Mocks (one file, all options)

> **Harness note (read every time):**
>
> | Environment | Mock artifact |
> |-------------|----------------|
> | **Cursor IDE** | One **`.canvas.tsx`** beside the chat: follow the built-in **`canvas`** skill (`~/.cursor/skills-cursor/canvas/SKILL.md` or Cursor **Customize → Skills → canvas**). One file with **labeled sections or tabs** for each option; layout and components **as the approved spec describes** (real labels, sample data, primary actions, empty states) — **not** gray wireframe placeholders. |
> | **Not Cursor** | One portable **`docs/mocks/<feature-slug>-ui-options.html`** (self-contained, open in browser). Same **spec-faithful, production-density** requirement. |
> | **Other harness with its own preview tool** | Add a **project skill** mirroring this step (mock contract = one file, 1–3 labeled variants) **before** referencing that tool here; until then use **HTML**. |

Do **not** edit `frontend/src/**` in this step.

### 5. User choice

- **Cursor:** use **AskQuestion** (or equivalent) with one option per direction + **Other / mix** if needed.
- **Any harness:** stop and ask the user to reply with option id (A/B/C) or mix description.

### 6. Record decision

Write `docs/specs/<feature-slug>-ui-decision.md`:

- Chosen option id and name
- Token summary to apply at IMPLEMENT
- Link to mock file used
- Date / spec version reference

Update the feature spec **UI & layout** section to reference the decision file.

### 7. Hand off

IMPLEMENT may start: apply chosen direction to `App.tsx` + `styles.css` per **implement-feature**, **ui-ux-pro-max** checklist, `./scripts/verify.sh`. Behavior unchanged unless spec says so.

## Ticket graph (optional)

`/to-tickets` may add:

- **UI-CHOOSE** — blocked by: spec approved (and any functional prerequisites listed in spec)
- **UI-IMPLEMENT** (or fold into slice) — blocked by: **UI-CHOOSE** complete (`-ui-decision.md` exists)
