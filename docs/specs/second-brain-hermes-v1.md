# Feature: Second Brain Hermes v1

<!-- ac-tests: enforced -->
<!-- delivery-phase: P1 P6 P7 -->
<!-- plan: docs/plans/second-brain-hermes-v1-plan.md -->

## Goal

Implement in-repo Second Brain foundation per **`docs_manual_gen/PLAN_SECOND_BRAIN_HERMES_V1.md`** and **`docs_manual_gen/second-brain-llm-wiki-architecture.md`**: corpus tree, harness contract, backup scripts; external tools via human gates.

## Constraints

- Topology A (Mac): Hermes and LLM Wiki co-located; API `127.0.0.1:19828`.
- No custom wiki compiler in this repo; no Hermes bundled compiler skill active.
- Secrets only in `~/.hermes`, LLM Wiki UI — never committed.

## Acceptance criteria (behavior)

1. **AC-SB1:** (P1) `brain/` tree matches plan §5 (raw/sources channels, wiki, manifests, purpose.md, .gitignore policy).
2. **AC-SB2:** (P1) Root README links plan, architecture, and bootstrap usage.
3. **AC-SB6:** (P6) `harness/second-brain/` with ingest skill doc + manifest example; optional `scripts/brain/ingest.sh`.
4. **AC-SB7:** (P7) Backup script documented in plan exit; `scripts/brain/backup.sh` or equivalent rsync/zip stub.

## Human gates

1. **HG-2:** (P2) Human installs LLM Wiki, opens project at repo `brain/`, enables API/MCP, first ingest — agent provides OS-specific steps via **desktop-install**.
2. **HG-3:** (P3) Run `./scripts/brain/setup-local.sh` (or `setup-hermes.sh`); `hermes doctor` exit 0 — then `hermes setup` for API keys as needed.
3. **HG-4:** (P4) Human configures `~/.hermes/config.yaml` MCP + disables bundled llm-wiki skill; agent supplies template paths from repo docs.
4. **HG-5:** (P5) Human opens Obsidian vault on wiki root.
5. **HG-8:** (P8) Human runs architecture acceptance tests with apps running; agent supplies checklist.

## Out of scope

VPS Topology B, Telegram gateway (optional later), webapp UI.

## Test seams

| ID | Phase | Seam | Verification |
|----|-------|------|----------------|
| SB1 | P1 | pytest | `test_ac_sb1_brain_layout` |
| SB2 | P1 | pytest | `test_ac_sb2_readme_links` |
| SB6 | P6 | pytest | `test_ac_sb6_ingest_harness` |
| SB7 | P7 | pytest | `test_ac_sb7_backup_script` |
| HG-* | P2–P5,P8 | human | Decisions |

Implement per **`docs/PROJECT-TDD.md`**.

## Decisions

- **P1 (2026-10-03):** Repo corpus layout, harness stub README, root README, verify scripts seeded. Pytest/check-ac-tests skipped locally when `python3` unavailable (Xcode CLT not installed).
- **HG-2 source build (2026-10-03):** `nu_llm_wiki` sibling repo; CLT; `tauri dev` — API `127.0.0.1:19828`.
- **HG-2 GUI (2026-10-03):** LLM provider keys/models in app Settings → LLM; API + MCP enabled; bearer in operator `.env` as `LLM_WIKI_API_TOKEN`. Runbook §5–§7. API `GET /projects` → 200.
- **HG-2 smoke (2026-10-03):** `brain/raw/sources/uploads/smoke-test.md` added; `brain/wiki/index.md` seeded. Native app **Open project → `second_brain/brain`** with Source Watch; uploads and smoke produced compiled pages under `brain/wiki/` (not only `index.md`).
- **HG-2 fork (2026-10-04):** Sibling compiler repo pushes to `git@github.com:horselord-joe-8053/llm-wiki.git`; runbook §4 updated. Optional `upstream` remote for upstream merges.
- **HG-2 closed (2026-10-04):** Human confirmed ingest smoke complete. P2 exit: API/MCP enabled; operator bearer in gitignored `.env` as `LLM_WIKI_API_TOKEN` (not in repo). Query/read path documented in `docs_manual_gen/MORE_SECOND_BRAIN_QUERY_HERMES_MCP.md` §9–§10. **Resume P3** (Hermes CLI / `hermes doctor`).
- **HG-3 (2026-10-04):** `./scripts/brain/setup-hermes.sh` — official installer (repair path on partial install); binary `~/.hermes/hermes-agent/hermes`. `hermes doctor` exit **0** with advisories (npm audit notes, optional `hermes setup` / `hermes doctor --fix`); core runtime OK. Next: `hermes setup`, then P4 MCP.
- **HG-4 closed (2026-10-05):** Automated P4 via `setup-hermes-mcp.sh` / `setup-local.sh`: token sync, MCP config, `skills.disabled: [llm-wiki]`, `external_dirs` → repo harness skills. Read smoke: `mcp-smoke-read.sh`. Nashsu hub skill install **blocked** by Hermes skills-guard (localhost API patterns) — repo **`nashsu-mcp-read`**, **`query-brain`**, **`ingest-to-brain`** substitute.
- **P6 (2026-10-05):** Harness skills + `example-ingest.yaml`, `ingest.sh`; pytest AC-SB6.
- **P7 (2026-10-05):** `scripts/brain/backup.sh`; pytest AC-SB7; `./scripts/verify.sh` green.
- **HG-5 (pending):** Default vault **`…/second_brain/brain/wiki`** — confirm when Obsidian opened (runbook §11).
- **HG-8 (pending):** [`docs/ACCEPTANCE-second-brain-hermes-v1.md`](../ACCEPTANCE-second-brain-hermes-v1.md); **NB-SB1** table lookup not yet run.
