# Plan: [Feature]

<!-- plan-for: docs/specs/[feature].md -->

**Delivery phases** (`P1`, `P2`, …) are ordered increments. One plan per spec. Implement in order.

## Spec link

`docs/specs/[feature].md`

## Delivery phases

### P1 — [short name]

- **ACs:** AC-B1
- **Human gates:** HG-1 (if any)
- **Tickets:** [names matching `project_specific/bootstrap.md`]
- **Depends on:** none
- **Exit:** AC tests green OR checklist complete; `./scripts/verify.sh`; human gates documented in spec **Decisions**
- **Verify:** `pytest tests/...` or **Waiver:** manual checklist only

### P2 — [short name]

- **ACs:** …
- **Depends on:** P1
- **Exit:** same shape

## Risks / open questions
