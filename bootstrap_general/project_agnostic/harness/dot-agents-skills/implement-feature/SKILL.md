# implement-feature

Implement an approved spec with red → green TDD per `docs/PROJECT-TDD.md`.

**Provenance:** General harness (bootstrap_general). AC mapping: `scripts/check-ac-tests.py`.

## Before code

1. **`align-requirements`** satisfied (`## Decisions` or **`skip align`**).
2. Read spec and linked plan; list ACs and **HG-*** by delivery phase.
3. For **`<!-- ac-tests: enforced -->`**, add failing `test_ac_*` before production edits.
4. For each **HG-***, post clear human instructions and **stop** until confirmed — do not simulate external installs.

## Per AC

1. Red → evidence → green → `./scripts/verify.sh` when the phase exit requires it.

## Human gates

When the plan lists **HG-***, use `docs/templates/human-gate.md` shape in chat; update **Decisions** after confirmation.

## Complete

- Phase **Exit** criteria met.
- `./scripts/verify.sh` passes when the plan requires it.
