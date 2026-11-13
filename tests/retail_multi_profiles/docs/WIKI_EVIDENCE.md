<h1 id="wiki-evidence-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Wiki evidence — audit registry and harness modes</h1>

**Suite context:** Phase **3 (A1)** — Lane **B** `brain/retail-md`. Plan: [`REFACTOR_A1_WIKI_HG_P3.md`](../../../../docs_manual_gen/ref_plan/new/REFACTOR_A1_WIKI_HG_P3.md).

## Claim audit

```bash
export PYTHONPATH=$PWD/scripts/retail:$PWD
python -m retail_brain.evidence.wiki_audit --brain-root brain/retail-md
python -m retail_brain.evidence.wiki_audit --brain-root brain/retail-md --summarize
```

Registry: `brain/retail-md/.wiki-claim-audit/claims.jsonl` — statuses `supported`, `uncertain`, `contradicted`, `unverified`.

## Harness `wiki_evidence` modes

`run-config.yaml` → `wiki_evidence.mode`:

| Mode | Behavior |
|------|----------|
| `full` | All wiki search hits (default) |
| `sources_only` | Keep `wiki/sources/` hits only |
| `sources_rerank` | Filter sources, then reorder by score |

CLI override:

```bash
python -m tests.retail_multi_profiles --smoke --lanes B --wiki-evidence sources_only
```

## LLM Wiki server

```bash
./scripts/brain/llm-wiki.sh status
./scripts/brain/llm-wiki.sh start
```

Wiki arms require API up on `127.0.0.1:19828` (or `LLM_WIKI_API_BASE_URL`).

## TYPE_C_C20 insight benchmark

```bash
python -m tests.retail_multi_profiles.run_cos_insight_qa --smoke --arm both
```

Fixture: `data/retail-cos-insight-test-suite.json` (`TYPE_C_C20`).
