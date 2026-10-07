# Web app — TDD policy

## Loop

1. Map acceptance criteria to **vertical slices** (smallest user-visible behavior).
2. **Use test seams** from this file and the approved feature spec **as written** — do **not** ask the human to confirm. If the spec is silent or contradictory, update the spec (or ask **one** clarifying question only when blocked).
3. **Red:** one failing test at one seam **per AC**.
4. **Green:** minimal code; run the test, then `./scripts/verify.sh`.
5. Refactor during review/evaluate, not inside red → green.

## AC ↔ test naming (enforced when spec says so)

For specs marked with `<!-- ac-tests: enforced -->` in `docs/specs/`:

- Each **`**AC-XN:**`** line (e.g. **AC-G1**, **AC-AI3**) MUST have at least one test whose name starts with **`test_ac_<xn>_`** (letters lowercased), e.g. `test_ac_g1_mocked_gemini_returns_data_image_url`.
- **Order of implementation:** add the failing `test_ac_*` **before** production code for that AC; do not land feature code ahead of its AC tests.
- **`./scripts/verify.sh`** runs **`scripts/check-ac-tests.py`** — merge gate fails if an enforced spec is missing tests.

Specs without the marker may still use TDD; the checker does not require AC-named tests until you opt in.

## Default seams (phase 1 homepage)

| Seam | Tool | Test behavior |
|------|------|----------------|
| HTTP API | pytest + `TestClient` | `GET /health` |
| React UI | Vitest + Testing Library | Homepage renders expected heading |

## Delivery phases

Bootstrap-authored specs carry **`<!-- delivery-phase: P1 -->`** and **`<!-- plan: docs/plans/<file> -->`**. Implement ACs in the order of those phases in the linked plan. Finish a phase’s exit (verify for its ACs, logging, smoke or waiver) before the next phase. Delivery phases are product increments, not factory phase 1 / product phase 2.

## Logging

Product backend logic uses **`utils/neat_logger`**: `from utils.neat_logger import logger`, then `info` / `step` / `warning` / `error` at important transitions. Work that can go quiet (HTTP, LLM, batches) uses `with logger.Heartbeat("short label"):`. Repo root must be on `PYTHONPATH` (`scripts/dev.sh` and `scripts/verify.sh` set this).

Product frontend logic uses **`utils/neat_logger_ts`** (`@floor35/neat-logger-ts`, `NeatLoggerFactory.frontendMonitor()`). Quiet async work uses `await log.withHeartbeat("short label", async () => { ... })`. The timer ticks while the event loop is awaiting; interval defaults to `heartbeat_interval_sec` (20s).

Do not log secrets or full user source text (`docs/SECURITY.md`). Skip the helper only when the module cannot import it, and say why in the spec or plan.

## Playwright smoke

When a delivery phase has a user-visible path, add one Playwright smoke under `frontend/e2e/` using **`utils/playwright_e2e`** (`resolvePlaywrightBaseURL`, JSON helpers, `createProxyMockRouter` if a live LLM must stay out). Run it with a timeout (`npx playwright test e2e --timeout=120000`; 60s per test unless the plan says otherwise) and treat a failure as the phase not being done. Do not use `skipUnlessExternalPlaywrightStack` for this smoke. If a browser smoke is impractical, the plan records a one-sentence waiver. This smoke is not part of `./scripts/verify.sh`.

## Product phase seams

When phase 2 adds features, **do not** add a second TDD doc. Put the seam table in the **approved feature spec** (`docs/specs/*.md`); this file stays the **procedure** (loop, avoid, UI tickets, Matt `/tdd`).

## Avoid

- Horizontal slicing (all tests, then all code).
- **Implementation-first** (code before failing tests) on enforced specs.
- Testing private helpers instead of public behavior.
- Live LLM / Gemini calls in CI.

## UI polish and tickets

See `docs/specs/ui-factory-convention.md`. **`/to-tickets`:** fold UI+a11y into frontend slices, or **UI-CHOOSE** then implement blocked by `-ui-decision.md`.

## Matt `/tdd`

[mattpocock/skills `/tdd`](https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md) is the procedure; **seam tables** live in feature specs after phase 2.

## Mechanical gates (not optional for factory apps)

| Gate | What it proves | What it does **not** prove |
|------|----------------|----------------------------|
| **`check-ac-tests.py`** | Every enforced AC has a `test_ac_*`; tests pass | Tests were written before prod code |
| **`check-tdd-pairing.sh`** (CI: `TDD_PAIRING_BASE` / `TDD_PAIRING_HEAD`) | PR diff that touches `backend/app/**` or `frontend/src/**` also touches tests | Strict red→green order inside one commit |
| **`implement-feature` skill** | Agent procedure: one AC, show failing output, then green | Agent compliance without human/CI review |

Local **`verify.sh`** runs AC mapping + full suite. **Pairing runs in CI** (and locally when you export `TDD_PAIRING_*`).

<!-- Optional future gates (document only — not shipped in harness v1):
  - **`check-tdd-commits.sh`** — Tier 3: fail impl-only commits in `base..head` (weak with squash merge).
  - **`tdd-red-first` skill** — thin wrapper looping implement-feature per AC.
  - Two-commit RED/GREEN policy per behavior (test-only commit must fail CI in isolation).
-->

## Why agents skip TDD (fix)

- **`implement-feature`** must **not** wait for human test-seam approval — seams are in the spec.
- Chat sessions often batch-edit; **do not rely on `.mdc` rules alone** — use **`check-ac-tests.py`** + **`check-tdd-pairing.sh`** in CI.
