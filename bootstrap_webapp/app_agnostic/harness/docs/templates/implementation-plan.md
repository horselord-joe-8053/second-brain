# Plan: [Feature]

<!-- plan-for: docs/specs/[feature].md -->

**Delivery phases** (`P1`, `P2`, …) are ordered product increments for this spec. They are not bootstrap Part A (factory) or Part B (product run). One plan file per spec. Every AC lives in exactly one phase. Implement phases in order; do not start a later phase before the earlier phase exit is met.

## Spec link

`docs/specs/[feature].md`

## Delivery phases

### P1 — [short name]

- **ACs:** AC-T1
- **Tickets:** [names matching `app_specific/bootstrap.md` ticket slices]
- **Depends on:** none
- **Exit:** those ACs green under `./scripts/verify.sh`; backend/frontend logging from the spec is in the code paths this phase adds; Playwright smoke command below passed, or a one-sentence waiver
- **Smoke:** `cd frontend && npx playwright test e2e --timeout=120000` (adjust the path to this phase’s spec). Timeout on the Playwright project is 60s per test unless the spec says otherwise.

### P2 — [short name]

- **ACs:** AC-T2
- **Tickets:** …
- **Depends on:** P1
- **Exit:** same shape as P1
- **Smoke:** command or **Waiver:** …

## Risks / open questions
