# specify-feature

Write a feature spec under `docs/specs/` using `docs/templates/feature-spec.md`.

1. Read `docs/PRODUCT.md`, `docs/SECURITY.md`, `GLOSSARY.md`, and any linked architecture docs.
2. Include phase markers and plan link per template.
3. Draft **AC-*** criteria and **HG-*** human gates where automation is impossible.
4. Write matching `docs/plans/<feature>-plan.md` from `docs/templates/implementation-plan.md` (include **Execution checklist** **`[ ]`** per phase and **`<!-- delivery-status: new -->`**).
5. Add empty **`## Decisions`**; run **`align-requirements`** unless user **`skip align`**.
6. Stop unless the user asked to implement.
