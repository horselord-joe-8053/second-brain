<h1 id="bootstrap-kit-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Web app bootstrap kit</h1>

One app per workspace: embedded kit matches that app only.

## Document outline

1. [Layout](#layout)
2. [How to use](#how)
3. [Adding another app](#another-app)

---

<h2 id="layout" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Layout</h2>

| Path | Role |
|------|------|
| **`app_agnostic/`** | Harness (incl. **`.cursor/rules/`**, **`check-ac-tests.py`**), scripts, templates, **`bootstrap_webapp.md`** (factory phase 1 + product phase 2) |
| **`app_specific/`** | This app only: **`bootstrap.md`** (kit meta + mission/tickets), **`specs/*.md`** (seeded to `docs/specs/`), **`plans/*.md`** (seeded to `docs/plans/`; authored by ANALYZE, not stored in the harness) |
| **`utils/`** | Portable helpers copied to the **project root** `utils/` by **`seed-utils.sh`** when that directory is absent (`neat_logger`, `neat_logger_ts`, `playwright_e2e`, and the rest of the tree) |

---

<h2 id="how" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. How to use</h2>

**Prompts:**

| Goal | Tell the agent |
|------|----------------|
| Bootstrap only ( **`app_specific/`** already filled ) | Run **`bootstrap_webapp/EXECUTE_GEN.md`** |
| Author **`app_specific/`** from a brief | Run **`bootstrap_webapp/ANALYZE_APP_SPECIFIC.md for the following app: …`** |
| Greenfield: spec + bootstrap | Run **`bootstrap_webapp/EXECUTE_GEN.md for the following app: …`** (ANALYZE then EXECUTE) |

Manual steps (same flow as EXECUTE):

1. Copy **`bootstrap_webapp/`** into the app repo (or keep beside root).
2. Agent: **`app_agnostic/bootstrap_webapp.md`** — **Part A** through **STOP** (§A6).
3. After **`./scripts/verify.sh` green:** read **`app_specific/bootstrap.md`**, continue **Part B** in the same file.

**Seed product spec and plans:** `bash app_agnostic/scripts/seed-product.sh <repo-root>` (copies `app_specific/specs/` → `docs/specs/` and `app_specific/plans/` → `docs/plans/`).

**Seed utils:** `bash app_agnostic/scripts/seed-utils.sh <repo-root>` — copies this kit’s `utils/` to `<repo-root>/utils` only when the project root does not already have `utils/`.

**TDD gate (from phase 1):** `scripts/check-ac-tests.py` + **`<!-- ac-tests: enforced -->`** on product specs → matching **`test_ac_*`** tests required before merge (`verify.sh`).

---

<h2 id="another-app" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Adding another app</h2>

Use a **separate repo or branch** with its own embedded kit: replace **`app_specific/`** (bootstrap + specs). Do not put product specs in **`app_agnostic/harness/`**.
