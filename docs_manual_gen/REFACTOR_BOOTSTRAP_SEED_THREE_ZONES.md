<h1 id="refactor-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor: three-zone bootstrap (<code>bootstrap_seed</code> / <code>seed_grow</code> / product)</h1>

**Status:** **completed** (8 October 2026). Landed on **`feature/bootstrap-seeding`**; checklist closed on **`feature/bootstrap-seeding-skill`**. Verify: `./scripts/verify.sh` + `bash bootstrap_seed/core/scripts/check-seed-kit.sh`. Every implementable box below is **`[X]`**.

**Execute with:** [`implref`](../.cursor/rules/implref-resumimpl-refactor-plan-followthrough.mdc) on **this file**. Do not run `bootstrap_seed/EXECUTE_GEN.md implementing` this plan. That command uses the kit this plan replaces and would write into `bootstrap/specific/`.

**Canonical path:** `docs_manual_gen/REFACTOR_BOOTSTRAP_SEED_THREE_ZONES.md`. On `implref` closeout, leave the file here. Do not `git mv` it to `cursor_gen/refactor_plans/`.

<h2 id="document-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Evidence](#1-evidence) — what git already shows.
2. [Zones](#2-zones) — what each tree holds.
3. [Phase 1 — Build the seed kit](#3-phase-1) — `bootstrap_seed/` from today’s agnostic `bootstrap_seed/` files.
4. [Phase 2 — Writes leave the kit](#4-phase-2) — `seed_grow/` is the only project slot.
5. [Phase 3 — Static gate](#5-phase-3) — the seed is safe to copy into a greenfield repo.
6. [Phase 4 — Back-fill this repo](#6-phase-4) — move this project’s ledger and instruction pack.
7. [Phase 5 — Retarget pointers](#7-phase-5) — this repo reads the new paths.
8. [Phase 6 — Product still verifies](#8-phase-6) — `./scripts/verify.sh`.
9. [Phase 7 — Delete the old kits](#9-phase-7) — `bootstrap/` and `bootstrap_general/` only (keep zone-1 **`bootstrap_seed/`**).
10. [Quality bar](#10-quality-bar) — tests, comments, docs.
11. [Deferred](#11-deferred) — out of this plan.

---

<h2 id="1-evidence" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Evidence</h2>

| Fact | Where |
|------|--------|
| Unified kit, `bootstrap/specific/`, `bootstrap/modules/second-brain/`, and the `second-brain)` branch in `apply-module.sh` arrived together | `ba3e1fb` (3 Oct 2026) |
| `apply-module.sh` has no diff after that commit | `git diff ba3e1fb HEAD -- bootstrap_seed/core/scripts/apply-module.sh` |
| Later kit edits retargeted example paths to `docs_manual_gen/PLAN_SECOND_BRAIN_HERMES_V1.md` and added checklist resume | `b38fd27`, `6e80fcc` (4 Oct 2026) |
| `bootstrap_general/EXECUTE_GEN.md` does not name a project module | same birth commit; keep that idea, do not keep the tree |
| Living checklist today | `seed_grow/plans/second-brain-hermes-v1-plan.md` (resume follows this copy, not only `bootstrap/specific/plans/`) |
| Product code already outside the kit | `brain/`, `harness/second-brain/`, `scripts/`, `scripts/verify-local.sh`, `tests/` |

Non-goals (prose, not checklist): do not reinstall Hermes, LLM Wiki, or Obsidian. Do not move `brain/`, `harness/`, `scripts/brain/`, `tests/`, or `docs_manual_gen/` into `seed_grow/`. Do not delete `bootstrap_webapp/` or the repo-root `utils/` copy in this plan.

---

<h2 id="2-zones" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Zones</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Zone</th><th>Path</th><th>Holds</th><th>Must not hold</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">1 Seed kit</td><td style="background:#e8f5e9"><code>bootstrap_seed/</code></td><td>Generic harness, built-in modules (<code>webapp</code>, <code>logging-neat</code>, <code>desktop-install</code>), generic utils, <code>EXECUTE_GEN.md</code></td><td><code>specific/</code>, <code>modules/second-brain/</code>, this product’s names, <code>utils/pglpl_cert/</code>, <code>utils/chatgpt/transcripts/</code></td></tr>
<tr><td style="background:#e3f2fd">2 Seed growth</td><td style="background:#fff3e0"><code>seed_grow/</code></td><td><code>bootstrap.md</code>, specs, plans, checklists, this project’s instruction pack (<code>MODULE.md</code>, <code>ANALYZE_FROM_PLAN.md</code>, <code>templates/verify-local.sh</code>)</td><td>Corpus, runtime skills, the kit, secrets</td></tr>
<tr><td style="background:#e3f2fd">3 Product</td><td style="background:#e8f5e9">rest of the repo</td><td><code>brain/</code>, <code>harness/</code>, operator <code>scripts/</code>, tests, <code>README.md</code>, <code>docs_manual_gen/</code>, the <code>verify-local.sh</code> that <code>verify.sh</code> runs</td><td>The kit, the working ledger, the instruction-pack sources</td></tr>
</tbody>
</table>

`modules/second-brain/` is the bootstrap instruction pack (how to analyze, which template to copy). It is not the product code. The template stays in zone 2. `scripts/verify-local.sh` stays in zone 3.

---

<h2 id="3-phase-1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Phase 1 — Build <code>bootstrap_seed/</code></h2>

Copy from **`bootstrap/`** only (historical unified kit). Output tree: **`bootstrap_seed/`**. Do not edit the old kit in this phase. Omit `bootstrap/specific/` and `bootstrap/modules/second-brain/`.

- [X] Copy `core/` (include `core/harness/cursor/rules/delivery-resumimpl.mdc`), `modules/webapp/`, `modules/logging-neat/`, `modules/desktop-install/`, `utils/` except the two trees in the next box, plus `README.md`, `EXECUTE_GEN.md`, `ANALYZE_SPECIFIC.md`.
- [X] Omit `utils/pglpl_cert/` and `utils/chatgpt/transcripts/`. Nothing outside `pglpl_cert/` imports it. Playwright writes new transcripts under `utils/chatgpt/playwright/test_result/transcripts/`, not the archived folder.
- [X] In `utils/chatgpt/HOWTO_EXTRACT_CHATGPT.md`, remove the instruction to commit copies into `utils/chatgpt/transcripts/` and the link to the missing `transcripts/README.md`.
- [X] Replace Second Brain example names in `README.md`, `EXECUTE_GEN.md`, `core/bootstrap-core.md`, `core/harness/docs/ARCHITECTURE.md`, and `modules/desktop-install/MODULE.md` with placeholders: `<project name>`, `<project general description file path>`.
- [X] Replace leftover product names that would ship inside the seed: `~/.hermes` and LLM Wiki in `EXECUTE_GEN.md` and `core/harness/docs/SECURITY.md`; `portuguese-learn` in `utils/neat_logger/neat_logger.py` and `HOWTO_USE_NEAT_LOGGER.md`; `gcp_pmle` in `utils/chatgpt/playwright/README.md`. Use a generic placeholder (`<tool config dir>`, `<repo root>`). Leave `@floor35/*` package names as the published npm names.
- [X] Rewrite every hardcoded `bootstrap/` kit path in the copied tree to `bootstrap_seed/` (`EXECUTE_GEN.md`, `README.md`, `core/bootstrap-core.md`, `delivery-resumimpl.mdc`, webapp factory docs, `desktop-install/MODULE.md`, skill files, `seed-utils.sh` comment). Shell scripts that compute `KIT` from their own path stay relative.

---

<h2 id="4-phase-2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phase 2 — Writes leave the kit</h2>

Touch only `bootstrap_seed/` here. Source files to change: `EXECUTE_GEN.md`, `ANALYZE_SPECIFIC.md`, `core/scripts/apply-module.sh`, `core/scripts/seed-product.sh`, `core/bootstrap-core.md`, `modules/webapp/ANALYZE_WEBAPP.md`.

- [X] `EXECUTE_GEN.md` states `KIT` = `bootstrap_seed/` and that a run must not create or edit any file under `bootstrap_seed/`.
- [X] The “implementing `<plan>`” row calls `ANALYZE_SPECIFIC.md` only. It must not name `modules/second-brain/ANALYZE_FROM_PLAN.md`.
- [X] `ANALYZE_SPECIFIC.md` authors `seed_grow/bootstrap.md`, `seed_grow/specs/`, and `seed_grow/plans/`. Delete the `specific/` destination and the Second Brain route row.
- [X] `seed-product.sh` reads `seed_grow/` (not `$KIT/specific`). It applies `phase2_modules`. It does not copy specs or plans into `docs/`.
- [X] Remove the `second-brain)` branch from `apply-module.sh`.
- [X] Add one generic branch: if `$REPO_ROOT/seed_grow/modules/<token>/MODULE.md` exists, follow that pack. If `templates/verify-local.sh` exists there and `$REPO_ROOT/scripts/verify-local.sh` is missing, copy it and `chmod +x`. Do not hardcode the token `second-brain`.
- [X] Built-in branches stay: `webapp`, `webapp-utils` / `kit-utils`, `logging-neat`, `ui-choose`, `desktop-install`.
- [X] File header on `apply-module.sh` and `seed-product.sh`: kit is read-only; project packs and the ledger live under `seed_grow/`.
- [X] Kit templates (`AGENTS.md`, `implementation-plan.md`, `delivery-resumimpl.mdc`, `specify-feature`, `implement-feature`) point resume at `seed_grow/plans/<feature>-plan.md`, not `docs/plans/`.

---

<h2 id="5-phase-3" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Phase 3 — Static gate</h2>

This is the check that a later copy of `bootstrap_seed/` into an empty repo can grow zone 2 and zone 3. Do not bootstrap a second product.

- [X] Add `bootstrap_seed/core/scripts/check-seed-kit.sh`. It fails if any of these exist or match under `bootstrap_seed/`: directory `specific/`, directory `modules/second-brain/`, directory `utils/pglpl_cert/`, directory `utils/chatgpt/transcripts/`, the strings `Second Brain`, `second-brain`, `docs_manual_gen`, `PLAN_SECOND_BRAIN`, `portuguese-learn`, `gcp_pmle`.
- [X] The same script fails unless `EXECUTE_GEN.md` and `ANALYZE_SPECIFIC.md` name `seed_grow/` and `EXECUTE_GEN.md` forbids edits under `bootstrap_seed/`.
- [X] Run the script; it exits 0.
- [X] Read `bootstrap_seed/EXECUTE_GEN.md` against both prompts: `run EXECUTE_GEN.md on <specific project description>` and `run EXECUTE_GEN.md implementing <specific project plan>`. Confirm both paths create `seed_grow/` (and, in phase 2 of that future run, product files) and do not instruct a write into the kit.

---

<h2 id="6-phase-4" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Phase 4 — Back-fill this repo</h2>

One living ledger. `seed_grow/plans/second-brain-hermes-v1-plan.md` is the copy resume uses today. If it differs from `bootstrap/specific/plans/second-brain-hermes-v1-plan.md`, the `docs/plans` file wins.

- [X] Create `seed_grow/`. Move `bootstrap/bootstrap.md`, `bootstrap/specific/specs/`, and the winning plan into `seed_grow/` (`bootstrap.md`, `specs/second-brain-hermes-v1.md`, `plans/second-brain-hermes-v1-plan.md`).
- [X] Move `bootstrap/modules/second-brain/` to `seed_grow/modules/second-brain/` (`MODULE.md`, `ANALYZE_FROM_PLAN.md`, `templates/verify-local.sh`).
- [X] Leave `scripts/verify-local.sh` where it is.
- [X] Remove duplicate live copies under **`docs/plans/`** and **`docs/specs/`** (optional snapshot kept in **`docs/plans/completed/`**). Keep `docs/plans/README.md`, `docs/plans/wip/`, and `docs/plans/completed/`. Point `docs/plans/README.md` at `seed_grow/plans/`.
- [X] In `seed_grow/specs/second-brain-hermes-v1.md`, set the plan comment to `seed_grow/plans/second-brain-hermes-v1-plan.md`.
- [X] Do not move `docs_manual_gen/`, `brain/`, `harness/`, or `scripts/brain/`.

---

<h2 id="7-phase-5" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Phase 5 — Retarget pointers in this repo</h2>

Installed copies, not the kit templates already edited in phase 2.

- [X] `AGENTS.md`, `.cursor/rules/delivery-resumimpl.mdc`, `.agents/skills/specify-feature/SKILL.md`, `.agents/skills/implement-feature/SKILL.md`, `docs/templates/implementation-plan.md`, `docs/PROJECT-TDD.md`: resume and kit paths say `bootstrap_seed/EXECUTE_GEN.md` and `seed_grow/plans/<feature>-plan.md`.
- [X] `docs_manual_gen/README.md`: add this plan to the index. Product resume points at `seed_grow/plans/second-brain-hermes-v1-plan.md` (this refactor itself runs by **`implref`** on this file, not **`EXECUTE_GEN`**).
- [X] `docs_manual_gen/SECOND_BRAIN_RUNBOOK.md`: `parse-bootstrap-meta.sh` reads `seed_grow/bootstrap.md` via `bootstrap_seed/core/scripts/parse-bootstrap-meta.sh`. Plan links point at `seed_grow/plans/`.
- [X] `docs_manual_gen/PLAN_SECOND_BRAIN_HERMES_V1.md` and `MORE_SECOND_BRAIN_QUERY_HERMES_MCP.md`: delivery-ledger links point at `seed_grow/plans/second-brain-hermes-v1-plan.md`.
- [X] `harness/second-brain/README.md` and `seed_grow/plans/second-brain-hermes-v1-plan.md`: start/resume lines use `bootstrap_seed/` and `seed_grow/plans/`.
- [X] `seed_grow/modules/second-brain/MODULE.md`: apply command is `bash bootstrap_seed/core/scripts/apply-module.sh <repo> second-brain`.

---

<h2 id="8-phase-6" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. Phase 6 — Product still verifies</h2>

- [X] `./scripts/verify.sh` exits 0 (it calls `scripts/verify-local.sh` and `tests/test_second_brain_corpus.py`).
- [X] `bash bootstrap_seed/core/scripts/check-seed-kit.sh` still exits 0 after the back-fill.
- [X] `rg` over the repo finds no `bootstrap/EXECUTE_GEN`, `bootstrap/specific`, or `bootstrap/modules/second-brain` outside historical mentions in this plan (old **`bootstrap/`** and **`bootstrap_general/`** trees deleted in phase 7).

---

<h2 id="9-phase-7" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">9. Phase 7 — Delete the old kits</h2>

- [X] `rg` for `bootstrap_general/` and stale `bootstrap/` kit paths. Fix any remaining live reference (product docs, rules, skills, runbook) before deleting old trees. **Keep** zone-1 **`bootstrap_seed/`**.
- [X] Delete the directory **`bootstrap/`** (legacy unified kit).
- [X] Delete the directory **`bootstrap_general/`**.
- [X] Re-run `check-seed-kit.sh` and `./scripts/verify.sh`. Both exit 0.
- [X] `rg` finds no live **`bootstrap/`** or **`bootstrap_general/`** tree; **`bootstrap_seed/`** remains the read-only kit (historical mentions may stay in this plan or **`bootstrap_webapp/`**).

---

<h2 id="10-quality-bar" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">10. Quality bar</h2>

<h3 id="10-1-tests" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">10.1 Tests</h3>

- The seed gate is `bootstrap_seed/core/scripts/check-seed-kit.sh` (phase 3). It is the regression check for kit purity. Run it after phase 3, phase 6, and phase 7.
- Product regression is `./scripts/verify.sh` after the move and after the delete. No Playwright pass: this refactor does not change UI.
- Do not mark phase 6 or phase 7 done if either command fails.

<h3 id="10-2-comments" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">10.2 Comments and docs</h3>

- `apply-module.sh` and `seed-product.sh` keep a short header: read-only kit, ledger and project packs under `seed_grow/`.
- Update the docs listed in phase 5 in the same change as the path edit. Do not add a new architecture doc.
- `docs_manual_gen/README.md` is the index row for this plan.

---

<h2 id="11-deferred" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">11. Deferred</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Item</th><th>Reason</th><th>Urgency</th><th>Recommended handling</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><code>bootstrap_webapp/</code></td><td style="background:#fff3e0">Superseded kit, still present, not in the delete ask</td><td style="background:#fff3e0">low</td><td>Delete in a later pass after <code>rg</code> shows nothing loads it</td></tr>
<tr><td style="background:#e3f2fd">Repo-root <code>utils/</code> (includes <code>pglpl_cert/</code> and ChatGPT transcripts)</td><td style="background:#fff3e0">Seeded copy already in the product tree; deleting it is separate from the kit</td><td style="background:#fff3e0">low</td><td>Leave until a product cleanup says those libraries are unused</td></tr>
<tr><td style="background:#e3f2fd"><code>utils/ui/</code> scoreboard, progression, audio player inside the seed</td><td style="background:#fff3e0">Language-app widgets, but they are shared libraries and still generic enough to ship</td><td style="background:#fff3e0">low</td><td>Keep in <code>bootstrap_seed/utils/ui/</code></td></tr>
<tr><td style="background:#e3f2fd">Live greenfield rehearsal</td><td style="background:#fff3e0">Phase 3 checks the instructions. A second repo that actually runs ANALYZE would create a real project</td><td style="background:#e8f5e9">after this plan</td><td>Copy <code>bootstrap_seed/</code> into an empty repo and run one ANALYZE-only prompt</td></tr>
</tbody>
</table>
