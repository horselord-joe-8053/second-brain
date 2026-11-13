---
name: local-llm-wiki
description: Start, stop, or restart the local LLM Wiki desktop app without changing saved UI settings. Use before query-brain or ingest when the wiki API may be down. This is not the bundled llm-wiki compiler skill.
---

# local-llm-wiki

Operate the **desktop app** that serves the wiki API on this Mac. Do not compile wiki pages yourself. The bundled Hermes skill named **`llm-wiki`** is a different thing and stays disabled.

Script (repo root is detected by the script; run it from anywhere):

```bash
./scripts/brain/llm-wiki.sh status
./scripts/brain/llm-wiki.sh start
./scripts/brain/llm-wiki.sh stop
./scripts/brain/llm-wiki.sh restart
```

| Command | When |
|---------|------|
| `status` | Before any wiki tool call. Exit 0 means the API is up. |
| `start` | `status` says `down`. If it is already up, this leaves it running. |
| `stop` | The user asked to shut the desktop app down. |
| `restart` | The user asked to restart it, or the API is wedged after a start that did not come up. |

## Settings and token

UI settings (models, keys, project, API on/off) live in the macOS app file `app-state.json`. These commands do not delete that file and do not click **Generate new token**.

Each `status`, `start`, and `restart` copies the token already saved in that file into `second_brain/.env` and `~/.hermes/.env`.

Trust only the lines that start with `llm-wiki:`. The token copy step also prints `updated LLM_WIKI_API_TOKEN`; that only means the env files were written, not that the token changed.

- **`llm-wiki: token unchanged`** — keep going.
- **`llm-wiki: token refreshed`** — the desktop app is on the new token. Wiki tools in **this** Hermes session can still be holding the previous one and will get unauthorized. Tell the user to start a **new Hermes session**, then run `status` again. Do not generate another token to fix it.
- **`no API token in app settings`** — stop and ask the user to save Settings → API + MCP once in the LLM Wiki window.

## After the API is up

1. `llm_wiki_set_project` to `…/second_brain/brain/<profile>` — `brain/retail` (default, FRU) or `brain/personal`.
2. Then **`query-brain`** or **`ingest-to-brain`**.

## Do not

- Enable or follow the bundled **`llm-wiki`** compiler skill.
- Delete `~/Library/Application Support/com.llmwiki.app`.
- Generate a new API token unless the user explicitly asked to rotate it.
