# Plan: second-brain-hermes-v1

Source: **`docs/PLAN_SECOND_BRAIN_HERMES_V1.md`**

## P1 — Repo corpus (plan §5)

**ACs:** SB1, SB2  
**Exit:** `./scripts/verify.sh` green; `./scripts/verify-local.sh` green  
**Depends:** phase 1 harness seeded

## P2 — Nashsu LLM Wiki (plan §6)

**HG-2** — desktop-install module; stop until human confirms ingest smoke  
**Exit:** Human recorded in Decisions; optional note of API token location (not in repo)

## P3 — Hermes harness (plan §7)

**HG-3**  
**Exit:** `hermes doctor` reported clean (human confirmation)

## P4 — Wire harness ↔ compiler (plan §8)

**HG-4**; repo may add `docs/harness/hermes-mcp.example.yaml`  
**Exit:** MCP smoke described in Decisions

## P5 — Obsidian (plan §9)

**HG-5**  
**Exit:** vault path recorded in Decisions

## P6 — Ingestion workflows (plan §10)

**ACs:** SB6  
**Exit:** `./scripts/verify.sh` green

## P7 — Backup and ops (plan §11)

**ACs:** SB7  
**Exit:** `./scripts/verify.sh` green

## P8 — Acceptance (plan §12)

**HG-8** manual checklist  
**Exit:** Decisions log + waiver or pass notes
