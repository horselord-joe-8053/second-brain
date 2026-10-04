# Second Brain — kit entry (Hermes v1)

## Kit meta

```text
profile: general
phase1_modules: second-brain
phase2_modules: desktop-install, second-brain
plan_source: docs/PLAN_SECOND_BRAIN_HERMES_V1.md
architecture_doc: docs/second-brain-llm-wiki-architecture.md
feature_id: second-brain-hermes-v1
spec_file: second-brain-hermes-v1.md
plan_file: second-brain-hermes-v1-plan.md
env_append: none
done_display_name: Second Brain (Hermes + LLM Wiki)
```

## Mission

Local-first Second Brain in this repo: **`brain/`** corpus, LLM Wiki (`horselord-joe-8053/llm-wiki` sibling) as compiler, Hermes as harness, Obsidian on compiled wiki. Topology A on Mac. See plan + architecture doc in meta.

## Ticket slices (delivery order)

| Phase | Focus | Type |
|-------|--------|------|
| P1 | Repo corpus layout (Phase 0) | automated |
| P2 | LLM Wiki install + project + ingest smoke | HG + verify |
| P3 | Hermes CLI + doctor | HG |
| P4 | MCP + llm-wiki agent skill; disable Hermes llm-wiki skill | HG + repo docs |
| P5 | Obsidian vault | HG |
| P6 | Ingestion harness + manifest schema | automated |
| P7 | Backup/ops scripts | automated |
| P8 | Acceptance checklist (architecture §12) | HG / manual |

## Glossary / AGENTS

- **Compiler:** LLM Wiki desktop app only — not Hermes bundled llm-wiki skill.
- **Corpus root:** `brain/` (LLM Wiki project folder).
- **Harness writes:** `brain/raw/sources/`; **never** direct edits to compiler-owned wiki except via LLM Wiki ingest.
- **TDD:** `docs/PROJECT-TDD.md`; repo ACs in **`second-brain-hermes-v1.md`**.
