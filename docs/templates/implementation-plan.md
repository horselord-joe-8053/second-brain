# Plan: [Feature]

<!-- delivery-status: new -->
<!-- plan-for: docs/specs/[feature].md -->

**Delivery phases** (`P1`, `P2`, …) are ordered increments. One plan per spec. Implement in order.

**Progress:** Open this file — first **`[ ]`** under **Execution checklist** is the resume point. Agents update **`[ ]` → `[X]`** after each item; humans scan the same file. Spec **`## Decisions`** holds audit notes, not tick state.

## Spec link

`docs/specs/[feature].md`

## Delivery phases

### P1 — [short name]

- **ACs:** AC-B1
- **Human gates:** HG-1 (if any)
- **Depends on:** none
- **Exit:** AC tests green OR checklist complete; `./scripts/verify.sh`; human gates documented in spec **Decisions**
- **Verify:** `pytest tests/...` or **Waiver:** manual checklist only

**Execution checklist**

- [ ] [Deliverable 1 — concrete repo or human outcome]
- [ ] [Deliverable 2]
- [ ] Phase **Exit** verified (command or waiver named above)
- [ ] Spec **Decisions** updated if this phase had **HG-*** or scope notes

### P2 — [short name]

- **ACs:** …
- **Depends on:** P1
- **Exit:** same shape

**Execution checklist**

- [ ] …
- [ ] Phase **Exit** verified
- [ ] Spec **Decisions** updated if needed

## Risks / open questions

- …

## Agent notes

- **Start:** `Run .cursor/skills/fabrication/references/EXECUTE_GEN.md` (or **`delivery-resumimpl seed_grow/plans/[feature]-plan.md`**).
- **Resume:** same; agent reads this file first.
- Rule: **`.cursor/rules/delivery-resumimpl.mdc`**
