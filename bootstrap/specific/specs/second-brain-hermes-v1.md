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

<!-- align-requirements / HG confirmations; mirror docs/specs/second-brain-hermes-v1.md -->

- **P1 (2026-10-03):** Repo corpus layout, harness stub README, root README, verify scripts seeded.
- **HG-2 closed (2026-10-04):** LLM Wiki on `brain/`; API/MCP; ingest smoke → wiki pages. Token in gitignored `.env`. See canonical spec **Decisions** in `docs/specs/second-brain-hermes-v1.md`.
