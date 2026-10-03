# Second Brain

Local-first personal knowledge system: **`brain/`** corpus, [Nashsu LLM Wiki](https://github.com/nashsu/llm_wiki) as compiler, [Hermes](https://hermes-agent.nousresearch.com/) as harness, Obsidian on compiled wiki.

## Docs

- [Architecture](docs/second-brain-llm-wiki-architecture.md)
- [Implementation plan (Hermes v1)](docs/PLAN_SECOND_BRAIN_HERMES_V1.md)
- [Setup runbook (commands + manual steps)](docs/SECOND_BRAIN_RUNBOOK.md)
- Product specs: `docs/specs/` (seeded from `bootstrap/specific/`)

## Bootstrap / delivery

Implementation follows the unified kit:

```text
Run bootstrap/EXECUTE_GEN.md implementing docs/PLAN_SECOND_BRAIN_HERMES_V1.md
```

Kit entry: `bootstrap/specific/bootstrap.md`.

## Verify

```bash
./scripts/verify.sh
./scripts/verify-local.sh
```

Requires Python 3 + pytest for AC tests when Xcode Command Line Tools (or another Python) is available.
