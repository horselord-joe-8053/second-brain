---
name: ingest-to-brain
description: Capture evidence into second_brain raw/sources with manifest; never compile wiki directly.
---

# ingest-to-brain

## Goal

Write new sources to **`brain/raw/sources/<channel>/`** and optional **`brain/manifests/<id>.yaml`**. Nashsu LLM Wiki compiles **`brain/wiki/`** — Hermes does **not** edit wiki pages as compiler.

## Steps

1. Choose channel: `uploads`, `personal`, `web`, `github`, `gmail`, `drive`, or `chat`.
2. Copy or fetch artifact into `brain/raw/sources/<channel>/` with stable filename.
3. Optional manifest under `brain/manifests/` with `source_id`, `channel`, `sha256`, `captured_at`, `uri`.
4. Trigger Nashsu ingest (Source Watch auto-ingest when desktop app open on project **brain**), or operator runs rescan in LLM Wiki UI.
5. **Do not** use bundled Hermes `llm-wiki` skill or write under `brain/wiki/` except via Nashsu.

## Prohibited

- Direct edits to compiled `brain/wiki/` as the ingestion compiler.
- Second wiki compiler alongside Nashsu.

See [`docs_manual_gen/PLAN_SECOND_BRAIN_HERMES_V1.md`](../../../../docs_manual_gen/PLAN_SECOND_BRAIN_HERMES_V1.md) §10.
