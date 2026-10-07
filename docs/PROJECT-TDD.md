# Second Brain — TDD and verification

## Scope

This policy applies to **any** project bootstrapped with `bootstrap_seed/` (core profile **general** or **webapp**): infra, agents, docs-only corpora, mixed repos, or optional web stacks.

## Enforced specs

When a feature spec includes `<!-- ac-tests: enforced -->`:

1. Each `**AC-<PREFIX><N>:**` needs a failing test named `test_ac_<prefix><n>_...` **before** production changes.
2. Tests may live under `tests/`, `backend/tests/`, `harness/tests/`, or other seams declared in the spec.
3. Run `./scripts/verify.sh` before calling a delivery phase done.

When a spec uses `<!-- ac-tests: optional -->` or omits the marker, verification is **manual checklist + plan exit** unless the plan names automated commands.

## Human gates

Steps that need the human (install desktop app, OAuth, API keys in external tools) belong in the spec as **`**HG-*:**`** human gates — not `test_ac_*`. Record completion in `## Decisions` or a log; do not fake automation.

## Logging

Use `utils/neat_logger` when Python code exists and the spec requires logging. Skip for pure shell/docs phases.

## Smoke / verification

Each plan phase **Exit** names either:

- a shell command (e.g. `./scripts/verify-local.sh`, `pytest tests/test_brain_smoke.py`), or  
- **Waiver:** one sentence.

Playwright and Vitest are **optional** — only when the spec declares a browser or frontend stack.

## Implement order

Follow delivery phases `P1`, `P2`, … in the linked **`docs/plans/*-plan.md`**. Use the **`implement-feature`** skill per AC and maintain **Execution checklist** **`[ ]`/`[X]`** (see **`delivery-resumimpl`**). Resume from the first open **`[ ]`**.
