<h1 id="refactor-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor: Fabrication skill, checkpoint log, roadmap</h1>

**Status:** **completed** (8 October 2026) on **`feature/bootstrap-seeding-skill`**. Every implementable box below is **`[X]`**. **TDD mode:** smoke-after-delete (no strict red-first); verify: `./scripts/verify.sh` + `bash .cursor/skills/fabrication/scripts/check-seed-kit.sh`.

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

- [X] Confirm [`REFACTOR_BOOTSTRAP_SEED_THREE_ZONES.md`](./REFACTOR_BOOTSTRAP_SEED_THREE_ZONES.md) has every implementable box `[X]`. If any `[ ]` remains, stop.
- [X] Confirm `.cursor/skills/fabrication/scripts/check-seed-kit.sh` exists and exits 0.
- [X] Confirm a run is specified to write `seed_grow/` and not to edit the kit (`references/EXECUTE_GEN.md`).

---

<h2 id="2-phase-2" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Phase 2 — Checkpoint log</h2>

The model does not write this log. Scripts append one JSON object per line.

- [X] Add `references/checkpoints.json` listing ids in order: `analyze`, `harness-seeded`, `modules-applied`, `verify-gate`, `product-seeded`. Mark `analyze` as repeatable.
- [X] Add `scripts/append-checkpoint.sh` → `$REPO_ROOT/seed_grow/progress.jsonl` (`ts`, `phase`, `checkpoint`, `status`; UTC ISO-8601).
- [X] Wired from `seed-harness.sh`, `apply-module.sh`, `seed-product.sh`, `EXECUTE_GEN.md` gate (`verify-gate`), `ANALYZE_SPECIFIC.md` success (`analyze`).
- [X] Repeated `analyze` appends; readers use the last line per id.
- [X] Helper refuses writes under the skill directory.

---

<h2 id="3-phase-3" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Phase 3 — Roadmap viewer</h2>

- [X] Add `assets/render-roadmap.sh` → `seed_grow/roadmap.html`.
- [X] Catalog order; last `done` per id; latest line = current node (CSS pulse).
- [X] `append-checkpoint.sh` invokes renderer after append.
- [X] Missing log renders catalog with no nodes done.

---

<h2 id="4-phase-4" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Phase 4 — Skill package</h2>

Move the kit from `bootstrap_seed/` into `.cursor/skills/fabrication/`. Do not leave a second copy at `bootstrap_seed/`.

- [X] Layout:

```text
.cursor/skills/fabrication/
├── SKILL.md
├── scripts/          # former bootstrap_seed/core/scripts and module scripts
├── references/       # EXECUTE_GEN.md, ANALYZE_SPECIFIC.md, checkpoints.json, harness docs
└── assets/           # render-roadmap.sh inputs that are not scripts, plus utils and module templates
```

- [X] `SKILL.md` frontmatter `name: fabrication`; description covers EXECUTE_GEN on / implementing prompts.
- [X] Body points at `references/EXECUTE_GEN.md`; forbids skill-tree edits; names `seed_grow/`.
- [X] Procedures remain in `references/` and `scripts/`.
- [X] Repo pointers retargeted to `.cursor/skills/fabrication/` (AGENTS, runbook, plans, rules).
- [X] Plan indexed in `docs_manual_gen/README.md`.

---

<h2 id="5-phase-5" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Phase 5 — Paths and purity</h2>

- [X] Scripts resolve paths via `fabrication-paths.sh` (skill tree, not repo-root kit).
- [X] `check-seed-kit.sh` guards `assets/` paths and forbidden strings; validates `SKILL.md` + `references/EXECUTE_GEN.md`.
- [X] `check-seed-kit.sh` exit 0; `./scripts/verify.sh` exit 0.
- [X] Copied to `~/.cursor/skills/fabrication/` on this machine (not committed).

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
