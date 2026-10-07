# implement-feature

Implement an approved spec with red → green TDD per `docs/PROJECT-TDD.md`.

**Provenance:** `bootstrap_seed/core` harness. AC mapping: `scripts/check-ac-tests.py`.

## Before code

1. **`align-requirements`** satisfied (`## Decisions` or **`skip align`**).
2. Read spec and linked **`docs/plans/*-plan.md`** (`<!-- plan: … -->`). List ACs and **HG-*** by delivery phase; **resume from the first `[ ]`** in **Execution checklist** (see **`delivery-resumimpl`** rule).
3. For **`<!-- ac-tests: enforced -->`**, add failing `test_ac_*` before production edits.
4. For each **HG-***, post clear human instructions and **stop** until confirmed — do not simulate external installs.

## Per AC

1. Red → evidence → green → `./scripts/verify.sh` when the phase exit requires it.

## Human gates

When the plan lists **HG-***, use `docs/templates/human-gate.md` shape in chat; update **Decisions** after confirmation.

## Delivery checklist (plan file)

After each completed checklist bullet or phase **Exit**:

1. Edit the linked plan: **`[ ]` → `[X]`**; prefix phase heading with **`[X]`** when all bullets in that phase are done.
2. Set **`<!-- delivery-status: wip -->`** on first progress (from **`new`**).
3. Set **`<!-- delivery-status: completed -->`** when every implementable checklist item is **`[X]`** (optional archive copy under **`docs/plans/completed/`**).

Spec **`## Decisions`** = audit trail; **`docs/plans/…-plan.md`** = tick state.

## Complete

- Phase **Exit** criteria met.
- `./scripts/verify.sh` passes when the plan requires it.
- Plan checkboxes and **delivery-status** reflect reality.
