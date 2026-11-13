---
name: fabrication
description: >-
  Bootstrap a repo from a read-only kit. In chat, say Run .cursor/skills/fabrication/references/EXECUTE_GEN.md
  on or implementing a brief or plan. Agent reads EXECUTE_GEN; writes seed_grow/ and product only.
---

# Fabrication

**Read-only:** `.cursor/skills/fabrication/` — never edit this tree during a run.

## How to use (in Cursor chat)

Say one of these from the **repo root** (this project or any repo that has the skill + `seed_grow/`):

| Goal | Prompt |
|------|--------|
| **New project brief** | `Run .cursor/skills/fabrication/references/EXECUTE_GEN.md implementing <path-to-description.md>` |
| **Same, inline brief** | `Run .cursor/skills/fabrication/references/EXECUTE_GEN.md for the following project: …` |
| **Web app** | `Run .cursor/skills/fabrication/references/EXECUTE_GEN.md profile: webapp for …` |
| **Resume delivery** | `delivery-resumimpl seed_grow/plans/<feature>-plan.md` |

The agent follows **[`references/EXECUTE_GEN.md`](references/EXECUTE_GEN.md)** (analyze → phase 1 harness → verify gate → phase 2 product). Progress checklists live in **`seed_grow/plans/*-plan.md`**.

**Second Brain (this repo):**  
`Run .cursor/skills/fabrication/references/EXECUTE_GEN.md implementing docs_manual_gen/PLAN_SECOND_BRAIN_HERMES_V1.md`  
or **`delivery-resumimpl seed_grow/plans/second-brain-hermes-v1-plan.md`**.

**Scripts (agent/shell):** `bash .cursor/skills/fabrication/scripts/seed-harness.sh`, `apply-module.sh`, `seed-product.sh`, `check-seed-kit.sh`. Checkpoint log → **`seed_grow/progress.jsonl`**; open **`seed_grow/roadmap.html`** after runs.

**Other machine:** copy this folder to **`~/.cursor/skills/fabrication/`** (same layout).
