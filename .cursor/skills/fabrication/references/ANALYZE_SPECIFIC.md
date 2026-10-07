<h1 id="analyze-specific" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Analyze and author <code>seed_grow/</code></h1>

Author **`seed_grow/bootstrap.md`**, **`seed_grow/specs/`**, **`seed_grow/plans/`** only (unless human asks to implement). **Do not** create or edit files under **`.cursor/skills/fabrication/`** (kit is read-only).

## Route by product shape

| Shape | Follow |
|-------|--------|
| **Web app** (FastAPI + React MVP) | **`modules/webapp/ANALYZE_WEBAPP.md`** — set **`profile: webapp`** in bootstrap meta |
| **General / infra** | Sections below — **`profile: general`** |
| **`implementing <project general description file path>`** | **`ANALYZE_SPECIFIC.md`** (this file) |

## Meta (`seed_grow/bootstrap.md`)

```text
profile: general | webapp
phase1_modules: kit-utils
phase2_modules: logging-neat, ui-choose, desktop-install
feature_id: …
spec_file: …
plan_file: …
env_append: none
done_display_name: …
```

Tag plan phases with `<!-- module: … -->` when a capability applies to one slice only.

**General:** use **`core/harness/docs/templates/feature-spec.md`** + **`human-gate.md`**.  
**Webapp:** use **`modules/webapp/harness/docs/templates/feature-spec.md`** (via ANALYZE_WEBAPP).

Validate: **`core/scripts/seed-product.sh`** after phase 1 harness exists.

**Success:** after `seed_grow/` artifacts are written, run **`bash .cursor/skills/fabrication/scripts/append-checkpoint.sh <repo-root> analyze done analyze`** (or **`.cursor/skills/fabrication/scripts/append-checkpoint.sh`** after the kit move). Repeatable — each analyze appends a new line.
