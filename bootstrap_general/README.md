<h1 id="bootstrap-general-kit" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">General project bootstrap kit</h1>

Same **workflow essence** as `bootstrap_webapp/`: **ANALYZE → phased specs/plans under `docs/` → ticketed IMPLEMENT → `./scripts/verify.sh`**.  
**Without** mandatory FastAPI/React scaffold or **UI-CHOOSE**.

## Document outline

1. [Layout](#layout)
2. [vs webapp kit](#vs-webapp)
3. [How to use](#how)
4. [Second Brain example](#second-brain)

---

<h2 id="layout" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Layout</h2>

| Path | Role |
|------|------|
| **`project_agnostic/`** | Harness, scripts, `bootstrap_general.md` |
| **`project_specific/`** | Filled by ANALYZE: `bootstrap.md`, `specs/`, `plans/` |
| **`EXECUTE_GEN.md`** | Single entry (phase 1 harness + phase 2 delivery) |
| **`ANALYZE_PROJECT_SPECIFIC.md`** | Author `project_specific/` from a brief or `docs/PLAN_*.md` |

Shared skills (not webapp-only): **`align-requirements`**, **`specify-feature`**, **`implement-feature`**, **`debug`**.

---

<h2 id="vs-webapp" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. vs webapp kit</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Aspect</th><th>bootstrap_webapp</th><th>bootstrap_general</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Phase 1</td><td>FastAPI + React + UI factory</td><td>Harness + verify scripts only</td></tr>
<tr><td style="background:#e3f2fd">TDD doc</td><td>WEBAPP-TDD.md</td><td>PROJECT-TDD.md</td></tr>
<tr><td style="background:#e3f2fd">UI-CHOOSE</td><td>Required for substantial UI</td><td>Not included</td></tr>
<tr><td style="background:#e3f2fd">Human gates</td><td>Mostly LLM_API_KEY</td><td><strong>HG-*</strong> in specs (installs, OAuth)</td></tr>
<tr><td style="background:#e3f2fd">Kit folder</td><td>app_specific/</td><td>project_specific/</td></tr>
</tbody>
</table>

---

<h2 id="how" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. How to use</h2>

| Goal | Prompt |
|------|--------|
| Author kit from brief | `Run bootstrap_general/ANALYZE_PROJECT_SPECIFIC.md for the following project: …` |
| Full greenfield | `Run bootstrap_general/EXECUTE_GEN.md for the following project: …` |
| Execute existing plan | `Run bootstrap_general/EXECUTE_GEN.md implementing docs/PLAN_SECOND_BRAIN_HERMES_V1.md` |

Agent should **pause with instructions** on **HG-*** steps only.

---

<h2 id="second-brain" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Second Brain example</h2>

Use **`docs/PLAN_SECOND_BRAIN_HERMES_V1.md`** + **`docs/second-brain-llm-wiki-architecture.md`** as ANALYZE inputs. Phase 2 implements in-repo work (`brain/`, `harness/`, scripts); Hermes / LLM Wiki / Obsidian installs stay **HG-*** gates.
