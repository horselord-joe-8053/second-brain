# Feature: [Name]

<!-- ac-tests: enforced -->
<!-- delivery-phase: P1 -->
<!-- plan: docs/plans/[feature]-plan.md -->

Use **`<!-- ac-tests: optional -->`** when verification is checklist-only (e.g. external tool install).

Each **`**AC-<ID>:**`** maps to tests or checklists per `docs/PROJECT-TDD.md`. One AC per delivery phase.

## Goal

## Constraints

- Stack / tools for this feature
- **Human gates:** list external installs (HG-*) with clear owner action

## Acceptance criteria (behavior)

1. **AC-B1:** (P1) …

## Human gates (when applicable)

1. **HG-1:** (P1) Human installs/configures … — agent stops with instructions until done.

## UI & layout

Optional. Fill only when this feature includes a user-visible UI (web, desktop, or Obsidian vault layout).

## Out of scope

## Verification

- Automated: pytest/shell commands named in plan **Exit**
- Manual: checklist items for HG-*

## Test seams

| AC / HG | Phase | Seam | Verification |
|---------|-------|------|--------------|
| B1 | P1 | pytest `tests/...` | `test_ac_b1_...` |
| HG-1 | P1 | human | recorded in Decisions |

Implement per **`docs/PROJECT-TDD.md`**.

## Decisions

<!-- align-requirements fills this -->
