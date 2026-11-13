---
name: align-requirements
description: >-
  Post at most three requirement-alignment questions before implement; record answers in the spec.
  Use when drafting specs, implementing tickets, or the user says "implement tickets".
---

# align-requirements

**Provenance:** Forked from the *intent* of Matt-style **`grilling`** (`.agents/skills/grilling/SKILL.md` from `mattpocock/skills`) — shared understanding before building — but **not** a drop-in replacement for that skill.

| Source skill | Role |
|--------------|------|
| **`grilling` / `grill-me`** (imported) | Multi-round, whole-frontier stress interview for **plans and designs**. |
| **`align-requirements`** (this skill, harness) | **≤3** editable questions per spec/ticket; **requirement alignment** only; then stop for answers. |

## When to run

- New or updated **`docs/specs/*.md`** before **IMPLEMENT**.
- User says **implement tickets** / **implement this spec** and the spec lacks a **`## Decisions`** section (or it is empty).
- **Do not** use this skill for deep plan stress-tests — invoke **`grilling`** or **`grill-with-docs`** instead.

## Steps

1. Read the spec/ticket, `docs/PRODUCT.md`, and open ambiguities (defaults, quotas, UI scope, out-of-scope).
2. Post **at most three** numbered questions. Each must be **answerable in one short paragraph** or a single choice.
3. Add a **recommended default** under each question (agent’s best guess if the user says “use your defaults”).
4. Use **`AskQuestion`** when options are finite; otherwise plain Markdown.
5. **Wait** for answers, or explicit **`skip grill`** / **`skip align`** with a one-line reason.
6. Write answers into the spec under **`## Decisions`** (bullet list: `Q1 → …`). Set **`last_aligned:`** ISO date if missing.
7. Only then proceed to **`implement-feature`** (or UI-CHOOSE when required).

## Rules

- Never exceed **three** questions in one round; if more ambiguity exists, note “deferred” items for a follow-up spec revision.
- Do **not** ask the user to look up facts you can read from the repo (paths, existing APIs, config keys).
- Waiving alignment requires **explicit** user text in chat; record the waiver under **`## Decisions`**.
