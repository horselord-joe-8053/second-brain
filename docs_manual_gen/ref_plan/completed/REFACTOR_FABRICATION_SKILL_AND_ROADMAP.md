<h1 id="refactor-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor: Fabrication skill, checkpoint log, roadmap</h1>

**Status:** **Part I–II + Phase 14 completed** — phases **1–14** **`[X]`**. **TDD mode:** Part I smoke-after-delete; Part II strict-TDD; **Phase 14** smoke-after-delete (wrapper removal) + doc grep. **Verify:** `./scripts/verify.sh`.

**After (Part I):** [`REFACTOR_BOOTSTRAP_SEED_THREE_ZONES.md`](./REFACTOR_BOOTSTRAP_SEED_THREE_ZONES.md) — all boxes **`[X]`**. **After (Part II):** [`REFACTOR_BRAIN_STACK_CONFIG.md`](./REFACTOR_BRAIN_STACK_CONFIG.md) P1–P3 **completed**.

**Execute with:** [`implref`](../.cursor/rules/implref-resumimpl-refactor-plan-followthrough.mdc) on **this file**. Resume Part II from the first **`[ ]`** in §9. Do not run `EXECUTE_GEN.md implementing` this plan.

**Canonical path:** `docs_manual_gen/ref_plan/completed/REFACTOR_FABRICATION_SKILL_AND_ROADMAP.md`.

**Part I — format:** [Agent Skills](https://agentskills.io/specification). `SKILL.md` plus `scripts/`, `references/`, `assets/`. **Ship:** `.cursor/skills/fabrication/` (+ optional `~/.cursor/skills/fabrication/` copy).

**Part II — architecture:** [`second-brain-llm-wiki-architecture.md`](./second-brain-llm-wiki-architecture.md) §8 — Nashsu + `brain/` + **`SKILL.md` + MCP + raw-source contract**; **Hermes** default harness, **OpenClaw** first alternate (Telegram/WhatsApp via adapter channel config, not duplicate ingest).

**Out of scope (whole doc):** splitting specify/TDD/implement into other skills; fabrication marketplace; DSH/Pi adapters (deferred); moving product harness adapters into `.cursor/skills/fabrication/`.

<h2 id="document-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

**Part I — Fabrication (completed)**
1. [Phase 1 — Gate](#1-phase-1) — the three-zone kit exists.
2. [Phase 2 — Checkpoint log](#2-phase-2) — scripts append JSONL.
3. [Phase 3 — Roadmap viewer](#3-phase-3) — HTML from that log.
4. [Phase 4 — Skill package](#4-phase-4) — move the kit under the skill.
5. [Phase 5 — Paths and purity](#5-phase-5) — this repo and the copy use the skill directory.
6. [Quality bar (Part I)](#6-quality-bar) — tests, comments, docs.
7. [Deferred (Part I)](#7-deferred) — fabrication-only follow-ups.

**Part II — Harness adapters & shared MCP (completed)**
8. [Zones](#8-zones) — shared vs Hermes vs OpenClaw.
9. [Phase 6 — Shared MCP catalog](#9-phase-6) — one YAML for all harnesses.
10. [Phase 7 — Contract naming](#10-phase-7) — harness-neutral `harness/second-brain/`.
11. [Phase 8 — Hermes adapter templates](#11-phase-8) — move `docs/harness/` examples.
12. [Phase 9 — Hermes merge DRY](#12-phase-9) — catalog-driven `merge-hermes-wiring.py`.
13. [Phase 10 — Script layout](#13-phase-10) — `scripts/brain/adapters/hermes/`.
14. [Phase 11 — Stack dispatch](#14-phase-11) — `active_harness` + shared `messaging`.
15. [Phase 12 — OpenClaw skeleton](#15-phase-12) — templates + merge stub (schema TBD).
16. [Phase 13 — Docs and verify](#16-phase-13) — runbook, tests.
17. [Phase 14 — Runbook split + wrapper removal](#19-phase-14) — per-harness runbooks, canonical adapter paths.
18. [Quality bar (Part II)](#17-quality-bar-part-ii) — tests and non-goals.
19. [Deferred (Part II)](#18-deferred-part-ii) — OpenClaw live channels, etc.

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
<tr><td style="background:#e3f2fd">Live greenfield rehearsal</td><td style="background:#fff3e0">Same limit as the three-zone plan: a real ANALYZE creates a project</td><td style="background:#e8f5e9">after Part I</td><td>Copy the skill into an empty repo and run one ANALYZE-only prompt</td></tr>
</tbody>
</table>

---

<h2 id="part-ii-divider" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Part II — Harness adapters & shared MCP</h2>

**DRY principle:** `docs/harness/hermes-mcp.example.yaml` (`llm_wiki` + `second_brain_fs`) is **stack MCP**, not Hermes-only — only the envelope (`mcp_servers:` in `~/.hermes/config.yaml`) is Hermes. OpenClaw maps the **same catalog** into its config shape. **Do not** merge Telegram/WhatsApp into the shared MCP file (`platforms:` stays Hermes adapter; OpenClaw channels stay OpenClaw adapter).

---

<h2 id="8-zones" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. Zones</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Zone</th><th>Path</th><th>Holds</th><th>Must not hold</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Knowledge</td><td style="background:#e8f5e9"><code>brain/</code></td><td>raw, wiki, Nashsu project tree</td><td>Hermes/OpenClaw config</td></tr>
<tr><td style="background:#e3f2fd">Contract</td><td style="background:#e8f5e9"><code>harness/second-brain/</code></td><td><code>ingest-to-brain</code>, <code>query-brain</code>, <code>nashsu-mcp-read</code>, manifests</td><td>Harness install paths, <code>platforms:</code>, <code>~/.hermes</code> as sole truth</td></tr>
<tr><td style="background:#e3f2fd">Shared MCP catalog</td><td style="background:#fff3e0"><code>config/second-brain.mcp-servers.yaml</code></td><td>stdio MCP: <code>llm_wiki</code>, <code>second_brain_fs</code> (placeholders from brain-stack)</td><td>Telegram/WhatsApp, Hermes <code>external_dirs</code></td></tr>
<tr><td style="background:#e3f2fd">Adapter (Hermes)</td><td style="background:#fff3e0"><code>harness/adapters/hermes/</code> + <code>scripts/brain/adapters/hermes/</code></td><td><code>platforms:</code> examples; merge/start/messaging scripts</td><td>Duplicate contract skills</td></tr>
<tr><td style="background:#e3f2fd">Adapter (OpenClaw)</td><td style="background:#fff3e0"><code>harness/adapters/openclaw/</code> + <code>scripts/brain/adapters/openclaw/</code></td><td>Skill install README; channel/MCP template after schema confirmed</td><td>Second compiler, forked <code>brain/</code></td></tr>
<tr><td style="background:#e3f2fd">Stack</td><td style="background:#e8f5e9"><code>config/brain-stack.yaml</code></td><td><code>active_harness</code>, <code>llm_wiki</code>, <code>paths</code>, shared <code>messaging</code> key names</td><td>Committed secrets</td></tr>
</tbody>
</table>

---

<h2 id="9-phase-6" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">9. Phase 6 — Shared MCP catalog</h2>

- [X] Add `config/second-brain.mcp-servers.yaml` — **`llm_wiki`** (`node` + `${NU_LLM_WIKI_MCP}`, token env) and **`second_brain_fs`** (`npx` filesystem MCP + `${BRAIN_ROOT}`).
- [X] Extend `scripts/brain/brain_stack.py` to load the catalog with resolved paths.
- [X] Unit test: expanded catalog uses repo-relative paths, no hardcoded operator home dirs.

---

<h2 id="10-phase-7" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">10. Phase 7 — Contract naming</h2>

- [X] Update `harness/second-brain/README.md`: **Second Brain contract v1** (Hermes/OpenClaw = install targets for same skills).
- [X] Contract skills use MCP + filesystem only (no Hermes-only ingest/query APIs).
- [X] `merge-hermes-skills-config.py` keeps `external_dirs` → `harness/second-brain/skills`.

---

<h2 id="11-phase-8" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">11. Phase 8 — Hermes adapter templates</h2>

- [X] Create `harness/adapters/hermes/`.
- [X] Move `docs/harness/hermes-mcp.example.yaml` → `harness/adapters/hermes/mcp-servers.example.yaml` (pointer to canonical catalog + note: merged as `mcp_servers:` in `~/.hermes/config.yaml`).
- [X] Add `harness/adapters/hermes/platforms.example.yaml` (Telegram/WhatsApp `platforms:` shape; matches `merge-hermes-wiring.py`).
- [X] Remove or grep-clean old `docs/harness/hermes-mcp.example.yaml` (runbook links to catalog + adapters).

---

<h2 id="12-phase-9" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">12. Phase 9 — Hermes merge DRY</h2>

- [X] Refactor `merge-hermes-wiring.py` to emit `mcp_servers:` from **`config/second-brain.mcp-servers.yaml`** via `brain_stack.py` (drop duplicated f-string).
- [X] Unchanged: managed wiring markers, `platforms:` from env/preserve, target `~/.hermes/config.yaml`.
- [X] Update `tests/test_merge_hermes_wiring.py`.
- [X] PLAN/runbook links → `config/second-brain.mcp-servers.yaml`.

---

<h2 id="13-phase-10" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">13. Phase 10 — Script layout</h2>

- [X] Create `scripts/brain/adapters/hermes/`; move Hermes-only scripts (`setup-hermes*`, start/stop, merge-*, messaging).
- [X] Optional thin wrappers at old `scripts/brain/` paths for one release.
- [X] Shared at `scripts/brain/`: `brain_stack.py`, `apply-stack-config.sh`, `sync-llm-wiki-token.sh`, `ingest.sh`, `backup.sh`, `mcp-smoke-read.sh`, `setup-local.sh`.

---

<h2 id="14-phase-11" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">14. Phase 11 — Stack dispatch</h2>

- [X] Extend `config/brain-stack.example.yaml`: **`active_harness`** (`hermes` | `openclaw`), top-level **`messaging`** (dedupe Telegram/WhatsApp keys from `hermes.sync_env_keys`), harness-specific subsections.
- [X] `apply-stack-config.sh` dispatches to `adapters/hermes/*` or `adapters/openclaw/*`.
- [X] Extend `tests/test_brain_stack_config.py`.

---

<h2 id="15-phase-12" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">15. Phase 12 — OpenClaw skeleton</h2>

- [X] `harness/adapters/openclaw/README.md` — contract skill install paths; link architecture §8.
- [X] Placeholder **`openclaw-config.example.yaml`** (or `.json` — rename after upstream schema validated).
- [X] Stub `scripts/brain/adapters/openclaw/merge-openclaw-wiring` — loads shared MCP catalog; channel merge blocked until schema known.
- [X] No “live OpenClaw TG/WA” checkbox in this plan.

---

<h2 id="16-phase-13" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">16. Phase 13 — Docs and verify</h2>

- [X] `SECOND_BRAIN_RUNBOOK.md`: Hermes vs OpenClaw subsections; shared MCP catalog section.
- [X] `PLAN_SECOND_BRAIN_HERMES_V1.md` §13 → Part II of this file for adapter layout.
- [X] `./scripts/verify.sh` green after Hermes script moves (wrappers OK).

---

<h2 id="19-phase-14" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">17. Phase 14 — Runbook split + wrapper removal</h2>

**TDD mode:** smoke-after-delete (remove wrappers) + **`tests/test_brain_script_layout.py`** (no Hermes shim files at `scripts/brain/` root).

- [X] **`SECOND_BRAIN_RUNBOOK.md`** — hub only (corpus, LLM Wiki, shared MCP, `setup-local`, verify); link per-harness runbooks.
- [X] **`RUNBOOK_HARNESS_HERMES.md`** — P3–P4, Desktop, smoke, messaging (content moved from hub §10 / §16).
- [X] **`RUNBOOK_HARNESS_OPENCLAW.md`** — same phase checklist; TBD steps marked (skeleton).
- [X] **`setup-local.sh`** → **`scripts/brain/adapters/<active_harness>/setup-harness.sh`** (shared stack steps stay in hub script).
- [X] Remove thin **`scripts/brain/setup-hermes*`** / **`start|stop-hermes`** / **`merge-hermes-*`** / **`hermes-*`** wrappers; canonical paths under **`adapters/hermes/`**.
- [X] Move **`smoke-integrated.sh`** / **`acceptance-automated.sh`** under **`adapters/hermes/`** if Hermes-only; update runbook links.
- [X] Grep repo for old wrapper paths; **`./scripts/verify.sh`** green.

---

<h2 id="17-quality-bar-part-ii" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">17. Quality bar (Part II)</h2>

<h3 id="17-1-tests" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">17.1 Tests</h3>

- Catalog load (phase 6); `merge-hermes-wiring` regression (phase 9); `brain_stack` dispatch (phase 11). No OpenClaw in CI (phase 12 stub).

<h3 id="17-2-non-goals" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">17.2 Non-goals</h3>

- Duplicate contract skills per adapter; Nashsu/`brain/` layout changes; shared YAML merge library until OpenClaw merge is real.

---

<h2 id="18-deferred-part-ii" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">18. Deferred (Part II)</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Item</th><th>Reason</th><th>Handling</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">OpenClaw live Telegram/WhatsApp</td><td style="background:#fff3e0">Channel schema TBD</td><td style="background:#e8f5e9">After phase 12 validation; same <code>messaging</code> env as Hermes</td></tr>
<tr><td style="background:#e3f2fd">DSH / Pi adapters</td><td style="background:#fff3e0">Not first swap target</td><td style="background:#fff3e0">Copy adapter pattern later</td></tr>
<tr><td style="background:#e3f2fd">Shared merge helper library</td><td style="background:#fff3e0">Only two merges today</td><td style="background:#fff3e0">Extract when OpenClaw merge ships</td></tr>
</tbody>
</table>
