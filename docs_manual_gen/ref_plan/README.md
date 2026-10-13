<h1 id="ref-plan-index" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Refactor plans (second_brain / retail)</h1>

**Layout:** same lifecycle as `cursor_gen/refactor_plans/` — **`new/`** (not started), **`wip/`** (partial), **`completed/`** (done).

Retail and Samsung service-brain plans live here instead of scattered under `docs_manual_gen/REFACTOR_*.md` or duplicate `cursor_gen/refactor_plans/` copies.

| Folder | Use |
|--------|-----|
| [`new/`](./new/) | **`onlyref`** — all implementable items **`[ ]`**. |
| [`wip/`](./wip/) | **`implref`** / **`resumimpl`** — some **`[X]`**, not finished. |
| [`completed/`](./completed/) | All implementable phases **`[X]`** (or waived). |

**Execute:** `qimpltdd docs_manual_gen/ref_plan/new/REFACTOR_….md` (or **`wip/`** path when resuming).

**Article (not a plan):** [`../artifacts/ABOUT_SEARCH_RRF.md`](../artifacts/ABOUT_SEARCH_RRF.md).

**Legacy pointer:** `cursor_gen/refactor_plans/` may hold stubs; canonical retail plans are under this tree.
