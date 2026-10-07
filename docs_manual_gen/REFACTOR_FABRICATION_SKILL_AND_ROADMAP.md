<h1 id="refactor-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor: Fabrication skill, checkpoint log, roadmap</h1>

**Status:** plan only (5 October 2026). Every implementable box is `[ ]`.

**After:** [`REFACTOR_BOOTSTRAP_SEED_THREE_ZONES.md`](./REFACTOR_BOOTSTRAP_SEED_THREE_ZONES.md). Do not start until that plan’s implementable boxes are `[X]`.

**Execute with:** [`implref`](../.cursor/rules/implref-resumimpl-refactor-plan-followthrough.mdc) on **this file**. Do not run `EXECUTE_GEN.md implementing` this plan.

**Canonical path:** `docs_manual_gen/REFACTOR_FABRICATION_SKILL_AND_ROADMAP.md`. On `implref` closeout, leave the file here. Do not `git mv` it to `cursor_gen/refactor_plans/`.

**Format:** [Agent Skills](https://agentskills.io/specification). `SKILL.md` plus `scripts/`, `references/`, `assets/`. Template: [anthropics/skills](https://github.com/anthropics/skills).

**Ship decision:** the skill tree in this repo is `.cursor/skills/fabrication/`. Other repos get a copy at `~/.cursor/skills/fabrication/`. No separate git repo in this plan.

**Out of scope:** splitting specify, TDD, and implement into other skills, and any new package format, installer, or marketplace.

<h2 id="document-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Phase 1 — Gate](#1-phase-1) — the three-zone kit exists.
2. [Phase 2 — Checkpoint log](#2-phase-2) — scripts append JSONL.
3. [Phase 3 — Roadmap viewer](#3-phase-3) — HTML from that log.
4. [Phase 4 — Skill package](#4-phase-4) — move the kit under the skill.
5. [Phase 5 — Paths and purity](#5-phase-5) — this repo and the copy use the skill directory.
6. [Quality bar](#6-quality-bar) — tests, comments, docs.
7. [Deferred](#7-deferred) — not this plan.

---

<h2 id="1-phase-1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Phase 1 — Gate</h2>

- [ ] Confirm [`REFACTOR_BOOTSTRAP_SEED_THREE_ZONES.md`](./REFACTOR_BOOTSTRAP_SEED_THREE_ZONES.md) has every implementable box `[X]`. If any `[ ]` remains, stop.
- [ ] Confirm `bootstrap_seed/core/scripts/check-seed-kit.sh` exists and exits 0.
- [ ] Confirm a run is specified to write `seed_grow/` and not to edit the kit.

---

<h2 id="2-phase-2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Phase 2 — Checkpoint log</h2>

The model does not write this log. Scripts append one JSON object per line.

- [ ] Add `bootstrap_seed/references/checkpoints.json` (path may still be `bootstrap_seed/` until phase 4) listing ids in order: `analyze`, `harness-seeded`, `modules-applied`, `verify-gate`, `product-seeded`. Mark `analyze` as repeatable.
- [ ] Add a helper `append-checkpoint.sh` that appends to `$REPO_ROOT/seed_grow/progress.jsonl`. Each line is `{"ts","phase","checkpoint","status"}` with `status` of `done` or `failed`. `ts` is UTC ISO-8601.
- [ ] Call it from `seed-harness.sh` (`harness-seeded`), `apply-module.sh` (`modules-applied`), `seed-product.sh` (`product-seeded`), and the verify step named in `EXECUTE_GEN.md` (`verify-gate`). `ANALYZE_SPECIFIC.md`’s success step calls it for `analyze`.
- [ ] A repeated `analyze` appends a new line. Readers use the last line for that id.
- [ ] The helper refuses to write inside the kit directory.

---

<h2 id="3-phase-3" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Phase 3 — Roadmap viewer</h2>

- [ ] Add `bootstrap_seed/assets/render-roadmap.sh`. It reads `checkpoints.json` and `seed_grow/progress.jsonl` and writes `seed_grow/roadmap.html`.
- [ ] The HTML shows the ids in catalog order. A checkpoint whose last status is `done` is marked done. The latest line is the current node, with a CSS animation on that node only.
- [ ] `append-checkpoint.sh` runs `render-roadmap.sh` after a successful append.
- [ ] A missing log still renders the catalog with no node done.

---

<h2 id="4-phase-4" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phase 4 — Skill package</h2>

Move the kit from `bootstrap_seed/` into `.cursor/skills/fabrication/`. Do not leave a second copy at `bootstrap_seed/`.

- [ ] Layout:

```text
.cursor/skills/fabrication/
├── SKILL.md
├── scripts/          # former bootstrap_seed/core/scripts and module scripts
├── references/       # EXECUTE_GEN.md, ANALYZE_SPECIFIC.md, checkpoints.json, harness docs
└── assets/           # render-roadmap.sh inputs that are not scripts, plus utils and module templates
```

- [ ] `SKILL.md` frontmatter: `name: fabrication`. Description states when to run: `run EXECUTE_GEN.md on <description>` and `run EXECUTE_GEN.md implementing <plan>`. Do not set `disable-model-invocation`.
- [ ] The body only points at `references/EXECUTE_GEN.md`, names `seed_grow/` as the write target, and forbids creating or editing files under `.cursor/skills/fabrication/`.
- [ ] Keep the body short. Procedures stay in `references/` and `scripts/`.
- [ ] Retarget this repo’s pointers from `bootstrap_seed/` to `.cursor/skills/fabrication/` (`AGENTS.md`, `docs_manual_gen/README.md`, runbook, `seed_grow/` plan resume lines, `delivery-resumimpl`).
- [ ] Add this plan to the index in `docs_manual_gen/README.md`.

---

<h2 id="5-phase-5" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Phase 5 — Paths and purity</h2>

- [ ] Scripts resolve the kit from their own directory (the skill tree), not from `$REPO_ROOT/bootstrap_seed/`.
- [ ] Move `check-seed-kit.sh` with the kit. It still fails on `specific/`, `modules/second-brain/`, `utils/pglpl_cert/`, `utils/chatgpt/transcripts/`, and the strings `Second Brain`, `second-brain`, `docs_manual_gen`, `PLAN_SECOND_BRAIN`, `portuguese-learn`, `gcp_pmle`.
- [ ] It also fails if `SKILL.md` does not name `seed_grow/` and does not forbid edits to the skill directory.
- [ ] `check-seed-kit.sh` exits 0. `./scripts/verify.sh` exits 0.
- [ ] Copy `.cursor/skills/fabrication/` to `~/.cursor/skills/fabrication/` so another repo on this machine can invoke it. Do not commit that home-directory copy.

---

<h2 id="6-quality-bar" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Quality bar</h2>

<h3 id="6-1-tests" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">6.1 Tests</h3>

- A fixture log with two `analyze` lines and one `harness-seeded` line: the renderer marks `analyze` from the second line and `harness-seeded` done.
- `check-seed-kit.sh` exits 0 on the skill tree and non-zero if a forbidden string is planted in a temp copy.
- `./scripts/verify.sh` after phase 5. No Playwright pass.

<h3 id="6-2-comments" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">6.2 Comments and docs</h3>

- Header on `append-checkpoint.sh`: zone 2 log, kit directory is not a write target.
- `SKILL.md` is the only new entry doc. Update the path list in phase 4. Do not add an architecture doc.

---

<h2 id="7-deferred" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Deferred</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Item</th><th>Reason</th><th>Urgency</th><th>Recommended handling</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Own git repo for the skill</td><td style="background:#fff3e0">This plan ships a directory copy to <code>~/.cursor/skills/</code></td><td style="background:#fff3e0">low</td><td>Split the skill out only if people outside this machine need it</td></tr>
<tr><td style="background:#e3f2fd">Live greenfield rehearsal</td><td style="background:#fff3e0">Same limit as the three-zone plan: a real ANALYZE creates a project</td><td style="background:#e8f5e9">after this plan</td><td>Copy the skill into an empty repo and run one ANALYZE-only prompt</td></tr>
</tbody>
</table>
