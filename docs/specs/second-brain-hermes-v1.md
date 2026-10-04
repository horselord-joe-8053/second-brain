# Feature: Second Brain Hermes v1

<!-- ac-tests: enforced -->
<!-- delivery-phase: P1 P6 P7 -->
<!-- plan: docs/plans/second-brain-hermes-v1-plan.md -->

## Goal

Implement in-repo Second Brain foundation per **`docs/PLAN_SECOND_BRAIN_HERMES_V1.md`** and **`docs/second-brain-llm-wiki-architecture.md`**: corpus tree, harness contract, backup scripts; external tools via human gates.

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
2. **HG-3:** (P3) Human installs Hermes CLI; `hermes doctor` clean — agent gives install commands only.
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
- **HG-2 smoke (2026-10-03, partial):** `brain/raw/sources/uploads/smoke-test.md` added; `brain/wiki/index.md` seeded so Nashsu accepts the folder. API rescan detected `smoke-test.md` as a change when `brain` is current (clip `POST /project` or UI). **LLM ingest → wiki pages** still requires **native app → Open project → `second_brain/brain`** with Source Watch auto-ingest; confirm new wiki output then mark HG-2 closed.
