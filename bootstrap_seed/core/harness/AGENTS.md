# {{PROJECT_NAME}} Agent Guide

{{PROJECT_DESCRIPTION}}

Domain vocabulary: `GLOSSARY.md`.

## Sources of truth

- Product: `docs/PRODUCT.md`
- Architecture: `docs/ARCHITECTURE.md`
- Security: `docs/SECURITY.md`
- TDD / verification: `docs/PROJECT-TDD.md`
- Templates: `docs/templates/`
- Specs: `docs/specs/`
- Plans: `docs/plans/`

## Feature lifecycle

**SPEC → ALIGN → PLAN → IMPLEMENT → VERIFY → COMPLETE**

- **SPEC:** `specify-feature` or existing architecture/plan docs converted to specs.
- **ALIGN:** `align-requirements` — ≤3 questions; `## Decisions` in spec.
- **PLAN:** `docs/plans/<feature>-plan.md` with delivery phases `P1`, `P2`, … and **Execution checklist** **`[ ]`/`[X]`** (human-visible progress).
- **IMPLEMENT:** `implement-feature` — red → green per AC when enforced; respect **human gates** (`HG-*`); tick plan checkboxes after each exit.
- **RESUME:** `delivery-resumimpl docs/plans/<feature>-plan.md` or **`Run bootstrap_seed/EXECUTE_GEN.md`** (agent reads plan first).
- **VERIFY:** `./scripts/verify.sh` plus any phase **Exit** commands in the plan.
- **UI-CHOOSE:** enable **`profile: webapp`** and **`ui-choose`** module when a spec needs factory UI polish; otherwise document UI in the spec without UI-CHOOSE.

## Stack

Not fixed. Spec **Constraints** declare languages, tools, and verify commands. Optional FastAPI/React may coexist if the project adds them later.
