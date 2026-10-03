<h1 id="runbook-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Second Brain — setup runbook (live log)</h1>

**Purpose:** Commands and manual steps to stand up Topology A (Mac). Intended to become an idempotent Python driver later.  
**Repos:** `second_brain/` (corpus + harness) · sibling `../nu_llm_wiki/` (Nashsu LLM Wiki from source).

## Document outline

1. [Prerequisites](#prereq) · 2. [Repo layout](#layout) · 3. [second_brain harness](#harness) · 4. [nu_llm_wiki from source](#nu-llm-wiki) · 5. [Manual in-app steps](#manual-app) · 6. [Hermes (pending)](#hermes) · 7. [Verification](#verify)

---

<h2 id="prereq" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Prerequisites</h2>

| Tool | Notes |
|------|--------|
| **Node.js** | **≥20.19** for Vite 8 / `nu_llm_wiki` (system `/usr/local` was 20.5.0 — too old). Portable **22.14** used: see §4. |
| **Xcode Command Line Tools** | Required for Rust/Tauri + Python. Unattended: `softwareupdate -i "Command Line Tools for Xcode-16.4" --agree-to-license` (or GUI `xcode-select --install`). |
| **protoc** | `brew install protobuf` (this host: libprotoc 3.21.9) |
| **Rust** | `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh -s -- -y` then `source "$HOME/.cargo/env"` (installed rustc 1.99.0) |
| **Python 3 + pytest** | For `./scripts/verify.sh` AC tests |

---

<h2 id="layout" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Repo layout</h2>

```text
/Users/jjw8053/projects/
├── second_brain/          # this repo — brain/ corpus, docs, bootstrap
└── nu_llm_wiki/           # git clone of nashsu/llm_wiki (renamed from ambiguous llm_wiki)
```

**LLM Wiki project folder (open in app):**  
`/Users/jjw8053/projects/second_brain/brain`

---

<h2 id="harness" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. second_brain harness (automated)</h2>

From repo root:

```bash
cd /Users/jjw8053/projects/second_brain
eval "$(bash bootstrap/core/scripts/parse-bootstrap-meta.sh bootstrap/specific/bootstrap.md)"
bash bootstrap/core/scripts/seed-harness.sh . "Second Brain" "Hermes + Nashsu" "$BOOTSTRAP_PROFILE"
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

**Clone + deps (run with Node 22 on PATH; reinstall after switching Node major):**

```bash
cd /Users/jjw8053/projects
git clone https://github.com/nashsu/llm_wiki.git nu_llm_wiki
cd nu_llm_wiki
npm install
npm --prefix mcp-server ci && npm run mcp:build
source "$HOME/.cargo/env"
npm run tauri dev           # NOT tauri build — requires Xcode CLT for linker
```

**Dev server (2026-10-03):** after CLT + Node 22, `npm run tauri dev` → API **`http://127.0.0.1:19828/api/v1`**, clip **`127.0.0.1:19827`**. First Rust build ~11m; leave terminal open.

**MCP server entry (after build):**  
`nu_llm_wiki/mcp-server/dist/src/index.js` (for Hermes `config.yaml` later).

**Dev run:** first `tauri dev` compiles Rust crates; keep terminal open. GUI window should open when ready.

---

<h2 id="manual-app" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Manual in-app steps (HG-2)</h2>

After LLM Wiki dev app is running:

1. **Open project** → `/Users/jjw8053/projects/second_brain/brain`
2. **Settings → LLM:** ingest + chat models; API keys in app UI only
3. **Settings → API + MCP:** enable API (`127.0.0.1:19828`), create token, enable MCP; copy MCP snippet paths
4. **Smoke:** drop `brain/raw/sources/uploads/smoke-test.md`; confirm ingest → `brain/wiki/`

Record token storage (password manager) — never commit.

---

<h2 id="hermes" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Hermes (pending P3–P4)</h2>

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
hermes doctor
hermes setup
```

Wire MCP (human edits `~/.hermes/config.yaml`):

```yaml
mcp_servers:
  llm_wiki:
    command: node
    args:
      - /Users/jjw8053/projects/nu_llm_wiki/mcp-server/dist/src/index.js
    env:
      LLM_WIKI_API_TOKEN: "<from LLM Wiki settings>"
```

Disable Hermes bundled `llm-wiki` compiler skill; use Nashsu skill:  
`npx skills add https://github.com/nashsu/llm_wiki_skill.git --skill llm-wiki`

---

<h2 id="verify" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Verification</h2>

```bash
cd /Users/jjw8053/projects/second_brain
./scripts/verify.sh
./scripts/verify-local.sh
# When LLM Wiki API up:
curl -sS -H "Authorization: Bearer TOKEN" "http://127.0.0.1:19828/api/v1/health"
```

---

<h2 id="future-script" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Future: idempotent driver</h2>

Sections marked **automated** above → shell/Python steps. Sections **manual in-app** → HG gates with `input()` or config file the human fills once (`~/.second_brain/local.yaml`).
