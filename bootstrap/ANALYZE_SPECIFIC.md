<h1 id="analyze-specific" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Analyze and author `specific/`</h1>

Author **`KIT/specific/bootstrap.md`**, **`specs/`**, **`plans/`** only (unless human asks to implement).

## Route by product shape

| Shape | Follow |
|-------|--------|
| **Web app** (FastAPI + React MVP) | **`modules/webapp/ANALYZE_WEBAPP.md`** — set **`profile: webapp`** in bootstrap meta |
| **General / Second Brain / infra** | Sections below — **`profile: general`** |
| **`implementing docs/PLAN_*.md`** | **`modules/second-brain/ANALYZE_FROM_PLAN.md`** (or use pre-seeded **`specific/`** when **`plan_source`** matches) |

## Meta (`specific/bootstrap.md`)

```text
profile: general | webapp
phase1_modules: kit-utils   # webapp factory often needs this after harness
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
