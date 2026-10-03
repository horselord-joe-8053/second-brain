# specify-feature

Write a feature spec under `docs/specs/` using `docs/templates/feature-spec.md`.

1. Read `docs/PRODUCT.md`, `docs/SECURITY.md`, `GLOSSARY.md`, and `docs/specs/ui-factory-convention.md`.
2. Include **`<!-- ac-tests: enforced -->`**, **`<!-- delivery-phase: P1 -->`** (every phase the spec touches), and **`<!-- plan: docs/plans/<feature>-plan.md -->`**.
3. Draft testable **behavior** acceptance criteria as **`**AC-<PREFIX><N>:** (P1)`** (e.g. **AC-T1**) and a **Test seams** table with phase, seam, and **`test_ac_<prefix><n>_...`** names (see `docs/WEBAPP-TDD.md`). One AC belongs to one delivery phase.
4. Fill **Logging** and **End-to-end smoke** (or a one-sentence waiver). If the feature has a **user-visible screen** or changes `frontend/src/**`, fill **UI & layout** and **Accessibility (a11y)** sections. Do not leave them empty or “TBD” without human approval.
5. Write the matching plan at `docs/plans/<feature>-plan.md` from `docs/templates/implementation-plan.md`: contiguous `P1`, `P2`, … with ACs, tickets, exit, and a smoke command or waiver.
6. Add an empty **`## Decisions`** section (filled by **`align-requirements`** before implement).
7. Save the spec to `docs/specs/<feature>.md`.
8. Run **`align-requirements`** (≤3 questions) unless the user explicitly **`skip align`**.
9. Stop unless the user asked to implement.
