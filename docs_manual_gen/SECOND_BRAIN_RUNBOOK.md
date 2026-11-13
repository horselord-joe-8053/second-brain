<h1 id="runbook-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Second Brain — setup runbook (live log)</h1>

**Purpose:** Commands and manual steps to stand up Topology A (Mac). GUI setup for LLM Wiki is required today; automation is a later fork/driver.  
**Repos:** `second_brain/` (corpus + harness) · sibling `../nu_llm_wiki/` ([private LLM Wiki fork](https://github.com/horselord-joe-8053/llm-wiki)).

<h2 id="document-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Prerequisites](#prereq) — tools and versions.
2. [Repo layout](#layout) — paths on this host.
    2.1 [Brain profiles](#layout-profiles) — `personal` / `retail`, `BRAIN_PROFILE` switch.
3. [second_brain harness](#harness) — seed and verify.
4. [nu_llm_wiki from source](#nu-llm-wiki) — dev app and MCP build.
5. [Manual in-app steps (HG-2)](#manual-app) — project first, then settings.
6. [Secrets and config files](#secrets) — `.env` vs LLM Wiki app state.
7. [Embeddings (optional)](#embeddings) — vector search; lexical-only OK.
8. [Local API and MCP](#api-mcp) — token, curl, endpoints, Hermes snippet.
9. [Query path (MCP)](#query-path) — read path pointer.
10. [Harness runbooks](#harness-runbooks) — Hermes / OpenClaw (per-agent docs).
11. [Obsidian (HG-5)](#obsidian) — vault on compiled wiki.
12. [Backup](#backup) — rsync stub.
13. [Verification](#verify) — scripts and API smoke.
14. [Brain stack config](#brain-stack) — yaml overlay + apply script.
15. [After reboot + P8 acceptance (HG-8)](#p8-acceptance) — stack order, harness smoke, checklist.

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

**LLM Wiki project folders (open in app, one per brain-profile):**  
`/Users/jjw8053/projects/second_brain/brain/personal` · `/Users/jjw8053/projects/second_brain/brain/retail`

<h3 id="layout-profiles" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">2.1 Brain profiles (personal / retail)</h3>

`brain/` holds exactly two **brain-profiles** (each a full LLM Wiki project: `purpose.md`, `schema.md`, `raw/`, `wiki/`, `manifests/`). Exactly one is **active**; shared scripts derive every path from it.

| Profile | Root | Content |
|---------|------|---------|
| `retail` (default) | `brain/retail` | Fridges R Us manuals (`raw/sources/fridge-docs/`), PDF page index, answer-bundle contract |
| `personal` | `brain/personal` | Personal notes / proposals (previous single-brain tree) |

**Switch:** `BRAIN_PROFILE` env → `active_brain_profile` in `config/brain-stack.yaml` → `retail`. Scripts source `scripts/brain/brain-profile-env.sh`, which exports `BRAIN_PROFILE`, `BRAIN_ROOT`, `SECOND_BRAIN_WIKI_VAULT` (= `$BRAIN_ROOT/wiki`, also the Obsidian vault).

```bash
scripts/py scripts/brain/brain_stack.py profile-env          # show the active profile exports
BRAIN_PROFILE=personal ./scripts/brain/setup-obsidian.sh     # one-off run against the personal brain
```

The desktop apps keep their own state: switching profile in the repo does **not** re-point LLM Wiki or Obsidian — open the matching folder there by hand (HG-P2 in the brain-profiles plan).

---

<h2 id="harness" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. second_brain harness (automated)</h2>

From repo root:

```bash
cd /Users/jjw8053/projects/second_brain
eval "$(bash .cursor/skills/fabrication/scripts/parse-bootstrap-meta.sh seed_grow/bootstrap.md)"
bash .cursor/skills/fabrication/scripts/seed-harness.sh . "Second Brain" "Hermes + LLM Wiki" "$BOOTSTRAP_PROFILE"
bash .cursor/skills/fabrication/scripts/seed-scaffold-scripts.sh . general
bash .cursor/skills/fabrication/scripts/apply-module.sh . second-brain
bash .cursor/skills/fabrication/scripts/seed-product.sh .
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

**Day to day** (from `second_brain`; does not reinstall, and does not touch UI settings):

```bash
./scripts/brain/llm-wiki.sh start      # leaves the app alone if the API is already up
./scripts/brain/llm-wiki.sh status
./scripts/brain/llm-wiki.sh stop
./scripts/brain/llm-wiki.sh restart
```

That calls `../nu_llm_wiki/scripts/restart-dev.sh`. Hermes uses the skill **`local-llm-wiki`** (not the disabled compiler skill **`llm-wiki`**). Each status/start copies the token already saved in the UI into `.env`. It does not generate a new token.

**MCP entry (after build):**  
`/Users/jjw8053/projects/nu_llm_wiki/mcp-server/dist/src/index.js`

---

<h2 id="manual-app" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Manual in-app steps (HG-2)</h2>

<span style="background:#fff9c4;padding:2px 4px">GUI required</span> — no supported repo config file for LLM provider keys yet. Order matters:

1. **Start app** — first time: `npm run tauri dev` (§4). Later: `./scripts/brain/llm-wiki.sh start` from `second_brain`.
2. **Open or create project first** — **File → Open project** (or equivalent) → select the profile root,  
   `/Users/jjw8053/projects/second_brain/brain/personal` or `…/brain/retail` ([§2.1](#layout-profiles))  
   Many settings (Source Watch, per-project LLM overrides, `{id}` in API calls as `current`) assume a project is active. Do this **before** relying on API + MCP.
3. **Settings → LLM** — ingest + chat models and **provider API keys** (OpenAI, Gemini, Ollama, etc.). Stored in macOS app data (`app-state.json`), **not** in `second_brain/.env`.
4. **Settings → API + MCP** — enable **local HTTP API**, **Generate new token**, enable **MCP access**, **Save**. Copy token into local `.env` as `LLM_WIKI_API_TOKEN` (see §6) or a password manager — **never commit**.
5. **Smoke ingest (HG-2 exit)** — drop `brain/personal/raw/sources/uploads/smoke-test.md` (committed in repo). In the **native LLM Wiki window**, **Open project** → `…/second_brain/brain/personal` (required: ingest workers run in the UI, not via API alone). Ensure **Settings → Source Watch** has **auto-ingest** on for that project. Wait until activity finishes; expect new/updated pages under `brain/personal/wiki/` (not only `index.md`). Retail: open `…/brain/retail` and ingest `raw/sources/fridge-docs/**` the same way. Optional API assist after the project is open: `POST …/projects/current/sources/rescan` with bearer token.

**Ingest tip:** Source Watch queues **new or modified** files. If a file was already in the project snapshot before auto-ingest was enabled, use **Refresh folder** (Sources tab), the **book** icon on the row, or edit-and-save the source file to trigger a change.

---

<h2 id="secrets" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Secrets and config files</h2>

| What | Where | Consumed by |
|------|--------|-------------|
| OpenAI / Gemini **provider** keys and models | LLM Wiki **Settings → LLM** (+ optional embedding/search sections) | Desktop ingest, chat, Agent |
| Same keys for **Hermes** scripts (optional) | `second_brain/.env` (gitignored) — template **`.env.example`** | Future Hermes / repo scripts only |
| **Local API bearer** (not an LLM key) | LLM Wiki **Settings → API + MCP**; copy to **`LLM_WIKI_API_TOKEN`** in `.env` | `curl`, MCP `node …`, Hermes `config.yaml` |
| Shared MCP catalog | **`config/second-brain.mcp-servers.yaml`** | Harness-agnostic `llm_wiki` + `second_brain_fs` |
| Hermes MCP envelope | **`harness/adapters/hermes/mcp-servers.example.yaml`** | Managed block via **`merge-hermes-wiring.py`** (P4) |
| Telegram / WhatsApp | **`~/.hermes/.env`** (synced from repo `.env` when listed in **`hermes.sync_env_keys`**) | Hermes **gateway** (Desktop sidebar **Gateway ready** or **`hermes gateway`**) |
| Messaging `platforms:` | **`~/.hermes/config.yaml`** wiring block | **`merge-hermes-wiring.py`** when env vars are set (§16) |

The LLM Wiki app does **not** read `second_brain/.env` for ingest. Keep provider keys in the app UI; use `.env` for automation convenience on **this machine** only. **Never commit** bot tokens or API keys.

<h3 id="harness-hermes-openclaw" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">6.1 Harnesses (Hermes vs OpenClaw)</h3>

| Harness | `active_harness` | Scripts | Messaging |
|---------|------------------|---------|-----------|
| **Hermes** (default) | `hermes` | [`RUNBOOK_HARNESS_HERMES.md`](./RUNBOOK_HARNESS_HERMES.md) · `scripts/brain/adapters/hermes/` | `platforms:` in `~/.hermes/config.yaml` via **`merge-hermes-wiring.py`** |
| **OpenClaw** (skeleton) | `openclaw` | [`RUNBOOK_HARNESS_OPENCLAW.md`](./RUNBOOK_HARNESS_OPENCLAW.md) · `scripts/brain/adapters/openclaw/` | Channel schema TBD |

**Shared MCP:** [`config/second-brain.mcp-servers.yaml`](../config/second-brain.mcp-servers.yaml) — same catalog for every harness. **`apply-stack-config.sh`** dispatches merge scripts from **`config/brain-stack.yaml`** → **`active_harness`**.

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

Full catalog with filesystem MCP: **`config/second-brain.mcp-servers.yaml`**. Hermes merge envelope: **`harness/adapters/hermes/`**. Minimal shape:

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

<h2 id="query-path" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">9. Query path (MCP)</h2>

**Read path** (HERMES-3 / `query-brain`): compiled knowledge lives in **`brain/<profile>/wiki/`** ([§2.1](#layout-profiles)); agents should query via LLM Wiki API/MCP, not by scanning the whole tree in prompt context.

- **In app:** Chat / Agent tab on project **brain** (full UI retrieval loop).
- **For any MCP host (Hermes, Cursor, …):** tools `llm_wiki_set_project`, `llm_wiki_search`, `llm_wiki_read_file`, optional `llm_wiki_chat` — see [`MORE_SECOND_BRAIN_QUERY_HERMES_MCP.md`](./MORE_SECOND_BRAIN_QUERY_HERMES_MCP.md).
- **Preflight:** App running; **`brain`** is current project; bearer token in MCP env; embeddings optional (§7).

---

<h2 id="harness-runbooks" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">10. Harness runbooks</h2>

Shared driver (any harness):

```bash
./scripts/brain/agent.sh setup
```

Set **`active_harness`** in **`config/brain-stack.yaml`**, then open the matching runbook:

| Harness | Runbook | Adapter scripts |
|---------|---------|-------------------|
| **Hermes** (default) | [`RUNBOOK_HARNESS_HERMES.md`](./RUNBOOK_HARNESS_HERMES.md) | `scripts/brain/adapters/hermes/` |
| **OpenClaw** (skeleton) | [`RUNBOOK_HARNESS_OPENCLAW.md`](./RUNBOOK_HARNESS_OPENCLAW.md) | `scripts/brain/adapters/openclaw/` |

**P4 MCP (all harnesses):** shared catalog **`config/second-brain.mcp-servers.yaml`**. Harness-neutral read smoke: **`./scripts/brain/mcp-smoke-read.sh`**.

**Retail lane raw RAG (eval harness, not Hermes):** [`tests/retail_multi_profiles/docs/RAW_RAG.md`](../tests/retail_multi_profiles/docs/RAW_RAG.md).

From verify: `RUN_BRAIN_SETUP=1 ./scripts/verify-local.sh` runs **`agent.sh setup`** (via setup-local) before layout/pytest checks.

---

<h2 id="obsidian" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">11. Obsidian (HG-5)</h2>

**Recommended vault root:** `…/second_brain/brain/<profile>/wiki` (compiled Markdown only; `setup-obsidian.sh` uses the active profile). Alternative: the profile root `brain/<profile>/` if `.obsidian/` was generated there by LLM Wiki.

**Automated install (macOS + Homebrew):**

```bash
./scripts/brain/setup-obsidian.sh
OPEN_OBSIDIAN_VAULT=1 ./scripts/brain/setup-obsidian.sh   # also launch Obsidian on the vault
```

Also runs from **`./scripts/brain/agent.sh setup`** (`setup-local.sh`). Record the vault path in spec **Decisions** (HG-5) after first open.

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

Also runs at the start of **`./scripts/brain/agent.sh setup`**. **Does not** write LLM Wiki provider keys into the desktop app (GUI remains source for ingest).

<h2 id="p8-acceptance" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">15. After reboot + P8 acceptance (HG-8)</h2>

**Stack order (Mac):**

1. **LLM Wiki** — `./scripts/brain/llm-wiki.sh start` (no-op if already up). Project **`…/second_brain/brain`**, API/MCP on. UI settings stay in macOS app data.
2. **Obsidian** — vault **`…/second_brain/brain/wiki`** (already registered as **wiki**).
3. **Harness wiring** — `./scripts/brain/agent.sh setup` (uses **`active_harness`**). Hermes P8 automated: `RUN_BRAIN_ACCEPTANCE=1 ./scripts/brain/agent.sh setup` or [`adapters/hermes/acceptance-automated.sh`](../scripts/brain/adapters/hermes/acceptance-automated.sh).

4. **Harness integration chat** — [`RUNBOOK_HARNESS_HERMES.md`](./RUNBOOK_HARNESS_HERMES.md) §4 (Hermes Desktop smoke when `active_harness: hermes`).
5. **Messaging (optional, Hermes)** — same runbook §5; confirm **Gateway ready** before Telegram/WhatsApp capture.
6. **NB-SB1** — `./scripts/brain/nb-sb1-probe.sh` (automated search seam).

Checklist mirror: [`docs/ACCEPTANCE-second-brain-hermes-v1.md`](../docs/ACCEPTANCE-second-brain-hermes-v1.md). Plan exit: [`seed_grow/plans/second-brain-hermes-v1-plan.md`](../seed_grow/plans/second-brain-hermes-v1-plan.md) **P8**.

<h2 id="retail-fru" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">16. FRU US retail ticket brain (Postgres + Tantivy)</h2>

Default sim corpus **`fru_us_1k`** (`scripts/retail/sim_data/profiles/fru_us_1000_100/`). LLM Wiki project for manuals: **`…/second_brain/brain/retail`** (PDFs under `raw/sources/fridge-docs/`).

```bash
cd /Users/jjw8053/projects/second_brain
export RETAIL_SIM_DATA_PROFILE=fru_us_1k RETAIL_MARKET=US RETAIL_FAULT_CODE_PREFIX=FRU-E RETAIL_LEXICAL_BACKEND=tantivy
bash cursor_gen/retail_v11_prep/00_docker_ensure.sh
bash cursor_gen/retail_v11_prep/03_pg_up_and_load.sh
bash cursor_gen/retail_v11_prep/05_run_abc_postgres.sh
```

**Answer a new ticket** (`retail_answer.v1` JSON: top-2 similar resolved tickets with cosine + fused scores, plus manual hits cited as `raw/sources/fridge-docs/<sku>/<guide>.pdf p.N`):

```bash
scripts/py scripts/retail/answer/answer_ticket.py --query "RF28K9070SG ice maker not making ice" --postgres --md
scripts/py scripts/retail/answer/answer_ticket.py --query "…" --no-wiki --json   # CSV corpus, raw PDF pages only
```

Manual leg uses committed ``.txt`` under `brain/retail/raw/sources/fridge-docs/` (rebuild from archive PDFs: `scripts/py scripts/retail/manuals/build_pdf_txt_and_page_idx.py`, ~5 min; optional page JSONL with `WRITE_PAGE_INDEX=1`). Tests: CI `tests/retail/test_retail_answer_e2e.py` (in `verify.sh`); live `RUN_RETAIL_E2E=1 scripts/py -m pytest -q tests/retail/test_retail_answer_live.py -s` (Postgres + Gemini + LLM Wiki after **HG-TXT-2**).

Spec: [`docs/specs/fru-us-service-synthetic-data.md`](../docs/specs/fru-us-service-synthetic-data.md). Prep split: [`cursor_gen/retail_v11_prep/CURSOR_PREP_RUNBOOK.md`](../cursor_gen/retail_v11_prep/CURSOR_PREP_RUNBOOK.md) · [`HERMES_WIKI_OPERATOR.md`](../cursor_gen/retail_v11_prep/HERMES_WIKI_OPERATOR.md).

<h2 id="future-script" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Idempotent driver</h2>

**In repo:** [`scripts/brain/agent.sh`](../scripts/brain/agent.sh) **`setup`** → [`setup-local.sh`](../scripts/brain/setup-local.sh) — shared stack + **`adapters/<active_harness>/setup-harness.sh`**, Obsidian hint, optional **`RUN_BRAIN_ACCEPTANCE=1`** (Hermes: [`acceptance-automated.sh`](../scripts/brain/adapters/hermes/acceptance-automated.sh)). Daily launch: **`agent.sh start`**.

**Process up/down:** `./scripts/brain/llm-wiki.sh` and Hermes skill **`local-llm-wiki`**. **Still human-gated:** first-time LLM Wiki GUI (§5–§8: provider keys, enabling API), harness-specific chat smoke (per harness runbook), NB-SB1 cited table lookup in agent UI.
