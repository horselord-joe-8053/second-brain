# Feature: [Name]

<!-- ac-tests: enforced -->
<!-- delivery-phase: P1 -->
<!-- plan: docs/plans/[feature]-plan.md -->

Product specs from this kit **must** keep the three lines above. **`delivery-phase`** lists every delivery phase this spec touches (`P1`, `P2`, …). **`plan`** is the matching file under `docs/plans/`. These are product increments, not bootstrap Part A / Part B.

Each **`**AC-<ID>:**`** needs a matching **`test_ac_<id>_...`** pytest/Vitest (see `docs/WEBAPP-TDD.md`) and a phase id that appears in the plan. Do not split one AC across phases.

## Goal

## Constraints

## Acceptance criteria (behavior)

1. **AC-T1:** (P1) …

## UI & layout

Use when the feature has a user-visible screen (or changes `frontend/src/**`).

- Layout / information hierarchy (where controls and feedback live)
- Responsive breakpoints if relevant (e.g. narrow vs wide)
- Design direction: cite `design-system/<project-slug>/MASTER.md` if it exists, or run **UI-CHOOSE** (`ui-choose-look`) before implement for substantial layout/visual work (see `docs/specs/ui-factory-convention.md`)
- After UI-CHOOSE: link `docs/specs/<feature>-ui-decision.md`
- Explicit **out of scope** for UI: no marketing sections, extra routes, or restyling unrelated areas unless listed here

## Accessibility (a11y)

Required when the feature has a user-visible screen.

- Keyboard: focus order, visible `:focus-visible`, operable controls
- Names: labels / `aria-label` on inputs and icon-only buttons
- Feedback: errors (`role="alert"`), status (`role="status"`), live regions where appropriate
- Contrast and motion: meet stated targets; respect `prefers-reduced-motion` when adding animation

## Out of scope

## Logging

Required on product specs. See **`docs/WEBAPP-TDD.md`** (Logging).

- **Backend:** `from utils.neat_logger import logger`. Log each important transition (`info`, `step`, `warning`, `error`). Wrap work that can go quiet (external HTTP, LLM, batch) in `with logger.Heartbeat("short label"):`.
- **Frontend:** `@floor35/neat-logger-ts` via `NeatLoggerFactory.frontendMonitor()`. Wrap quiet async work in `await log.withHeartbeat("short label", async () => { ... })`. Interval defaults to `heartbeat_interval_sec` (20s).
- Do not log secrets, API keys, or full user source text (`docs/SECURITY.md`).

## End-to-end smoke

Required when the feature has a user-visible path. Otherwise write **Waiver:** one sentence, and repeat that waiver in the plan phase exit.

- One Playwright smoke under `frontend/e2e/` using `@floor35/playwright-e2e` (`resolvePlaywrightBaseURL`, `getJson` / `postJson` / `pollUntil`, `createProxyMockRouter` when a live LLM must stay out).
- The smoke starts or attaches to the local stack. Do not use `skipUnlessExternalPlaywrightStack` for this smoke.
- Run it with a timeout during implementation (see the plan phase exit). It is not part of `./scripts/verify.sh`.

## Test seams

| AC | Phase | Seam | Test naming |
|----|-------|------|-------------|
| T1 | P1 | pytest / TestClient / Vitest | `test_ac_t1_...` |

Implement per **`docs/WEBAPP-TDD.md`** — failing **`test_ac_*`** before production code for each AC, in delivery-phase order from the linked plan.
