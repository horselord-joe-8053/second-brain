<h1 id="analyze-app-specific-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Analyze app and author `app_specific/`</h1>

**Human says:** run **`bootstrap_webapp/ANALYZE_APP_SPECIFIC.md`** **for the following app:** *&lt;description&gt;*  
**Workspace:** app repo root (parent of **`bootstrap_webapp/`**). **`KIT`** = `bootstrap_webapp/`.

The **app description** is the text after **`for the following app:`** or **`for webapp:`** in the human message (or the whole message if they paste only the description). Treat it as the product brief.

<h3 id="agent-mandate" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">For the coding agent</h3>

Produce **`KIT/app_specific/bootstrap.md`**, **`KIT/app_specific/specs/<spec_file>`**, and **`KIT/app_specific/plans/<plan_file>`** so a later run of **`KIT/EXECUTE_GEN.md`** can seed and implement phase 2 without guessing. **Do not** implement the app in this task—**author kit files only** (unless the human explicitly asks for more).

**Delivery phases** (`P1`, `P2`, …) group ACs and tickets into ordered increments inside the plan. They are not bootstrap Part A / Part B. One plan file per spec. Each AC belongs to exactly one phase.

Use **AskQuestion** (multiple choice) when the description leaves **material** ambiguity (data storage, auth, API surface, language/locale, MVP scope). Do **not** ask the human to confirm test seams or TDD loop—those come from the kit. Ask **one batch** of questions when possible; proceed with documented defaults only for **non-material** gaps and list defaults in the spec **Constraints** section.

## Document outline

1. [Inputs and kit context](#inputs)
2. [Research and gap-fill](#research)
3. [Clarifications](#clarify)
4. [Author artifacts](#author) — bootstrap, specs, delivery-phase plans.
5. [Validation before success](#validate)

---

<h2 id="inputs" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Inputs and kit context</h2>

Read before writing:

| Source | Why |
|--------|-----|
| Human **app description** | Primary intent |
| **`KIT/app_agnostic/bootstrap_webapp.md`** Part B (§B2–§B6) | What phase 2 expects from `app_specific/` |
| **`KIT/app_agnostic/harness/docs/templates/feature-spec.md`** | Spec shape (phase markers, Goal, Constraints, ACs, UI & layout, a11y, logging, smoke, seams) |
| **`KIT/app_agnostic/harness/docs/templates/implementation-plan.md`** | Plan shape (delivery phases, exits, smoke command or waiver) |
| **`KIT/utils/neat_logger/HOWTO_USE_NEAT_LOGGER.md`** | Backend logging API (`logger`, `Heartbeat`) |
| **`KIT/utils/neat_logger_ts/HOWTO.md`** | Frontend logging API (`NeatLoggerFactory.frontendMonitor`) |
| **`KIT/utils/playwright_e2e/HOWTO_USE_PLAYWRIGHT_E2E.md`** | Playwright helpers for smoke tests |
| **`KIT/app_agnostic/harness/docs/WEBAPP-TDD.md`** | Procedure; seams live in the feature spec |
| **`KIT/app_agnostic/harness/docs/SECURITY.md`** | Server-side keys, logging, localStorage rules |
| **`KIT/app_agnostic/harness/docs/specs/ui-factory-convention.md`** | UI-CHOOSE ticket naming (`<feature_id>-ui-decision.md`) |
| **`KIT/app_agnostic/templates/backend.env.template`** | Phase 1 always seeds **`LLM_*`**; human sets **`LLM_API_KEY`** after **`seed-dev-env.sh`** |
| **`KIT/app_specific/`** (if present) | Reference quality (e.g. Traduz); replace only after human choice if non-empty |

**Stack assumption (from kit):** React + FastAPI, `./scripts/verify.sh`, default dev ports **8900** / **5973** (`APP_BACKEND_PORT`, `APP_FRONTEND_PORT` in factory `dev.sh`) unless the app description requires otherwise—then state ports in the spec **Constraints**.

---

<h2 id="research" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Research and gap-fill</h2>

Analyze the description **carefully and thoroughly**. Where the brief is silent on industry-norm behavior for this class of app, **research** (web search, current docs, reputable patterns) and **fill gaps** in the spec—do not leave critical behavior undefined.

Examples of gap-fill (adapt to the app):

- Validation limits, error shapes, empty states  
- Privacy (what never hits the server), retention caps  
- Accessibility baseline (keyboard, labels, alert/status regions)  
- MVP **non-goals** to prevent scope creep  

Record non-obvious choices in **Constraints** or **Out of scope**. Prefer **testable** acceptance criteria over vague goals.

---

<h2 id="clarify" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Clarifications</h2>

Use **AskQuestion** when any of these would **materially** change ACs or architecture:

- Authentication / multi-user vs anonymous  
- Server-side persistence vs browser-only vs none  
- External integrations (LLM, payments, third-party APIs)  
- Language, locale, or regulatory constraints  
- Single page vs multiple routes for v1  
- Replace vs keep existing **`app_specific/`** files when already present  

If the human does not answer, **stop** and report blockers—do not declare success.

---

<h2 id="author" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Author artifacts</h2>

Create or update **only** under **`KIT/app_specific/`**:

<h3 id="author-bootstrap" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.1 `bootstrap.md` (kit-only, not seeded)</h3>

Structure (match Traduz reference):

- Title: phase 2 kit entry  
- **Kit meta** fenced block (`text`) with **exact keys** on their own lines (`feature_id`, `spec_file`, `plan_file`, `env_append`, `done_display_name`). `seed-product.sh` reads `env_append`; the other keys are for the agent:

```text
feature_id: <kebab-id>-v1
spec_file: <same-as-spec-filename>.md
plan_file: <same-stem>-plan.md
env_append: none
done_display_name: <Human-facing app name>
```

- **`env_append`:** use **`none`** (legacy). **`LLM_*`** is always written from **`backend.env.template`** in phase 1; phase 2 does not append env snippets. Document in **Mission** / spec **Constraints** when the app **requires** a key vs optional fallback.  
- **Mission** — one short paragraph aligned with the spec **Goal**.  
- **Ticket slices** — ordered list for **`/to-tickets`**, grouped under the same **`P1` / `P2`** ids as the plan: vertical slices, blockers, **UI-CHOOSE** (`feature_id`) then **UI implement** blocked by `docs/specs/<feature_id>-ui-decision.md` when the app has a substantial UI. Do not put a later phase’s tickets ahead of an earlier phase’s exit.  
- **Glossary / AGENTS** — terms + invariants; point implementers to **`docs/WEBAPP-TDD.md`** and **`docs/specs/<spec_file>`** after seed.  
- **UI mock notes** — what production-density mock should show (regions, sample content, empty/error states).

<h3 id="author-spec" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.2 `specs/<spec_file>` (seeded to `docs/specs/`)</h3>

Follow **`feature-spec.md`** sections. Minimum:

- **`<!-- ac-tests: enforced -->`** (required — enables **`check-ac-tests.py`** in verify)
- **`<!-- delivery-phase: P1 -->`** (space-separated ids when the spec spans more than one phase, earliest first)
- **`<!-- plan: docs/plans/<plan_file> -->`** matching kit meta **`plan_file`**
- **Goal**, **Constraints** (include security/privacy from harness), **Acceptance criteria** as **`**AC-<PREFIX><N>:**`** with a phase tag, e.g. **`**AC-D1:** (P1)`**
- **UI & layout** and **Accessibility** when there is a user-visible screen  
- **Logging** and **End-to-end smoke** (or a one-sentence smoke waiver) as in the template  
- **Out of scope**  
- **Test seams** table: each AC → phase + seam + expected **`test_ac_<prefix><n>_...`** name  
- Closing line: implement per **`docs/WEBAPP-TDD.md`**, agent applies **as written**

Filename must equal **`spec_file`** in kit meta.

Ensure **`mkdir -p KIT/app_specific/specs`** before writing.

<h3 id="author-plan" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.3 `plans/<plan_file>` (seeded to `docs/plans/`)</h3>

Follow **`implementation-plan.md`**. One file per spec. Filename must equal **`plan_file`** in kit meta.

Split work into delivery phases when the product has a real sequence (API before UI, deterministic path before LLM, UI-CHOOSE before visual implement). Use a single **P1** when the spec is already one vertical slice. Prefer two to four phases. Do not invent a phase that cannot be verified on its own.

Each phase lists its ACs, the matching ticket names, what it depends on, an exit check (`./scripts/verify.sh` for those ACs, logging present, smoke command or waiver). Phases are contiguous: **P1**, **P2**, … with no gaps. Every AC in the spec appears in exactly one phase, and every phase id in the spec marker appears as a heading in the plan.

Ensure **`mkdir -p KIT/app_specific/plans`** before writing.

---

<h2 id="validate" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Validation before success</h2>

All must pass before reporting **ANALYZE success**:

- [ ] **`KIT/app_specific/bootstrap.md`** exists; kit meta block parses (`feature_id`, `spec_file`, `plan_file`, `env_append`, `done_display_name`)  
- [ ] **`KIT/app_specific/specs/<spec_file>`** exists and matches **`spec_file`** in meta  
- [ ] **`KIT/app_specific/plans/<plan_file>`** exists and matches **`plan_file`** in meta  
- [ ] Spec includes **`<!-- ac-tests: enforced -->`**, **`<!-- delivery-phase: … -->`**, **`<!-- plan: docs/plans/<plan_file> -->`**, and **`**AC-*:**`** ids with a phase column in the test seam table  
- [ ] Plan phases are contiguous (`P1`…); each AC is in exactly one phase; spec phase ids match plan headings  
- [ ] Spec has **Logging** and **End-to-end smoke** (or a waiver repeated in the plan)  
- [ ] Spec ACs cover the human description; gaps filled or called out in Constraints  
- [ ] Ticket slices use the same phase ids and order as the plan; UI-CHOOSE present iff substantial UI  
- [ ] **`env_append`** is **`none`** (or documented legacy value if an old kit copy still appends)  
- [ ] Dry-run: `bash KIT/app_agnostic/scripts/seed-product.sh <workspace-root>` succeeds (copies `docs/specs/` and `docs/plans/`)

**Success message to human:** list files written and confirm they may run **`bootstrap_webapp/EXECUTE_GEN.md`** (or **`EXECUTE_GEN.md`** with the same app description for full greenfield).

**Failure:** list blockers; do not claim success.
