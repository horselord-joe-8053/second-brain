# implement-feature

Implement an approved spec with **strict red → green TDD** per `docs/WEBAPP-TDD.md` and UI factory rules in `docs/specs/ui-factory-convention.md`.

**Provenance:** Factory harness skill (seeded from bootstrap kit). TDD pairing gate: **`scripts/check-tdd-pairing.sh`** (CI); AC mapping: **`scripts/check-ac-tests.py`**.

## Before code

1. Confirm **`align-requirements`** is satisfied: spec has **`## Decisions`** or documented **`skip align`** waiver.
2. Read the spec and its **`<!-- plan: … -->`** file. List **acceptance criteria** (AC ids) grouped by **delivery phase** (`P1`, then `P2`, …). Do not start a later phase before the earlier phase exit.
3. If the spec has `<!-- ac-tests: enforced -->`, plan one **`test_ac_<id>_...`** pytest/Vitest per AC **before** writing production code.
4. If substantial UI work on `frontend/src/**` is required, confirm `docs/specs/<feature>-ui-decision.md` exists (UI-CHOOSE per `ui-choose-look`) unless spec/ticket waives UI-CHOOSE with reason.
5. Confirm project-root **`utils/neat_logger`**, **`utils/neat_logger_ts`**, and **`utils/playwright_e2e`** exist. If `<repo-root>/utils` is missing, run **`bash bootstrap/core/scripts/apply-module.sh <repo> kit-utils`**.
6. **Do not** ask the human to confirm test seams — they are in the spec and `docs/WEBAPP-TDD.md`.

## Per AC (required order — agent checklist)

Do **one AC at a time**. Do **not** batch multiple ACs in a single edit pass.

1. **Red:** add or extend **`test_ac_*`** so it fails for the **right reason** (not import/syntax noise).
2. **Evidence:** run targeted pytest/vitest and **capture failing output** in the agent trace (one line: test name + assertion message).
3. **Green:** minimal production code until that test passes.
4. Re-run the **same** test; then the next AC.

When the slice is stable, run **`./scripts/verify.sh`**.

## Logging and smoke (same phase, after its ACs are green)

Follow **Logging** and **Playwright smoke** in `docs/WEBAPP-TDD.md` and the spec.

- Backend: `from utils.neat_logger import logger`. Log transitions. Use `with logger.Heartbeat("…"):` around quiet work (HTTP, LLM, batches).
- Frontend: `NeatLoggerFactory.frontendMonitor()` from `@floor35/neat-logger-ts`. Quiet async work uses `await log.withHeartbeat("…", async () => { ... })` (default interval 20s).
- Do not log secrets or full user source text.
- If this phase has a user-visible path, add one Playwright smoke under `frontend/e2e/` using `@floor35/playwright-e2e` and run `npx playwright test e2e --timeout=120000` (60s per test unless the plan says otherwise). Do not use `skipUnlessExternalPlaywrightStack` for that smoke. If a browser smoke is impractical, the waiver is already in the plan — do not skip silently.

<!-- Optional (not required in harness v1):
  - scripts/check-tdd-commits.sh — Tier 3 per-commit test-first in CI
  - Skill tdd-red-first — wrapper that loops this checklist per AC
-->

## Boundaries

- Mock external HTTP / OpenAI / Gemini at the backend test boundary when the spec includes those features.
- If touching `frontend/src/**`, apply chosen look from `-ui-decision.md`, ui-ux-pro-max checklist, or `design-system/*/MASTER.md`; do not change behavior unless the spec says so.

## Complete

- **`./scripts/verify.sh`** must pass (includes **`scripts/check-ac-tests.py`**; CI adds **`check-tdd-pairing.sh`** when `TDD_PAIRING_*` is set).
- Use evaluator or `/code-review` when valuable.
