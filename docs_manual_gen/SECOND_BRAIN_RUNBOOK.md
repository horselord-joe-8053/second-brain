<h1 id="runbook-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Second Brain — setup runbook (live log)</h1>

**Purpose:** Commands and manual steps to stand up Topology A (Mac). GUI setup for LLM Wiki is required today; automation is a later fork/driver.  
**Repos:** `second_brain/` (corpus + harness) · sibling `../nu_llm_wiki/` ([private LLM Wiki fork](https://github.com/horselord-joe-8053/llm-wiki)).

<h2 id="document-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Prerequisites](#prereq) — tools and versions.
2. [Repo layout](#layout) — paths on this host.
3. [second_brain harness](#harness) — seed and verify.
4. [nu_llm_wiki from source](#nu-llm-wiki) — dev app and MCP build.
5. [Manual in-app steps (HG-2)](#manual-app) — project first, then settings.
6. [Secrets and config files](#secrets) — `.env` vs LLM Wiki app state.
7. [Embeddings (optional)](#embeddings) — vector search; lexical-only OK.
8. [Local API and MCP](#api-mcp) — token, curl, endpoints, Hermes snippet.
9. [Query path (Hermes / MCP)](#query-path) — read path pointer.
10. [Hermes (P3–P4)](#hermes) — install and wire MCP.
11. [Verification](#verify) — scripts and API smoke.

---

<h2 id="prereq" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Prerequisites</h2>

| Tool | Notes |
|------|--------|
| **Node.js** | **≥20.19** for Vite 8 / `nu_llm_wiki` (system `/usr/local` was 20.5.0 — too old). Portable **22.14** used: see §4. |
| **Xcode Command Line Tools** | Required for Rust/Tauri + Python. Unattended: `softwareupdate -i "Command Line Tools for Xcode-16.4" --agree-to-license` (or GUI `xcode-select --install`). |
| **protoc** | `brew install protobuf` (this host: libprotoc 3.21.9) |
| **Rust** | `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh -s -- -y` then `source "$HOME/.cargo/env"` |
| **Python 3 + pytest** | For `./scripts/verify.sh` AC tests |

---

<h2 id="layout" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Repo layout</h2>

```text
/Users/jjw8053/projects/
├── second_brain/          # this repo — brain/ corpus, docs, bootstrap
└── nu_llm_wiki/           # git@github.com:horselord-joe-8053/llm-wiki.git
```

**LLM Wiki project folder (open in app):**  
`/Users/jjw8053/projects/second_brain/brain`

---

<h2 id="harness" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. second_brain harness (automated)</h2>

From repo root:

```bash
cd /Users/jjw8053/projects/second_brain
eval "$(bash bootstrap/core/scripts/parse-bootstrap-meta.sh bootstrap/specific/bootstrap.md)"
bash bootstrap/core/scripts/seed-harness.sh . "Second Brain" "Hermes + LLM Wiki" "$BOOTSTRAP_PROFILE"
bash bootstrap/core/scripts/seed-scaffold-scripts.sh . general
bash bootstrap/core/scripts/apply-module.sh . second-brain
bash bootstrap/core/scripts/seed-product.sh .
./scripts/verify.sh
```

P1 delivered: `brain/` tree, `harness/second-brain/README.md`, root README, tests under `tests/`.

---

<h2 id="nu-llm-wiki" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. nu_llm_wiki from source (dev only)</h2>

**Node 22 (portable — sibling `.tools`, not in git):**

```bash
curl -fsSL https://nodejs.org/dist/v22.14.0/node-v22.14.0-darwin-x64.tar.gz -o /tmp/node22.tar.gz
mkdir -p /Users/jjw8053/projects/.tools
tar -xzf /tmp/node22.tar.gz -C /Users/jjw8053/projects/.tools
export PATH="/Users/jjw8053/projects/.tools/node-v22.14.0-darwin-x64/bin:$PATH"
node --version   # v22.14.0
```

**Clone + deps (run with Node 22 on PATH):**

```bash
cd /Users/jjw8053/projects
git clone git@github.com:horselord-joe-8053/llm-wiki.git nu_llm_wiki
cd nu_llm_wiki
npm install
npm --prefix mcp-server ci && npm run mcp:build
source "$HOME/.cargo/env"
npm run tauri dev
```

**Remotes on this machine:** `origin` → private fork (push here). Optional **`upstream`** → `https://github.com/nashsu/llm_wiki.git` for pulling upstream releases; merge then `git push origin main`.

**Dev server:** API **`http://127.0.0.1:19828/api/v1`**, clip **`127.0.0.1:19827`**. Leave the terminal open while using the app.

**MCP entry (after build):**  
`/Users/jjw8053/projects/nu_llm_wiki/mcp-server/dist/src/index.js`

---

<h2 id="manual-app" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Manual in-app steps (HG-2)</h2>

<span style="background:#fff9c4;padding:2px 4px">GUI required</span> — no supported repo config file for LLM provider keys yet. Order matters:

1. **Start app** — `npm run tauri dev` (§4).
2. **Open or create project first** — **File → Open project** (or equivalent) → select  
   `/Users/jjw8053/projects/second_brain/brain`  
   Many settings (Source Watch, per-project LLM overrides, `{id}` in API calls as `current`) assume a project is active. Do this **before** relying on API + MCP.
3. **Settings → LLM** — ingest + chat models and **provider API keys** (OpenAI, Gemini, Ollama, etc.). Stored in macOS app data (`app-state.json`), **not** in `second_brain/.env`.
4. **Settings → API + MCP** — enable **local HTTP API**, **Generate new token**, enable **MCP access**, **Save**. Copy token into local `.env` as `LLM_WIKI_API_TOKEN` (see §6) or a password manager — **never commit**.
5. **Smoke ingest (HG-2 exit)** — drop `brain/raw/sources/uploads/smoke-test.md` (committed in repo). In the **native LLM Wiki window**, **Open project** → `…/second_brain/brain` (required: ingest workers run in the UI, not via API alone). Ensure **Settings → Source Watch** has **auto-ingest** on for that project. Wait until activity finishes; expect new/updated pages under `brain/wiki/` (not only `index.md`). Optional API assist after the project is open: `POST …/projects/current/sources/rescan` with bearer token.

**Ingest tip:** Source Watch queues **new or modified** files. If a file was already in the project snapshot before auto-ingest was enabled, use **Refresh folder** (Sources tab), the **book** icon on the row, or edit-and-save the source file to trigger a change.

---

<h2 id="secrets" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Secrets and config files</h2>

| What | Where | Consumed by |
|------|--------|-------------|
| OpenAI / Gemini **provider** keys and models | LLM Wiki **Settings → LLM** (+ optional embedding/search sections) | Desktop ingest, chat, Agent |
| Same keys for **Hermes** scripts (optional) | `second_brain/.env` (gitignored) — template **`.env.example`** | Future Hermes / repo scripts only |
| **Local API bearer** (not an LLM key) | LLM Wiki **Settings → API + MCP**; copy to **`LLM_WIKI_API_TOKEN`** in `.env` | `curl`, MCP `node …`, Hermes `config.yaml` |
| Hermes MCP layout | **`docs/harness/hermes-mcp.example.yaml`** | Paste into `~/.hermes/config.yaml` (P4) |

The LLM Wiki app does **not** read `second_brain/.env` for ingest. Keep provider keys in the app UI; use `.env` for automation convenience on **this machine** only.

---

<h2 id="embeddings" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Embeddings (optional)</h2>

Vector search is **optional**. With embeddings **disabled**, chat and `POST …/search` still work using **lexical/token** retrieval (BM25-style). Enable embeddings only when you want the **vector** leg of hybrid search.

**Settings → Embeddings** (project **brain** open):

1. Turn **Enable vector search** on (or leave off for lexical-only).
2. Fill **Endpoint**, **Model**, **API key**, and (Gemini only) **Output dimensionality** — stored in app `app-state.json`, not repo `.env`.

**Verified on this host (Gemini, Oct 2026):**

| Field | Value |
|-------|--------|
| Endpoint | `https://generativelanguage.googleapis.com/v1beta` |
| Model | `gemini-embedding-2` |
| Output dimensionality | `768` |
| API key | Same Gemini key as **Settings → LLM** |
| Custom request headers | Leave empty for Gemini (remove third-party provider headers) |

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Provider</th><th>Endpoint (paste as-is)</th><th>Model (examples)</th><th>API key</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Google Gemini <span style="background:#2e7d32;color:white;padding:1px 4px">verified</span></td><td style="background:#e8f5e9"><code>https://generativelanguage.googleapis.com/v1beta</code></td><td style="background:#e8f5e9"><code>gemini-embedding-2</code> (GA); alternates: <code>gemini-embedding-001</code>, <code>gemini-embedding-2-flash-001</code></td><td style="background:#e8f5e9">Gemini API key</td></tr>
<tr><td style="background:#e3f2fd">OpenAI</td><td style="background:#fff3e0"><code>https://api.openai.com/v1/embeddings</code></td><td style="background:#fff3e0"><code>text-embedding-3-small</code></td><td style="background:#fff3e0">OpenAI key (Bearer)</td></tr>
<tr><td style="background:#e3f2fd">Local (Ollama / LM Studio)</td><td style="background:#fff3e0">e.g. <code>http://127.0.0.1:1234/v1/embeddings</code> or <code>http://127.0.0.1:11434/v1/embeddings</code></td><td style="background:#fff3e0">Model id shown in the local server</td><td style="background:#fff3e0">Often empty</td></tr>
</tbody>
</table>

3. **Test connection** (and optional functional test) in the same panel.
4. **Reindex / embed all pages** for project **brain** so LanceDB under `brain/.llm-wiki/` is populated (required before vector hits appear in search). Re-run after changing model or dimensionality.

The app detects Google endpoints by hostname or `:embedContent` and builds the REST path from **Endpoint + Model**; OpenAI-compatible servers use JSON `{ "model", "input" }` at the URL you provide.

---

<h2 id="api-mcp" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. Local API and MCP</h2>

<h3 id="api-token" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">8.1 Token</h3>

- **One secret** for localhost API auth. MCP uses the **same** value via env `LLM_WIKI_API_TOKEN` (there is no separate “MCP token”).
- Load for shell: `set -a && source .env && set +a` from `second_brain` root (or export manually).

<h3 id="api-curl" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">8.2 Example curl</h3>

```bash
cd /Users/jjw8053/projects/second_brain
set -a && source .env && set +a

curl -sS -H "Authorization: Bearer ${LLM_WIKI_API_TOKEN}" \
  "http://127.0.0.1:19828/api/v1/projects"

curl -N -X POST \
  -H "Authorization: Bearer ${LLM_WIKI_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  "http://127.0.0.1:19828/api/v1/projects/current/chat" \
  -d '{"message":"Summarize this knowledge base.","stream":true}'
```

Use project UUID, filesystem path, or the literal `current` for `{id}` when the desktop app has that project open.

<h3 id="api-mcp-json" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">8.3 MCP client snippet</h3>

Full example with filesystem MCP: **`docs/harness/hermes-mcp.example.yaml`**. Minimal shape:

```json
{
  "mcpServers": {
    "llm-wiki": {
      "command": "node",
      "args": ["/Users/jjw8053/projects/nu_llm_wiki/mcp-server/dist/src/index.js"],
      "env": {
        "LLM_WIKI_API_TOKEN": "<same as Settings → API + MCP>"
      }
    }
  }
}
```

<h3 id="api-endpoints" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">8.4 HTTP endpoints (from app Settings)</h3>

Replace `{id}` with project UUID, project path, or `current`.

| Method | Path | Notes |
|--------|------|--------|
| GET | `/api/v1/health` | Liveness; no auth |
| GET | `/api/v1/projects` | List projects |
| GET | `/api/v1/projects/{id}/files` | `?root=wiki\|sources\|all`, `?recursive`, `?maxFiles` |
| GET | `/api/v1/projects/{id}/files/content` | `?path=wiki/index.md`, text, 2 MB max |
| GET | `/api/v1/projects/{id}/reviews` | Review tab data; default unresolved |
| PATCH | `/api/v1/projects/{id}/reviews/{reviewId}` | `{ resolved?, action? }` |
| POST | `/api/v1/projects/{id}/reviews/resolve` | Bulk resolve |
| POST | `/api/v1/projects/{id}/search` | Hybrid search JSON body |
| GET | `/api/v1/projects/{id}/graph` | Wikilinks graph |
| POST | `/api/v1/projects/{id}/sources/rescan` | Source Watch rescan |
| POST | `/api/v1/projects/{id}/pages/embed` | Index one wiki page; token required |
| POST | `/api/v1/projects/{id}/chat` | Agent chat; token required; optional SSE |
| POST | `/api/v1/projects/{id}/chat/{sessionId}/cancel` | Cancel Agent turn |

---

<h2 id="query-path" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">9. Query path (Hermes / MCP)</h2>

**Read path** (HERMES-3 / `query-brain`): compiled knowledge lives in **`brain/wiki/`**; agents should query via LLM Wiki API/MCP, not by scanning the whole tree in prompt context.

- **In app:** Chat / Agent tab on project **brain** (full UI retrieval loop).
- **For Hermes:** MCP tools `llm_wiki_set_project`, `llm_wiki_search`, `llm_wiki_read_file`, optional `llm_wiki_chat` — see [`MORE_SECOND_BRAIN_QUERY_HERMES_MCP.md`](./MORE_SECOND_BRAIN_QUERY_HERMES_MCP.md) for patterns, caveats, and verified tool names.
- **Preflight:** App running; **`brain`** is current project; bearer token in MCP env; embeddings optional (§7).

---

<h2 id="hermes" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">10. Hermes (P3–P4)</h2>

**P3 exit (HG-3):** `hermes doctor` reports clean; add one line to **`docs/specs/second-brain-hermes-v1.md` → Decisions**; tick P3 in [`docs/plans/second-brain-hermes-v1-plan.md`](../docs/plans/second-brain-hermes-v1-plan.md).

```bash
./scripts/brain/setup-local.sh      # idempotent: Hermes install (if needed) + doctor + corpus checks
# or Hermes only:
./scripts/brain/setup-hermes.sh
hermes setup                        # or: hermes setup --portal
```

From verify: `RUN_BRAIN_SETUP=1 ./scripts/verify-local.sh` runs the same driver before layout/pytest checks.

**P4 (HG-4) — automated:** `./scripts/brain/setup-hermes-mcp.sh` (also invoked from `setup-local.sh` when LLM Wiki `app-state.json` exists):

1. **`sync-llm-wiki-token.sh`** — reads `apiConfig.token` from `~/Library/Application Support/com.llmwiki.app/app-state.json` → `second_brain/.env` and `~/.hermes/.env` as `LLM_WIKI_API_TOKEN` (never printed).
2. **`merge-hermes-mcp-config.py`** — appends managed `mcp_servers` block to `~/.hermes/config.yaml` (token ref `${LLM_WIKI_API_TOKEN}`).
3. API health + optional `hermes mcp test llm_wiki`.

Manual reference shape: **`docs/harness/hermes-mcp.example.yaml`**. Disable Hermes bundled `llm-wiki` **compiler** skill (`hermes skills disable llm-wiki`); install Nashsu **llm-wiki** agent skill (API/MCP, not compile):

Optional Docker path (prefer **CLI on host** for MCP to `127.0.0.1:19828`): see [`PLAN_SECOND_BRAIN_HERMES_V1.md`](./PLAN_SECOND_BRAIN_HERMES_V1.md) §7.2.

**P4 (manual remainder):**

```bash
npx skills add https://github.com/nashsu/llm_wiki_skill.git --skill llm-wiki
```

---

<h2 id="verify" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">11. Verification</h2>

```bash
cd /Users/jjw8053/projects/second_brain
./scripts/verify.sh
./scripts/verify-local.sh

set -a && source .env && set +a
curl -sS -H "Authorization: Bearer ${LLM_WIKI_API_TOKEN}" \
  "http://127.0.0.1:19828/api/v1/health"
curl -sS -H "Authorization: Bearer ${LLM_WIKI_API_TOKEN}" \
  "http://127.0.0.1:19828/api/v1/projects"
```

---

<h2 id="future-script" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Idempotent driver</h2>

**In repo:** [`scripts/brain/setup-local.sh`](../scripts/brain/setup-local.sh) (Hermes via [`setup-hermes.sh`](../scripts/brain/setup-hermes.sh), corpus layout checks, next-step hints). Extend this script as more steps become automatable.

**Still human-gated:** LLM Wiki GUI (open project, ingest, embeddings) until `nu_llm_wiki` supports automation config merge.
