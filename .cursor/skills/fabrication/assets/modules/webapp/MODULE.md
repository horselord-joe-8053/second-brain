<h1 id="mod-webapp" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Module: webapp</h1>

**When:** `profile: webapp` in **`specific/bootstrap.md`** (or human **`EXECUTE_GEN … profile: webapp`**).

**Canonical procedure:** **`bootstrap-webapp.md`** in this folder (Part A factory + Part B product). **`bootstrap-core.md`** delegates here when profile is webapp.

**Applied by scripts:** `seed-harness.sh … webapp` → `apply-module.sh webapp` (WEBAPP-TDD, ui-factory, homepage waiver, web spec templates, ui-choose-look, web implement-feature). `seed-scaffold-scripts.sh … webapp` → factory **verify.sh** / **dev.sh** / **check-ac-tests.py**.

**Typical phase 1 modules:** `kit-utils`, then agent builds `backend/` + `frontend/` per **bootstrap-webapp.md §A3–A5**.

**Phase 2 add-ons:** `logging-neat`, `ui-choose` (see module list in **`.cursor/skills/fabrication/references/README.md`**).
