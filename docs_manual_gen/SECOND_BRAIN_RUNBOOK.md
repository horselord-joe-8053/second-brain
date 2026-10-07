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
10. [Hermes Desktop (P3–P4)](#hermes) — install/start Desktop, MCP, smoke (§10.1–§10.3).
11. [Obsidian (HG-5)](#obsidian) — vault on compiled wiki.
12. [Backup](#backup) — rsync stub.
13. [Verification](#verify) — scripts and API smoke.
14. [Brain stack config](#brain-stack) — yaml overlay + apply script.
15. [After reboot + P8 acceptance (HG-8)](#p8-acceptance) — stack order, Hermes integration chat, checklist.
16. [Hermes messaging (Telegram / WhatsApp)](#messaging) — gateway env, config merge, Second Brain from phone.

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
eval "$(bash bootstrap_seed/core/scripts/parse-bootstrap-meta.sh seed_grow/bootstrap.md)"
bash bootstrap_seed/core/scripts/seed-harness.sh . "Second Brain" "Hermes + LLM Wiki" "$BOOTSTRAP_PROFILE"
bash bootstrap_seed/core/scripts/seed-scaffold-scripts.sh . general
bash bootstrap_seed/core/scripts/apply-module.sh . second-brain
bash bootstrap_seed/core/scripts/seed-product.sh .
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
| Hermes MCP layout | **`docs/harness/hermes-mcp.example.yaml`** | Managed block via **`merge-hermes-wiring.py`** (P4) |
| Telegram / WhatsApp | **`~/.hermes/.env`** (synced from repo `.env` when listed in **`hermes.sync_env_keys`**) | Hermes **gateway** (Desktop sidebar **Gateway ready** or **`hermes gateway`**) |
| Messaging `platforms:` | **`~/.hermes/config.yaml`** wiring block | **`merge-hermes-wiring.py`** when env vars are set (§16) |

The LLM Wiki app does **not** read `second_brain/.env` for ingest. Keep provider keys in the app UI; use `.env` for automation convenience on **this machine** only. **Never commit** bot tokens or API keys.

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

<h2 id="hermes" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">10. Hermes (P3–P4) — Desktop UI</h2>

**Install + start Desktop (not TUI):**

```bash
cd /Users/jjw8053/projects/second_brain
./scripts/brain/install-and-start-hermes-desktop.sh --provider gemini -m gemini-3.0-flash
```

Split steps: **`setup-hermes-desktop.sh`** (once) → **`start-hermes.sh`**. Terminal TUI only if needed: **`start-hermes.sh --tui`**.

**P3 exit (HG-3):** `hermes doctor` reports clean (via **`setup-hermes.sh`** inside the scripts above).

```bash
./scripts/brain/setup-local.sh      # corpus + MCP + stack; does not replace Desktop install
```

From verify: `RUN_BRAIN_SETUP=1 ./scripts/verify-local.sh` runs the same driver before layout/pytest checks.

**P4 (HG-4) — automated:** `./scripts/brain/setup-hermes-mcp.sh` (also invoked from `setup-local.sh` when LLM Wiki `app-state.json` exists):

1. **`sync-llm-wiki-token.sh`** — reads `apiConfig.token` from `~/Library/Application Support/com.llmwiki.app/app-state.json` → `second_brain/.env` and `~/.hermes/.env` as `LLM_WIKI_API_TOKEN` (never printed).
2. **`merge-hermes-wiring.py`** — managed **`mcp_servers`** (`llm_wiki`, `second_brain_fs`) plus optional **`platforms.telegram` / `platforms.whatsapp`** from env (§16).
3. API health + optional `hermes mcp test llm_wiki`.

Manual reference shape: **`docs/harness/hermes-mcp.example.yaml`**. **`setup-hermes-skills.sh`** sets `skills.disabled: [llm-wiki]` and `external_dirs` → repo `harness/second-brain/skills`. Hub Nashsu install may be blocked by skills-guard — use repo **`nashsu-mcp-read`** / **`query-brain`** skills.

**Smoke:** `./scripts/brain/mcp-smoke-read.sh`

**PATH after reboot:** `export PATH="${HOME}/.local/bin:${HOME}/.hermes/hermes-agent:${PATH}"` before `hermes` / `hermes mcp list`.

Optional Docker path (prefer **CLI on host** for MCP to `127.0.0.1:19828`): see [`PLAN_SECOND_BRAIN_HERMES_V1.md`](./PLAN_SECOND_BRAIN_HERMES_V1.md) §7.2.

<h3 id="hermes-integration-smoke" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">10.1 Automated preflight</h3>

```bash
./scripts/brain/smoke-integrated.sh
```

Runs **`acceptance-automated.sh`** (wiki, MCP, `hermes mcp test`, NB-SB1 probe) and prints **Desktop chat prompts** below.

<h3 id="hermes-desktop-smoke" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">10.3 Integrated smoke in Hermes Desktop (PLAN §8.4)</h3>

With **LLM Wiki** open on **`…/second_brain/brain`**, **Hermes Desktop** running (**Gateway ready** in sidebar), and model selected (e.g. **Gemini 2.5 Flash** — avoid retired **`gemini-2.0-flash`**, API returns 404):

1. **Capabilities** (left sidebar) — confirm MCP servers **`llm_wiki`** and **`second_brain_fs`**. If missing, run **`./scripts/brain/apply-stack-config.sh`** and restart Desktop or reload MCP in-app.
2. **New session** — working directory should be **`…/second_brain`** (from **`start-hermes.sh`** / **`HERMES_DESKTOP_CWD`**).
3. **Prompt 1 (wiki):** *Use LLM Wiki MCP only. Set project to `/Users/jjw8053/projects/second_brain/brain`. Search "smoke test", read the top `wiki/` hit, summarize with path citations. No web search.*
4. **Pass:** Activity shows **`llm_wiki_search`** / **`llm_wiki_read_file`**; answer cites **`wiki/sources/…smoke-test…`**.
5. **Prompt 2 (NB-SB1):** *Search James conjugation verb table, read wiki source, cite `wiki/` path.*
6. **Prompt 3 (boundary):** *Where do new files go for ingest? Do not edit `brain/wiki/` as the compiler.*
7. **Obsidian check (optional):** Same page visible under **`brain/wiki`** in Obsidian.

Skill reference: **`harness/second-brain/skills/query-brain/SKILL.md`**. TUI equivalent: **`start-hermes.sh --tui`** — same prompts.

<h3 id="hermes-ui-and-keys" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">10.2 Where is Hermes UI? How to start? API keys?</h3>

**Three different “UIs” (do not confuse):**

| Surface | What it is | Start (Second Brain) |
|---------|------------|----------------------|
| **Desktop app** | Native **Electron** chat (recommended) | `./scripts/brain/start-hermes.sh` |
| **Terminal TUI** | `hermes chat --tui` in Terminal | `./scripts/brain/start-hermes.sh --tui` |
| **Web dashboard** | Local **settings** UI (`hermes dashboard`, default `http://127.0.0.1:9119`) | `hermes dashboard` (config/keys; not the main agent chat) |

**Not** the agent UI: **`setup-hermes-desktop.sh`** may run **`open https://hermes-agent.nousresearch.com/desktop`** — that is only the **DMG download page** in Safari. Flag **`--no-open-download-page`** skips that step (alias **`--no-browser`**); it does **not** disable Hermes’s web dashboard.

| Stop | Command |
|------|---------|
| Desktop | `./scripts/brain/stop-hermes.sh` |
| Web dashboard | Ctrl+C in its terminal, or `hermes dashboard --stop` |

**Install Hermes Desktop (one-time):**

```bash
./scripts/brain/setup-hermes-desktop.sh
```

Opens the [DMG download page](https://hermes-agent.nousresearch.com/desktop) unless you pass **`--no-open-download-page`**. Install **Hermes.app** to **Applications**, or build from CLI:

```bash
./scripts/brain/setup-hermes-desktop.sh --build --no-open-download-page
```

**Start** (applies stack env, sets provider/model on `~/.hermes/config.yaml`, cwd = repo):

```bash
./scripts/brain/start-hermes.sh --provider gemini -m gemini-3.0-flash
```

If **Hermes.app** is in `/Applications`, the script opens it; otherwise it runs **`hermes desktop --cwd …`** (first launch may build Electron — several minutes).

There is no separate “Second Brain app” — Hermes is the agent shell; LLM Wiki + Obsidian are the compiler and reader.

**OpenAI and Gemini keys — not the repo `.env` for chat:**

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>File</th><th>Purpose</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><code>~/.hermes/.env</code></td><td style="background:#e8f5e9"><span style="background:#2e7d32;color:white;padding:1px 4px">Hermes chat</span> — set via <code>hermes setup</code> or edit manually: <code>OPENAI_API_KEY</code>; Gemini: <code>GEMINI_API_KEY</code> or <code>GOOGLE_API_KEY</code>. Also <code>LLM_WIKI_API_TOKEN</code> (from <code>sync-llm-wiki-token.sh</code>, not OpenAI).</td></tr>
<tr><td style="background:#e3f2fd"><code>second_brain/.env</code></td><td style="background:#fff3e0">Repo scripts + curl — <code>LLM_WIKI_API_TOKEN</code> (synced). Optional <code>LLM_API_KEY</code> / <code>GEMINI_*</code> in <code>.env.example</code> for <strong>this repo’s</strong> harness/scripts only; Hermes does <strong>not</strong> read those names unless you copy the same keys into <code>~/.hermes/.env</code>.</td></tr>
<tr><td style="background:#e3f2fd">LLM Wiki app Settings</td><td style="background:#e8f5e9">Provider keys for <strong>ingest / compile / embeddings</strong> inside Nashsu (separate from Hermes).</td></tr>
</tbody>
</table>

**Recommended once after install:**

```bash
./scripts/brain/apply-stack-config.sh   # repo .env → ~/.hermes/.env
./scripts/brain/start-hermes.sh --provider gemini -m gemini-3.0-flash
```

Official refs: [Configuration](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) · [Environment variables](https://hermes-agent.nousresearch.com/docs/reference/environment-variables).

---

<h2 id="obsidian" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">11. Obsidian (HG-5)</h2>

**Recommended vault root:** `…/second_brain/brain/wiki` (compiled Markdown only). Alternative: project root `brain/` if `.obsidian/` was generated there by LLM Wiki.

**Automated install (macOS + Homebrew):**

```bash
./scripts/brain/setup-obsidian.sh
OPEN_OBSIDIAN_VAULT=1 ./scripts/brain/setup-obsidian.sh   # also launch Obsidian on the vault
```

Also runs from **`./scripts/brain/setup-local.sh`**. Record the vault path in spec **Decisions** (HG-5) after first open.

<h2 id="backup" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">12. Backup</h2>

```bash
./scripts/brain/backup.sh              # → backups/brain-YYYYMMDD-HHMMSS/
./scripts/brain/backup.sh /path/to/dir # custom destination
```

Excludes `brain/.llm-wiki/` (regenerable index). Also back up `~/.hermes/` separately for Hermes config/skills.

<h2 id="verify" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">13. Verification</h2>

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

<h2 id="brain-stack" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">14. Brain stack config (three apps)</h2>

**Single overlay:** gitignored **`config/brain-stack.yaml`** (paths, MCP, `hermes.sync_env_keys`). **Secrets in repo `.env`** (gitignored); optional **`secrets:`** block in yaml if you prefer one file.

```bash
cp config/brain-stack.example.yaml config/brain-stack.yaml
# Edit hermes.chat_provider + hermes.chat_model (e.g. gemini / gemini-3.0-flash)
# Put GEMINI_API_KEY, OPENAI_API_KEY, LLM_WIKI_API_TOKEN in .env
./scripts/brain/verify-stack-config.sh   # names only, no secrets printed
./scripts/brain/apply-stack-config.sh  # .env → ~/.hermes/.env + hermes model + MCP
```

**Do not** rely on `GEMINI_MODEL` or `OPENAI_MODEL` in `.env` for Hermes — set **`hermes.chat_model`** in **`brain-stack.yaml`** instead.

Also runs at the start of **`./scripts/brain/setup-local.sh`**. **Does not** write LLM Wiki provider keys into the desktop app (GUI remains source for ingest).

<h2 id="p8-acceptance" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">15. After reboot + P8 acceptance (HG-8)</h2>

**Stack order (Mac):**

1. **LLM Wiki** desktop app — open project **`…/second_brain/brain`**, API/MCP on.
2. **Obsidian** — vault **`…/second_brain/brain/wiki`** (already registered as **wiki**).
3. **Hermes wiring (no chat required yet):**

```bash
cd /Users/jjw8053/projects/second_brain
export PATH="${HOME}/.local/bin:${HOME}/.hermes/hermes-agent:${PATH}"
./scripts/brain/setup-local.sh
# or full P8 automated seams in one pass:
RUN_BRAIN_ACCEPTANCE=1 ./scripts/brain/setup-local.sh
# equivalent:
./scripts/brain/acceptance-automated.sh
```

4. **Hermes integration chat** — [§10.1](#hermes-integration-smoke) (start `hermes` after `hermes setup` if needed).
5. **Messaging (optional)** — [§16](#messaging): `./scripts/brain/setup-hermes-messaging.sh`; confirm **Gateway ready** before Telegram/WhatsApp capture.
6. **NB-SB1** — automated seam: `./scripts/brain/nb-sb1-probe.sh` (search must hit L3 James conjugation wiki path). Full agent answer: ask in LLM Wiki Agent or Hermes with citations; record in **Decisions** if waiving the probe.

Checklist mirror: [`docs/ACCEPTANCE-second-brain-hermes-v1.md`](../docs/ACCEPTANCE-second-brain-hermes-v1.md). Plan exit: [`seed_grow/plans/second-brain-hermes-v1-plan.md`](../seed_grow/plans/second-brain-hermes-v1-plan.md) **P8**.

<h2 id="messaging" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">16. Hermes messaging (Telegram / WhatsApp)</h2>

Phone chat uses the **Hermes gateway**, not LLM Wiki directly. For Second Brain, the Mac must still run **LLM Wiki** (MCP **`llm_wiki`**) so Hermes can query **`brain/wiki/`** and write captures to **`brain/raw/sources/<channel>/`** (Telegram is transport — not the **`chat/`** source folder; see **`ingest-to-brain`** skill).

<h3 id="messaging-prereq" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">16.1 Prerequisites</h3>

| Requirement | Notes |
|-------------|--------|
| Hermes installed | §10 — Desktop or CLI |
| P4 wiring | **`llm_wiki`** + **`second_brain_fs`** MCP ( **`./scripts/brain/setup-hermes-mcp.sh`** ) |
| LLM Wiki up | Project **`…/second_brain/brain`** open; API/MCP on (§5–§8) |
| Gateway running | Hermes Desktop shows **Gateway ready**, or **`hermes gateway`** / **`hermes gateway install`** (macOS user service) |

Official guides: [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) · [WhatsApp](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp) · guided **`hermes gateway setup`**.

<h3 id="messaging-one-time" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">16.2 One-time pairing (human)</h3>

**Telegram (recommended for Second Brain V1.1)**

1. Create bot via **@BotFather** (`/newbot`) **or** Hermes Desktop / dashboard **Messaging → Telegram → Create with QR** (writes token + your user id).
2. Put secrets in gitignored **`second_brain/.env`** (see **`.env.example`** `[hermes-sync]` messaging block) or only in **`~/.hermes/.env`**.
3. **`/start`** your bot in Telegram; optional **`/sethome`** in DM so cron/delivery knows the home chat.

**WhatsApp (Baileys bridge — unofficial; use a dedicated number)**

1. Run **`hermes whatsapp`** (or **`hermes gateway setup`** → WhatsApp) and scan QR on the **bot** phone.
2. Set **`WHATSAPP_ENABLED=true`**, **`WHATSAPP_MODE=bot`**, and **`WHATSAPP_ALLOWED_USERS`** (E.164 **without** `+`, comma-separated). See upstream doc for `*` / pairing behavior.

<h3 id="messaging-automation" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">16.3 Repo automation</h3>

```bash
cd /Users/jjw8053/projects/second_brain
# Copy messaging vars into .env from .env.example; fill tokens (never commit).
./scripts/brain/setup-hermes-messaging.sh
# Also runs from ./scripts/brain/setup-local.sh
```

What the script does:

1. **`apply-stack-config.sh`** — copies messaging keys listed in **`config/brain-stack.yaml`** → **`hermes.sync_env_keys`** into **`~/.hermes/.env`** (same as LLM/chat keys).
2. **`merge-hermes-wiring.py`** — refreshes managed block in **`~/.hermes/config.yaml`**:
   - **`mcp_servers`**: `llm_wiki`, `second_brain_fs`
   - **`platforms.telegram` / `platforms.whatsapp`**: `enabled: true` when env is complete; optional **`home_channel`** from **`TELEGRAM_HOME_CHANNEL`** / **`WHATSAPP_HOME_CHANNEL`** (preserves existing **`home_channel`** if env omits them).
3. Prints **`hermes gateway status`** when CLI is available.

Managed region markers (do not edit by hand between them):

```text
# --- second-brain wiring (scripts/brain/merge-hermes-wiring.py) ---
… mcp_servers …
… platforms …   # optional
# --- end second-brain wiring ---
```

<h3 id="messaging-smoke" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">16.4 Smoke from phone</h3>

1. Mac: LLM Wiki on **`brain`**, Hermes **Gateway ready**.
2. Telegram or WhatsApp: ask a **wiki** question (should use **`llm_wiki_*`** tools) or ask to **save research** → expect file under **`brain/raw/sources/web/`** (or **`uploads/`** for attachments), then Nashsu Source Watch → **`brain/wiki/`**.
3. If MCP fails from gateway: re-run **`./scripts/brain/apply-stack-config.sh`**, restart Desktop, or **`/reload-mcp`** in session.

**macOS gateway service:** if WhatsApp bridge reports Node missing while Terminal works, re-run **`hermes gateway install`** so launchd snapshots PATH (upstream troubleshooting).

---

<h2 id="future-script" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Idempotent driver</h2>

**In repo:** [`scripts/brain/setup-local.sh`](../scripts/brain/setup-local.sh) — Hermes ([`setup-hermes.sh`](../scripts/brain/setup-hermes.sh)), messaging ([`setup-hermes-messaging.sh`](../scripts/brain/setup-hermes-messaging.sh)), MCP when LLM Wiki app-state exists ([`setup-hermes-mcp.sh`](../scripts/brain/setup-hermes-mcp.sh)), Obsidian install hint, P8 optional via **`RUN_BRAIN_ACCEPTANCE=1`**.

**P8 automated:** [`scripts/brain/acceptance-automated.sh`](../scripts/brain/acceptance-automated.sh) — wiki page count, MCP smoke, `hermes mcp list`, `skills.disabled: llm-wiki`, [`nb-sb1-probe.sh`](../scripts/brain/nb-sb1-probe.sh).

**Still human-gated:** LLM Wiki GUI (open project, ingest, embeddings), Hermes interactive MCP chat (§10.1), NB-SB1 cited table lookup.
