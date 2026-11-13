---
name: ingest-to-brain
description: Capture evidence into second_brain raw/sources with manifest; never compile wiki directly.
---

# ingest-to-brain

## Goal

Write new sources to **`brain/<profile>/raw/sources/<channel>/`** and optional **`brain/<profile>/manifests/<id>.yaml`**. Nashsu LLM Wiki compiles **`brain/<profile>/wiki/`** — Hermes does **not** edit wiki pages as compiler.

## Steps

1. Choose channel: `uploads`, `personal`, `web`, `github`, `gmail`, `drive`, or `chat`.
2. Copy or fetch artifact into `brain/<profile>/raw/sources/<channel>/` with stable filename.
3. Optional manifest under `brain/<profile>/manifests/` with `source_id`, `channel`, `sha256`, `captured_at`, `uri`.
4. If the desktop app is down, **`local-llm-wiki`** `start` first. Then Nashsu ingest (Source Watch auto-ingest when the app is open on project **brain**), or the operator runs rescan in the LLM Wiki window.
5. **Do not** use bundled Hermes `llm-wiki` skill or write under `brain/<profile>/wiki/` except via Nashsu.

## Prohibited

- Direct edits to compiled `brain/<profile>/wiki/` as the ingestion compiler.
- Second wiki compiler alongside Nashsu.

See [`docs_manual_gen/PLAN_SECOND_BRAIN_HERMES_V1.md`](../../../../docs_manual_gen/PLAN_SECOND_BRAIN_HERMES_V1.md) §10.
