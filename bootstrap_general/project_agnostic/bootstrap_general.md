<h1 id="bootstrap-general-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Bootstrap prompt: general project (phase 1 + phase 2)</h1>

**Kit path:** `bootstrap_general/project_agnostic/` (`harness/`, `scripts/`, `templates/`, this file).

<h3 id="agent-instructions" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">For the coding agent</h3>

1. **Read this file.** **`AGNOSTIC`** = `bootstrap_general/project_agnostic/`. **`KIT`** = `bootstrap_general/`.
2. **Workspace** = project repo root (parent of **`bootstrap_general/`**).
3. **Part A (phase 1):** project harness + verify scripts — **not** a FastAPI/React scaffold.
4. **STOP after §A4** until `./scripts/verify.sh` passes (may be trivial on empty repo).
5. **Part B (phase 2):** read **`project_specific/bootstrap.md`**, seed specs/plans, implement tickets in delivery-phase order.

## Document outline

**Part A — factory (phase 1)**  
A1. [Mission](#a-mission)  
A2. [Agent-run setup](#a-setup)  
A3. [Scaffold harness](#a-scaffold)  
A4. [Done / STOP](#a-done)

**Part B — product / system (phase 2)**  
B1. [Mission](#b-mission)  
B2. [Spec and glossary](#b-spec)  
B3. [Tickets](#b-tickets)  
B4. [Implementation](#b-implement)  
B5. [Done](#b-done)

---

<h2 id="a-mission" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">A1. Mission (phase 1)</h2>

Git-ready **process harness**: `docs/specs/`, `docs/plans/`, `AGENTS.md`, agent skills, `./scripts/verify.sh`, optional `utils/` copy. **No default webapp.**

---

<h2 id="a-setup" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">A2. Agent-run setup</h2>

| Step | Command |
|------|---------|
| Skills (optional npm) | `bash "$AGNOSTIC/scripts/install-agent-skills.sh" <repo-root>` |
| Utils (if repo has no `utils/`) | `bash "$AGNOSTIC/scripts/seed-utils.sh" <repo-root>` |

No `backend/.env` unless a spec later requires a web stack.

---

<h2 id="a-scaffold" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">A3. Scaffold harness</h2>

```bash
bash "$AGNOSTIC/scripts/seed-harness.sh" <repo-root> "<Project Name>" "<One-line description>"
bash "$AGNOSTIC/scripts/seed-scaffold-scripts.sh" <repo-root>
```

Update root **`README.md`** to point at `docs/PRODUCT.md` and `AGENTS.md`.

---

<h2 id="a-done" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">A4. Done / STOP (phase 1)</h2>

- [ ] `./scripts/verify.sh` passes (may only run check-ac-tests skip until specs exist)
- [ ] `docs/PROJECT-TDD.md`, `.agents/skills/*`, `.cursor/rules/tdd-ac-enforcement.mdc` present

**STOP.** Read **`project_specific/bootstrap.md`** before Part B.

---

<h2 id="b-mission" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">B1. Mission (phase 2)</h2>

Deliver the work described in **`project_specific/bootstrap.md`** and seeded **`docs/specs/`** + **`docs/plans/`**, in delivery-phase order. Respect **human gates** (`HG-*`) for external tools.

---

<h2 id="b-spec" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">B2. Spec and glossary</h2>

```bash
bash "$AGNOSTIC/scripts/seed-product.sh" "$REPO_ROOT"
```

Update **`GLOSSARY.md`**, **`docs/PRODUCT.md`**, **`docs/ARCHITECTURE.md`**, **`AGENTS.md`** per bootstrap **Glossary / AGENTS**.

---

<h2 id="b-tickets" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">B3. Tickets</h2>

Use **Ticket slices** in `project_specific/bootstrap.md`. Same **`P1` / `P2`** order as the plan. **No mandatory UI-CHOOSE.** Pause on **HG-*** until the human confirms.

---

<h2 id="b-implement" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">B4. Implementation</h2>

**`implement-feature` skill:** per AC, red → green when `<!-- ac-tests: enforced -->`. Shell/docs/infra work uses plan **Exit** commands. External installs (Hermes, LLM Wiki app, Obsidian) = **HG-*** with explicit instructions — never commit secrets.

Optional: add `scripts/verify-local.sh` for project-specific smoke (e.g. corpus layout, config syntax).

---

<h2 id="b-done" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">B5. Done (phase 2)</h2>

- [ ] All delivery phases exited per plan
- [ ] `./scripts/verify.sh` green
- [ ] README updated (**done_display_name** from kit meta)
