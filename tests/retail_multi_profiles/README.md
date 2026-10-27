<h1 id="rmp-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Retail multi-profile lane QA benchmark</h1>

Automated **A–D ingest lane** comparison on a shared **90-question** retail manual QA suite. Plan: [`REFACTOR_RETAIL_MANUAL_INGEST_ABCD_BENCHMARK.md`](../../docs_manual_gen/ref_plan/new/REFACTOR_RETAIL_MANUAL_INGEST_ABCD_BENCHMARK.md).

<h2 id="rmp-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Inputs](#rmp-inputs) — suite JSON, lane paths.
2. [Outputs](#rmp-outputs) — JSON, Markdown, HTML.
3. [Layout](#rmp-layout) — modules under this tree.
4. [Run tiers](#rmp-tiers) — CI vs live.
5. [Related retail tests](#rmp-related) — sibling folder.

---

<h2 id="rmp-inputs" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Inputs</h2>

| Input | Default location |
|-------|------------------|
| Benchmark Q&A JSON | `data/retail-manual-qa-test-suite.json` (vendored from upstream `fridge-qa-test-suite.json`) |
| Lane registry | `config/retail-ingest-lanes.yaml` (repo root) or CLI `--lane-path` list |
| Retail evidence (retrieval) | `config/brain-stack.yaml` → `second_brain.retail_evidence` (see `brain-stack.example.yaml`) |
| Harness eval | `data/run-config.yaml` → `retail_eval` (answer + judge LLM), `smoke_question_ids` |

---

<h2 id="rmp-outputs" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Outputs</h2>

Live runs write under **`ops/runs/retail-lane-abcd/<run_id>/`**:

| Artifact | Role |
|----------|------|
| `results.json` | Canonical row-level results + latency (future DB layer) |
| `results.jsonl` | Streaming / append-friendly copy |
| `scoreboard.md` | Human scan (extesttab-friendly tables) |
| `scoreboard.html` | Same metrics, colored comparison |
| `summary.json` | Lane winner + tie-break notes |

---

<h2 id="rmp-layout" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Layout</h2>

```
tests/retail_multi_profiles/
  README.md           ← this file
  ARCHITECTURE.md     ← data flow
  conftest.py         ← markers, shared fixtures
  data/               ← vendored suite + run-config template
  fixtures/           ← CI wiki pages + judge mocks
  docs/RAW_RAG.md     ← raw-sources vector RAG operator guide
  lib/raw_*.py        ← corpus, embed, Lance index, raw search, wiki vs raw compare
  lib/                ← load_suite, lanes, pipeline, scoring, report
  test_*.py           ← CI-tier pytest (incl. test_raw_*.py)
  __main__.py         ← CLI entry: python -m tests.retail_multi_profiles
```

**DRY:** Wiki HTTP client wraps `retail_brain.answer_manuals.LlmWikiHttpClient`; raw RAG reuses the same answer/judge pipeline with `--retrieval-mode raw_rag`.

**Main plan:** [`REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md`](../../docs_manual_gen/ref_plan/new/REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md) · **Raw RAG (M2, completed):** [`REFACTOR_RETAIL_RAW_SOURCES_RAG_ABCD_COMPARE.md`](../../docs_manual_gen/ref_plan/completed/REFACTOR_RETAIL_RAW_SOURCES_RAG_ABCD_COMPARE.md) · operator doc: [`docs/RAW_RAG.md`](./docs/RAW_RAG.md)

---

<h2 id="rmp-tiers" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Run tiers</h2>

| Tier | Command | Needs |
|------|---------|--------|
| CI | `pytest -q tests/retail_multi_profiles` | Fixture wiki + mocked LLM |
| Live smoke | `python -m tests.retail_multi_profiles --smoke --lanes A,B,C,D` | LLM Wiki, `OPENAI_API_KEY` (answer), `GEMINI_API_KEY` (judge) |
| Live full | `python -m tests.retail_multi_profiles --full --lanes A,B,C,D` | Same; 90×4 LLM calls (use `--limit 3` to dry-run) |
| Raw RAG | `--retrieval-mode raw_rag --lanes B,C,D` | `RETAIL_DATABASE_URL`; `OPENAI_API_KEY` for embeddings + answer; see [`docs/RAW_RAG.md`](./docs/RAW_RAG.md) |
| Resume | `--full --run-id abcd-full-openai --resume` | Skips rows in `ops/runs/…/results.jsonl` |
| Ops tail | `tail -f logs/ops/retail-lane-abcd-<run_id>.log` | Per-step progress; on crash grep `judge_start` in `results.jsonl` for last ticket |

---

<h2 id="rmp-related" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Related retail tests</h2>

Unit/integration tests for **`retail_answer.v1`** (tickets + single-profile manuals) live in **`tests/retail/`**, not here.
