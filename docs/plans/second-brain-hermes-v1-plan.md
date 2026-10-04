# Plan: second-brain-hermes-v1

<!-- delivery-status: wip -->
<!-- plan-for: docs/specs/second-brain-hermes-v1.md -->

Source: **`docs/PLAN_SECOND_BRAIN_HERMES_V1.md`**

**Progress:** First open **`[ ]`** is the resume point (currently **P2 — HG-2 closed**).

## Spec link

`docs/specs/second-brain-hermes-v1.md`

---

### [X] P1 — Repo corpus (plan §5)

- **ACs:** SB1, SB2
- **Exit:** `./scripts/verify.sh` green; `./scripts/verify-local.sh` green
- **Depends:** phase 1 harness seeded

**Execution checklist**

- [X] `brain/` tree matches plan §5 (raw/sources channels, wiki, manifests, `purpose.md`, gitignore policy)
- [X] Root README links plan, architecture, runbook, bootstrap usage (AC-SB2)
- [X] Pytest AC-SB1 / SB2 seams present and passing when Python available
- [X] `./scripts/verify.sh` and `./scripts/verify-local.sh` green
- [X] Spec **Decisions** records P1 completion

---

### P2 — Nashsu LLM Wiki (plan §6)

- **HG-2** — desktop-install module; stop until human confirms ingest smoke
- **Exit:** Human recorded in Decisions; API token location documented (not in repo)

**Execution checklist**

- [X] Sibling `nu_llm_wiki` dev build; API `127.0.0.1:19828` reachable
- [X] LLM provider keys/models in app Settings → LLM (not repo `.env`)
- [X] Settings → API + MCP enabled; operator bearer in local `.env` as `LLM_WIKI_API_TOKEN` (gitignored)
- [X] Native app **Open project** → `…/second_brain/brain`
- [X] Source Watch auto-ingest enabled for uploads (and ingest tip documented in runbook)
- [X] `smoke-test.md` and sample uploads produced wiki pages under `brain/wiki/` (not only `index.md`)
- [X] `docs/SECOND_BRAIN_RUNBOOK.md` §5–§9 covers HG-2, embeddings, MCP, query path
- [ ] Human confirms **HG-2 closed** (reply or **Decisions** line explicitly marking HG-2 complete)
- [ ] Phase **Exit** verified and **Decisions** updated for HG-2 closure

---

### P3 — Hermes harness (plan §7)

- **HG-3**
- **Exit:** `hermes doctor` reported clean (human confirmation)

**Execution checklist**

- [ ] Hermes CLI installed per runbook §10
- [ ] `hermes doctor` clean (human confirmation)
- [ ] Spec **Decisions** records HG-3

---

### P4 — Wire harness ↔ compiler (plan §8)

- **HG-4**; repo may add `docs/harness/hermes-mcp.example.yaml`
- **Exit:** MCP smoke described in Decisions

**Execution checklist**

- [X] Repo documents `docs/harness/hermes-mcp.example.yaml` (template paths)
- [ ] `~/.hermes/config.yaml` includes Nashsu MCP + `LLM_WIKI_API_TOKEN` env
- [ ] Hermes bundled `llm-wiki` compiler skill disabled; Nashsu skill installed
- [ ] MCP smoke (search or read) recorded in **Decisions**
- [ ] Phase **Exit** verified

---

### P5 — Obsidian (plan §9)

- **HG-5**
- **Exit:** vault path recorded in Decisions

**Execution checklist**

- [ ] Obsidian vault opened on compiled wiki root (`brain/wiki/` or project root per plan)
- [ ] Spec **Decisions** records vault path (HG-5)

---

### P6 — Ingestion workflows (plan §10)

- **ACs:** SB6
- **Exit:** `./scripts/verify.sh` green

**Execution checklist**

- [ ] `harness/second-brain/` ingest skill doc + manifest example (AC-SB6)
- [ ] Optional `scripts/brain/ingest.sh` if plan requires
- [ ] Pytest AC-SB6 green; `./scripts/verify.sh` green
- [ ] Spec **Decisions** updated if needed

---

### P7 — Backup and ops (plan §11)

- **ACs:** SB7
- **Exit:** `./scripts/verify.sh` green

**Execution checklist**

- [ ] `scripts/brain/backup.sh` or equivalent rsync/zip stub (AC-SB7)
- [ ] Backup steps documented in plan exit / runbook
- [ ] Pytest AC-SB7 green; `./scripts/verify.sh` green

---

### P8 — Acceptance (plan §12)

- **HG-8** manual checklist
- **Exit:** Decisions log + waiver or pass notes

**Execution checklist**

- [ ] Human runs architecture acceptance checklist with apps running
- [ ] Pass or waiver recorded in **Decisions**
- [ ] Set plan **`<!-- delivery-status: completed -->`**; optional copy to `docs/plans/completed/`

## Agent notes

- **Start / resume:** `Run bootstrap/EXECUTE_GEN.md implementing docs/PLAN_SECOND_BRAIN_HERMES_V1.md` or **`delivery-resumimpl docs/plans/second-brain-hermes-v1-plan.md`**
- Rule: **`.cursor/rules/delivery-resumimpl.mdc`**
