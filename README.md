# Second Brain

Local-first personal knowledge system: **`brain/`** corpus, [LLM Wiki fork](https://github.com/horselord-joe-8053/llm-wiki) (`../nu_llm_wiki/`) as compiler, [Hermes](https://hermes-agent.nousresearch.com/) as harness, Obsidian on compiled wiki.

## Docs

- [Architecture](docs_manual_gen/second-brain-llm-wiki-architecture.md)
- [Implementation plan (Hermes v1)](docs_manual_gen/PLAN_SECOND_BRAIN_HERMES_V1.md)
- [Setup runbook (commands + manual steps)](docs_manual_gen/SECOND_BRAIN_RUNBOOK.md)
- [Query layer + Hermes MCP (follow-on chat)](docs_manual_gen/MORE_SECOND_BRAIN_QUERY_HERMES_MCP.md)
- Product specs: `docs/specs/` (seeded from `bootstrap/specific/`)
- Manual design docs: [`docs_manual_gen/`](docs_manual_gen/README.md)

## Bootstrap / delivery

Implementation follows the unified kit:

```text
Run bootstrap/EXECUTE_GEN.md implementing docs_manual_gen/PLAN_SECOND_BRAIN_HERMES_V1.md
```

Kit entry: `bootstrap/specific/bootstrap.md`.

## Local setup (idempotent)

```bash
./scripts/brain/setup-local.sh    # Hermes install/repair + doctor + corpus checks
RUN_BRAIN_SETUP=1 ./scripts/verify-local.sh   # same driver, then verify-local
```

## Verify

```bash
./scripts/verify.sh
./scripts/verify-local.sh
```

Requires Python 3 + pytest for AC tests when Xcode Command Line Tools (or another Python) is available.
