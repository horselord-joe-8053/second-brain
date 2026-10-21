<h1 id="rmp-arch-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Lane benchmark — architecture</h1>

<h2 id="rmp-arch-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Flow](#rmp-arch-flow) — end-to-end.
2. [Modules](#rmp-arch-modules) — `lib/` responsibilities.
3. [Future DB](#rmp-arch-db) — JSON as data layer v1.

---

<h2 id="rmp-arch-flow" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Flow</h2>

```mermaid
graph TD
  J[retail-manual-qa-test-suite.json] --> L[lib.load_suite]
  Y[retail-ingest-lanes.yaml] --> R[lib.lanes]
  L --> X[lib.runner]
  R --> X
  X --> W[LlmWikiHttpClient per lane path]
  W --> A[lib.answer_pipeline]
  A --> S[lib.scoring]
  S --> O[results.json]
  O --> M[lib.report_md]
  O --> H[lib.report_html]

  style J fill:#e3f2fd,stroke:#1976d2,stroke-width:1px,font-size:9px
  style X fill:#fff3e0,stroke:#e65100,stroke-width:1px,font-size:9px
  style W fill:#ede7f6,stroke:#5e35b1,stroke-width:1px,font-size:9px
  style O fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,font-size:9px
```

Each lane uses **`POST /api/v1/projects/{absolute-path}/search`** — no UI project switch.

---

<h2 id="rmp-arch-modules" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Modules</h2>

| Module | Role |
|--------|------|
| `lib/load_suite.py` | Validate schema; iterate questions with SKU context |
| `lib/lanes.py` | Load A–D registry; preflight wiki + API |
| `lib/answer_pipeline.py` | Search → read → answer LLM → optional polish |
| `lib/scoring.py` | Negative exact match; LLM judge for easy/hard |
| `lib/runner.py` | Checkpointed multi-lane driver |
| `lib/report_md.py` / `lib/report_html.py` | Scoreboards from `results.json` |

---

<h2 id="rmp-arch-db" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Future DB</h2>

`results.json` schema is versioned (`schema_version`) so rows can migrate into Postgres/SQLite without changing report generators.
