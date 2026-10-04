---
name: nashsu-mcp-read
description: Thin Nashsu read path when hub llm_wiki_skill install is blocked — MCP tool names and smoke steps.
---

# nashsu-mcp-read

Use when **`llm_wiki_*` MCP tools** are configured (`setup-hermes-mcp.sh`).

| Tool | Use |
|------|-----|
| `llm_wiki_set_project` | Pin to `second_brain/brain` |
| `llm_wiki_search` | Hybrid search over wiki |
| `llm_wiki_read_file` | Full page read |
| `llm_wiki_graph` | Wikilink expansion |

Official skill (may require security review): `hermes skills inspect skills-sh/nashsu/llm_wiki_skill/llm-wiki`

Repo smoke: `./scripts/brain/mcp-smoke-read.sh`
