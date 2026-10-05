# Plan: second-brain-hermes-v1

<!-- delivery-status: wip -->
<!-- plan-for: docs/specs/second-brain-hermes-v1.md -->

Source: **`docs_manual_gen/PLAN_SECOND_BRAIN_HERMES_V1.md`**

**Progress:** First open **`[ ]`** is the resume point (currently **P5 Obsidian HG-5** + **P8 acceptance**; sync with repo `docs/plans/`).

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

### [X] P2 — LLM Wiki (plan §6)

- **HG-2** — desktop-install module; stop until human confirms ingest smoke
- **Exit:** Human recorded in Decisions; API token location documented (not in repo)

**Execution checklist**

- [X] Sibling `nu_llm_wiki` dev build; API `127.0.0.1:19828` reachable
- [X] LLM provider keys/models in app Settings → LLM (not repo `.env`)
- [X] Settings → API + MCP enabled; operator bearer in local `.env` as `LLM_WIKI_API_TOKEN` (gitignored)
- [X] Native app **Open project** → `…/second_brain/brain`
- [X] Source Watch auto-ingest enabled for uploads (and ingest tip documented in runbook)
- [X] `smoke-test.md` and sample uploads produced wiki pages under `brain/wiki/` (not only `index.md`)
- [X] `docs_manual_gen/SECOND_BRAIN_RUNBOOK.md` §5–§9 covers HG-2, embeddings, MCP, query path
- [X] `docs_manual_gen/MORE_SECOND_BRAIN_QUERY_HERMES_MCP.md` documents L1/L2/L3, MCP vs Agent tools, **Known gaps / Nashsu backlog** (§9–§10)
- [X] Human confirms **HG-2 closed** (reply or **Decisions** line explicitly marking HG-2 complete)
- [X] Phase **Exit** verified and **Decisions** updated for HG-2 closure

---

### [X] P3 — Hermes harness (plan §7)

- **HG-3**
- **Exit:** `hermes doctor` reported clean (human confirmation)

**Execution checklist**

- [X] Runbook §10 + `scripts/brain/setup-hermes.sh` / `setup-local.sh` (idempotent install + doctor)
- [X] Hermes CLI installed (`./scripts/brain/setup-hermes.sh` exits 0)
- [X] `hermes doctor` exit 0 (2026-10-04; advisories — optional `hermes setup` / `doctor --fix`)
- [X] Spec **Decisions** records HG-3

---

### [X] P4 — Wire harness ↔ compiler (plan §8)

- **HG-4**; repo may add `docs/harness/hermes-mcp.example.yaml`
- **Exit:** MCP smoke described in Decisions

**Execution checklist**

- [X] Repo documents `docs/harness/hermes-mcp.example.yaml` (template paths)
- [X] `~/.hermes/config.yaml` includes LLM Wiki MCP (`setup-hermes-mcp.sh` / `${LLM_WIKI_API_TOKEN}` in `~/.hermes/.env`)
- [X] `second_brain/.env` + `~/.hermes/.env` synced from LLM Wiki `app-state.json` (`sync-llm-wiki-token.sh`)
- [X] MCP smoke: API health + `hermes mcp test llm_wiki` + hybrid search on `projects/current` (2026-10-05)
- [X] Bundled **`llm-wiki`** disabled via `skills.disabled` + repo **`external_dirs`** (`setup-hermes-skills.sh`); hub Nashsu install blocked by skills-guard — **`nashsu-mcp-read`** repo skill substitute
- [X] MCP read smoke: `mcp-smoke-read.sh` on `wiki/sources/7-uploads--10-smoke-test--1dwb8eh.md` (2026-10-05)
- [X] Phase **Exit** verified and **Decisions** updated

---

### P5 — Obsidian (plan §9)

- **HG-5**
- **Exit:** vault path recorded in Decisions

**Execution checklist**

- [X] Obsidian installed via `./scripts/brain/setup-obsidian.sh` (brew cask; part of `setup-local.sh`)
- [ ] Obsidian vault opened on **`brain/wiki/`** (`OPEN_OBSIDIAN_VAULT=1 ./scripts/brain/setup-obsidian.sh` or manual)
- [ ] Spec **Decisions** records vault path (HG-5)

---

### [X] P6 — Ingestion workflows (plan §10)

- **ACs:** SB6
- **Exit:** `./scripts/verify.sh` green

**Execution checklist**

- [X] `harness/second-brain/skills/ingest-to-brain/SKILL.md` + `manifests/example-ingest.yaml` (AC-SB6)
- [X] `harness/second-brain/skills/query-brain/SKILL.md` — Pattern A/B, L2 escalation, cite-or-abstain (MORE §10 **G6**)
- [X] `scripts/brain/ingest.sh` helper
- [X] Pytest AC-SB6 green; `./scripts/verify.sh` green
- [X] Spec **Decisions** updated

---

### [X] P7 — Backup and ops (plan §11)

- **ACs:** SB7
- **Exit:** `./scripts/verify.sh` green

**Execution checklist**

- [X] `scripts/brain/backup.sh` rsync stub (AC-SB7)
- [X] Backup documented in runbook §12
- [X] Pytest AC-SB7 green; `./scripts/verify.sh` green

---

### P8 — Acceptance (plan §12)

- **HG-8** manual checklist
- **Exit:** Decisions log + waiver or pass notes

**Execution checklist**

- [ ] Human runs [`docs/ACCEPTANCE-second-brain-hermes-v1.md`](ACCEPTANCE-second-brain-hermes-v1.md) with apps running
- [ ] Pass or waiver recorded in **Decisions**
- [ ] Set plan **`<!-- delivery-status: completed -->`**; optional copy to `docs/plans/completed/`
- [ ] **NB-SB1:** Table/spreadsheet lookup test — answer cites **L2** (`.cache/*.txt`) or **L3** wiki path; no uncited parametric fill (MORE §10)

---

## Query fidelity — Nashsu backlog (non-blocking for P3)

**Detail:** [`docs_manual_gen/MORE_SECOND_BRAIN_QUERY_HERMES_MCP.md`](../docs_manual_gen/MORE_SECOND_BRAIN_QUERY_HERMES_MCP.md) §9–§10 (verified against sibling `nu_llm_wiki`).

**Do not** delay Hermes install (P3) or MCP wiring (P4) on upstream **NB-*** items. Track them for spreadsheet / evidence-bound Q&A quality.

| ID | Track | Owner | Plan hook |
|----|-------|-------|-----------|
| G1–G8 | Known gaps (today) | Nashsu + SB skill | MORE §10.1 |
| NB-1 | L2 hybrid passage search | Nashsu | Optional spike after P4 |
| NB-2 | Full-table ingest / L2 link in wiki | Nashsu | Re-ingest when available |
| NB-3 | Evidence-required agent mode | Nashsu | Complements SB cite-or-abstain |
| NB-4 | MCP/API raw or L2 search | Nashsu | Simplifies Hermes Pattern A |
| NB-5 | Agent vs MCP tool naming docs | Nashsu | Integrator clarity |
| NB-SB1 | Acceptance: cited table lookup | SB | P8 checklist |

**Optional P2 operator setting:** LLM Wiki **Settings → Multilingual** output language when corpus is bilingual (helps L3; does not fix G2/G4).

**Spike (optional, post-P4):** Same question via **`llm_wiki_chat`** vs MCP **search+read** — log in **Decisions** (MORE §11).

## Agent notes

- **Start / resume:** `Run bootstrap/EXECUTE_GEN.md implementing docs_manual_gen/PLAN_SECOND_BRAIN_HERMES_V1.md` or **`delivery-resumimpl docs/plans/second-brain-hermes-v1-plan.md`**
- Rule: **`.cursor/rules/delivery-resumimpl.mdc`**
