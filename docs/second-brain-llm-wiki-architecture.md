<h1 id="doc-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Second Brain architecture: LLM Wiki, Nashsu, and agent harnesses</h1>

**Extracted from:** [ChatGPT share — Rank LLM Wiki Projects](https://chatgpt.com/share/6ac0a93d-aee4-83e8-bb20-02de4c2dbbd2) (conversation as of **3 October 2026**).  
**Full machine transcript:** `utils/chatgpt/transcripts/rank_llm_wiki_projects_6ac0a93d-aee4-83e8-bb20-02de4c2dbbd2.txt` (via `utils/chatgpt/playwright/fetch_share.mjs`).  
**Note:** Web-search tool outputs in the original chat are redacted in the share export; rankings and star counts reflect the assistant’s research at conversation time, not live GitHub metrics.

<h2 id="document-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Baseline architecture](#1-baseline-architecture) — agreed “Second Brain” design.
    1.1 [Final baseline confirmation](#11-final-baseline-confirmation) — full diagrams, coupling rules, harness swap.
2. [Open-source landscape](#2-open-source-landscape) — LLM Wiki vs RAG/NotebookLM (Oct 2026).
3. [Roles of Obsidian, Notion, NotebookLM](#3-roles-of-obsidian-notion-notebooklm) — what belongs in the core loop.
4. [Knowledge compilation ownership](#4-knowledge-compilation-ownership) — Nashsu vs Hermes-built-in Wiki.
5. [Hermes stages (HERMES-1…4)](#5-hermes-stages-hermes-14) — numbered orchestration loop.
6. [Ingestion adapter](#6-ingestion-adapter) — capture, not “LLM everything to Markdown.”
7. [Storage and deployment (V1)](#7-storage-and-deployment-v1) — VM disk, Google Drive, Hostinger sketch.
8. [Agent harness replaceability](#8-agent-harness-replaceability) — Hermes default; OpenClaw, DSH, Pi, others.
9. [Existing Nashsu integrations](#9-existing-nashsu-integrations) — skills, MCP, what to build vs reuse.
10. [Hermes built-in skill vs Nashsu stack](#10-hermes-built-in-skill-vs-nashsu-stack) — do not run two compilers.
11. [Wiki compiler (plain language)](#11-wiki-compiler-plain-language) — who does compilation.
12. [LLM configuration in Nashsu](#12-llm-configuration-in-nashsu) — models and API keys.
13. [Performance trade-offs](#13-performance-trade-offs) — cost, latency, duplication.
14. [Second-Brain contract](#14-second-brain-contract) — portable boundary across harnesses.
15. [Open risks and next investigations](#15-open-risks-and-next-investigations) — scaling and headless deploy.
16. [Reference links](#16-reference-links) — primary repos and skills.
17. [Implementation plan](#17-implementation-plan) — phased Hermes + Nashsu rollout in this repo.

---

<h2 id="1-baseline-architecture" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Baseline architecture</h2>

The conversation converges on a **Karpathy-style LLM Wiki**: a **persistent, LLM-maintained, human-readable knowledge base** (not merely “chat with my documents”).

**One-sentence summary:**

> **Google Drive and other systems hold evidence → a personal agent harness acquires and orchestrates it → `nashsu/llm_wiki` compiles durable Markdown knowledge → Obsidian is the human UI → MCP/API exposes the brain back to the harness → the harness reasons and acts, producing new evidence that feeds the compiler again.**

**Baseline stack to implement and test first:**

```text
sources → nashsu/llm_wiki → Markdown → Obsidian → MCP → Hermes (default harness) → actions
```

**Role metaphor (conversation):**

| Role | Component |
|------|-----------|
| Brain builder / maintainer | `nashsu/llm_wiki` + configured LLM(s) |
| Window on the brain | Obsidian |
| Hands, feet, personal assistant | Agent harness (Hermes default; OpenClaw / DSH swappable) |

See [§1.1 Final baseline confirmation](#11-final-baseline-confirmation) for the **authoritative** closing diagrams and coupling table from the last assistant turn.

<h3 id="11-final-baseline-confirmation" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">1.1 Final baseline confirmation</h3>

**User question (final turn):** Confirm that the best viable architecture matches the Nashsu + Obsidian + harness split above, with **Hermes as default** for orchestration/ingestion/action roles working with Nashsu, but **flexibility to swap** OpenClaw or DSH.

**Answer:**

> Yes. **That is the architecture to treat as the baseline for this Second Brain project.**

**Reference architecture (full diagram from chat):**

```text
                         SECOND BRAIN
══════════════════════════════════════════════════════════════

                     SOURCE WORLD
          Drive • Gmail • GitHub • Web • Chat
                          │
                          ▼
            ╔═══════════════════════════╗
            ║  PERSONAL AGENT HARNESS   ║
            ║                           ║
            ║  ★ Hermes — DEFAULT      ║
            ║    OpenClaw — swappable   ║
            ║    DSH — swappable        ║
            ╚═════════════╤═════════════╝
                          │
                   acquire / sync
                   provenance / delta
                          │
                          ▼
                 ┌─────────────────┐
                 │  RAW EVIDENCE   │
                 │  raw/sources/   │
                 └────────┬────────┘
                          │
                          ▼
            ╔═══════════════════════════╗
            ║   KNOWLEDGE CORE          ║
            ║                           ║
            ║   nashsu/llm_wiki        ║
            ║          +                ║
            ║   configured LLM(s)       ║
            ║                           ║
            ║ analyze • reconcile       ║
            ║ synthesize • maintain     ║
            ║ graph • provenance        ║
            ╚═════════════╤═════════════╝
                          │
                          ▼
                 ┌─────────────────┐
                 │ COMPILED BRAIN  │
                 │    Markdown     │
                 └───────┬─────────┘
                         │
                 ┌───────┴─────────┐
                 │                 │
                 ▼                 ▼
            ┌─────────┐        MCP / API
            │Obsidian │             │
            └────┬────┘             ▼
                 │       ╔═══════════════════════════╗
              HUMAN      ║  PERSONAL AGENT HARNESS   ║
              ACCESS     ║                           ║
                         ║  ★ Hermes — DEFAULT      ║
                         ║    OpenClaw — swappable   ║
                         ║    DSH — swappable        ║
                         ╚═════════════╤═════════════╝
                                       │
                         reason • research • act
                                       │
                              new evidence?
                                       │
                                       └────► RAW EVIDENCE
                                                 │
                                              [loop]
```

The critical design principle is **where coupling is allowed**:

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Component</th><th>Default</th><th>Replaceability</th><th>Should knowledge depend on it?</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">🧠 Knowledge compiler</td><td style="background:#e8f5e9"><strong>Nashsu LLM Wiki</strong></td><td style="background:#fff3e0">Possible, but core</td><td style="background:#e8f5e9"><span style="background:#c8e6c9;padding:2px 4px">Yes</span></td></tr>
<tr><td style="background:#e3f2fd">📚 Knowledge representation</td><td style="background:#e8f5e9"><strong>Markdown + raw evidence</strong></td><td style="background:#e8f5e9"><span style="background:#c8e6c9;padding:2px 4px">Open format</span></td><td style="background:#e8f5e9"><span style="background:#c8e6c9;padding:2px 4px">Yes — durable asset</span></td></tr>
<tr><td style="background:#e3f2fd">👁 Human UI</td><td style="background:#e8f5e9"><strong>Obsidian</strong></td><td style="background:#e8f5e9"><span style="background:#c8e6c9;padding:2px 4px">Easy</span></td><td style="background:#ffebee"><span style="background:#ffcdd2;padding:2px 4px">No</span></td></tr>
<tr><td style="background:#e3f2fd">🤖 Agent harness</td><td style="background:#fff3e0"><strong>Hermes</strong></td><td style="background:#e8f5e9"><span style="background:#c8e6c9;padding:2px 4px">Designed to swap</span></td><td style="background:#ffebee"><span style="background:#ffcdd2;padding:2px 4px">No</span></td></tr>
<tr><td style="background:#e3f2fd">🤖 Alternative harness</td><td style="background:#fff3e0">OpenClaw</td><td style="background:#e8f5e9"><span style="background:#c8e6c9;padding:2px 4px">Yes</span></td><td style="background:#ffebee"><span style="background:#ffcdd2;padding:2px 4px">No</span></td></tr>
<tr><td style="background:#e3f2fd">🤖 Alternative harness</td><td style="background:#fff3e0">DSH</td><td style="background:#e8f5e9"><span style="background:#c8e6c9;padding:2px 4px">Yes</span></td><td style="background:#ffebee"><span style="background:#ffcdd2;padding:2px 4px">No</span></td></tr>
<tr><td style="background:#e3f2fd">🧠 Models</td><td style="background:#fff3e0">OpenAI / Claude / Gemini / local etc.</td><td style="background:#e8f5e9"><span style="background:#c8e6c9;padding:2px 4px">Yes</span></td><td style="background:#ffebee"><span style="background:#ffcdd2;padding:2px 4px">No single model</span></td></tr>
<tr><td style="background:#e3f2fd">🔌 Agent boundary</td><td style="background:#e8f5e9"><strong>MCP/API + portable skills</strong></td><td style="background:#e8f5e9"><span style="background:#c8e6c9;padding:2px 4px">Yes</span></td><td style="background:#fff3e0">—</td></tr>
</tbody>
</table>

<h4 id="why-hermes-default" style="color:#00695c;font-size:1em;font-weight:600;margin-top:0.75em">Why Hermes remains the default</h4>

Not because Hermes should “own” the Second Brain.

It is the default because it currently combines, in one place:

**personal-agent behavior + connectors + skills + scheduling + research + model choice + MCP + actions.**

All of that sits **outside the durable knowledge core**. Harness choice (Hermes vs OpenClaw vs DSH) is therefore **much less consequential to Second Brain durability** than choosing Nashsu + Markdown + raw evidence as the knowledge core.

**Harness swap without migrating the brain (example: DSH wins in two years):**

```text
TODAY

Hermes
  │
  ├── ingestion
  │
  ▼
Nashsu ──► Wiki
  │
 MCP
  ▼
Hermes


LATER

DSH
 │
 ├── ingestion
 │
 ▼
Nashsu ──► SAME Wiki
 │
MCP
 ▼
DSH
```

Raw sources, compiled knowledge, relationships, and Markdown **do not** need a full migration merely because the agent harness changes. That portability is a major architectural advantage.

**Second-Brain contract (preferred boundary — not verbatim portability of every Hermes skill):**

```text
            SECOND-BRAIN CONTRACT
─────────────────────────────────────────
INPUT
  acquire source
       ↓
  raw/sources/

KNOWLEDGE
  nashsu/llm_wiki
       ↓
  Markdown Wiki

AGENT INTERFACE
  MCP / API

WORKFLOWS
  ingest-to-brain
  query-brain
  audit-brain
  research-gap
─────────────────────────────────────────
          ▲        ▲        ▲
          │        │        │
       Hermes   OpenClaw   DSH
```

Each harness only needs a **thin adapter** to those four workflow families (plus the INPUT / KNOWLEDGE / AGENT INTERFACE layers above).

**Architectural decision (summary quote):**

> **Nashsu owns knowledge. Obsidian presents knowledge. Hermes orchestrates the world around knowledge. Hermes is the default harness, but OpenClaw and DSH remain replaceable implementations behind a small Second-Brain contract.**

This is stronger than the early Hermes-heavy design because **the most valuable asset—the accumulated brain—has the least dependency on whichever agent framework wins.**

**Optional follow-ups mentioned in chat (not expanded in the share):**

- Detail key benefits of Hermes as default agent harness
- Summarize architectural advantages of agent harness replaceability
- Outline implementation steps to integrate OpenClaw or DSH

---

<h2 id="2-open-source-landscape" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Open-source landscape</h2>

Separate **true LLM Wiki / knowledge-compiler** projects from **RAG / NotebookLM-style** tools so star rankings stay meaningful.

**Shortlist (GitHub popularity snapshot, Oct 3 2026 — from conversation):**

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Rank</th><th>Project</th><th>Stars (approx.)</th><th>Recent growth (approx.)</th><th>What it is</th><th>Fit to LLM Wiki goal</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">1</td><td style="background:#e8f5e9"><a href="https://github.com/nashsu/llm_wiki">nashsu/llm_wiki</a></td><td style="background:#e8f5e9">20.1k</td><td style="background:#e8f5e9">+186 / 7d; +17 / 24h</td><td style="background:#e8f5e9">Persistent LLM-maintained wiki</td><td style="background:#e8f5e9"><span style="background:#2e7d32;color:white;padding:1px 4px">Excellent</span></td></tr>
<tr><td style="background:#e3f2fd">2</td><td style="background:#fff3e0"><a href="https://github.com/infiniflow/ragflow">RAGFlow</a></td><td style="background:#fff3e0">91.6k</td><td style="background:#fff3e0">+369/week</td><td style="background:#fff3e0">RAG + Knowledge Compilation (wikis, graphs, timelines, Aug 2026)</td><td style="background:#fff3e0">Very good, heavier</td></tr>
<tr><td style="background:#e3f2fd">3</td><td style="background:#fff3e0"><a href="https://github.com/Mintplex-Labs/anything-llm">AnythingLLM</a></td><td style="background:#fff3e0">66.6k</td><td style="background:#fff3e0">+300/week</td><td style="background:#fff3e0">Local AI workspace / RAG / agents</td><td style="background:#fff3e0">Moderate</td></tr>
<tr><td style="background:#e3f2fd">4</td><td style="background:#fff3e0"><a href="https://github.com/lfnovo/open-notebook">Open Notebook</a></td><td style="background:#fff3e0">39.7k</td><td style="background:#fff3e0">+262/week</td><td style="background:#fff3e0">Open NotebookLM replacement</td><td style="background:#fff3e0">Moderate</td></tr>
<tr><td style="background:#e3f2fd">5</td><td style="background:#fff3e0"><a href="https://github.com/khoj-ai/khoj">Khoj</a></td><td style="background:#fff3e0">37.5k</td><td style="background:#fff3e0">+108/week</td><td style="background:#fff3e0">AI second brain / RAG / agents</td><td style="background:#fff3e0">Good (overlaps agent layer)</td></tr>
<tr><td style="background:#e3f2fd">6</td><td style="background:#fff3e0"><a href="https://github.com/MODSetter/SurfSense">SurfSense</a></td><td style="background:#fff3e0">16.3k</td><td style="background:#fff3e0">+107/week</td><td style="background:#fff3e0">NotebookLM / research + connectors</td><td style="background:#fff3e0">Moderate</td></tr>
</tbody>
</table>

**Primary recommendation:** evaluate **`nashsu/llm_wiki` first** — closest ready-made match to the discussed architecture (April 2026 launch, strong star velocity in the chat’s snapshot).

**Secondary bake-off:** same corpus through **RAGFlow Knowledge Compilation** and compare whether output is a **long-lived incrementally maintained** artifact vs a generated view of a dataset.

**Deprioritize:** small literal Karpathy clones (e.g. `ddsyasas/llm-wiki` ~56 stars in chat).

**`nashsu/llm_wiki` design highlights:**

- Pipeline: **documents → LLM analysis → persistent structured wiki → incremental maintenance** (not chunk-embed-answer-only RAG).
- Layout aligns with a compiler mental model: `purpose.md`, `schema.md`, `raw/sources/`, `wiki/` (entities, concepts, synthesis, …), `.obsidian/`, `.llm-wiki/`.
- Formats: PDF, DOCX, Markdown, EPUB/MOBI, images, URLs, Office; separate models for ingest vs chat; **local MCP server** and agent skill for Claude Code / Codex-style runtimes.

**Suggested acceptance tests before committing:**

- Claims in a career/skills page unsupported by primary sources?
- Important concepts from a paper corpus missing from the wiki?
- Contradictions between wiki and sources?
- Outdated beliefs vs newer sources?

---

<h2 id="3-roles-of-obsidian-notion-notebooklm" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Roles of Obsidian, Notion, NotebookLM</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Product</th><th>Architectural role</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>LLM Wiki (Nashsu)</strong></td><td style="background:#e8f5e9">Knowledge compiler + persistent knowledge layer</td></tr>
<tr><td style="background:#e3f2fd"><strong>Obsidian</strong></td><td style="background:#e8f5e9">Human wiki UI/editor (vault = ordinary files)</td></tr>
<tr><td style="background:#e3f2fd">Notion</td><td style="background:#fff3e0">Optional source or UI; poorer fit as canonical store vs Markdown-on-disk</td></tr>
<tr><td style="background:#e3f2fd">NotebookLM</td><td style="background:#ffebee">Ad-hoc source-grounded research — <strong>not</strong> in core pipeline</td></tr>
<tr><td style="background:#e3f2fd">Agent harness</td><td style="background:#e8f5e9">Orchestration, ingestion, actions</td></tr>
</tbody>
</table>

**NotebookLM vs LLM Wiki (conceptual):**

```text
NotebookLM:  sources → retrieve → answer (no durable compiled middle)

LLM Wiki:    sources → understand → reconcile → WRITE/UPDATE wiki → … → wiki
```

**Obsidian integration:** yes — as **human interface** to compiled Markdown; LLM Wiki keeps intelligence. Nashsu can emit `.obsidian/` for the vault.

---

<h2 id="4-knowledge-compilation-ownership" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Knowledge compilation ownership</h2>

**Correction from early diagrams:** **`nashsu/llm_wiki` owns most of the Knowledge Compilation layer.** The harness sits *around* it — not the routine wiki editor.

**Formal definition:**

> **Knowledge Compilation Layer = `nashsu/llm_wiki` + its configured LLM(s).**

**Nashsu maintenance loop (when a new artifact lands in `raw/sources/`):**

```text
new file
   → auto-watch + ingest queue + SHA-256 dedup
   → parse
   → STEP 1 ANALYSIS (entities, concepts, relations, contradictions, link to existing wiki)
   → STEP 2 GENERATION (update/create pages, provenance, index/log, review items)
```

**Responsibility split (compiler vs harness):**

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Responsibility</th><th>Nashsu</th><th>Harness (Hermes, etc.)</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Parse, extract, reconcile, update wiki, graph, review, lint, search</td><td style="background:#e8f5e9"><span style="background:#c8e6c9;padding:2px 4px">Core</span></td><td style="background:#ffebee"></td></tr>
<tr><td style="background:#e3f2fd">Acquire from Drive/Gmail/GitHub/chat/web</td><td style="background:#ffebee"></td><td style="background:#e8f5e9"><span style="background:#c8e6c9;padding:2px 4px">Core</span></td></tr>
<tr><td style="background:#e3f2fd">Intent routing, orchestration, actions, proactive research</td><td style="background:#ffebee"></td><td style="background:#e8f5e9"><span style="background:#c8e6c9;padding:2px 4px">Core</span></td></tr>
<tr><td style="background:#e3f2fd">Feed discovered evidence back to <code>raw/sources/</code></td><td style="background:#ffebee"></td><td style="background:#e8f5e9">Yes</td></tr>
</tbody>
</table>

**Estimate from chat:** Nashsu may remove **~70–80%** of custom knowledge-compilation engineering (architectural estimate, not a benchmark). Remaining custom work: **connectors, lifecycle reliability, auditing/supervision, harness workflows**.

---

<h2 id="5-hermes-stages-hermes-14" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Hermes stages (HERMES-1…4)</h2>

Number **harness involvement by logical stage** (`★ HERMES-n ★`), not as a single static box.

| Stage | Name | Job |
|------:|------|-----|
| **1** | Personal interface | Understand intent; route “summarize this” vs “add to Second Brain” |
| **2** | Acquisition / ingestion | Sync, provenance, delta, materialize into `raw/sources/` |
| — | *(not harness)* | **LLM Wiki compiles** — harness deliberately steps aside |
| **3** | Knowledge consumer | Query/reason/audit/synthesize via MCP/API over compiled wiki |
| **4** | Research / gap closure | Find/acquire evidence → back to raw corpus → recompile → loop to 3 |

**Compact loop:**

```text
YOU → ★1★ → ★2★ → RAW → LLM WIKI → COMPILED → Obsidian + MCP → ★3★ → (gap?) ★4★ → RAW …
```

---

<h2 id="6-ingestion-adapter" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Ingestion adapter</h2>

**Rule:**

> **Harness gets knowledge *to* LLM Wiki. LLM Wiki decides what that knowledge *does to* the wiki.**

Rename “normalize” → **`capture + adapt`** or **`ingestion adapter`**.

- Harness orchestrates **deterministic tools** (fetch, export, MIME, hashing) — not “LLM-rewrite every PDF to Markdown.”
- If Nashsu parses PDF/DOCX/EPUB natively, prefer **original artifact** in `raw/sources/` (tables, images, provenance).
- Hermes **must not** merge concepts into `wiki/` pages; that is compilation.

**Google Workspace nuance:**

- **Read for Q&amp;A:** Docs/Sheets APIs — direct read, no export required.
- **Ingest into Second Brain:** materialize a **snapshot** into `raw/sources/` because LLM Wiki watches a **local immutable corpus** (with source ID, revision, Drive URL, etc.).

**Source envelope / manifest (design homework):** stable `source_id`, URI, version, hash, capture time, type, parent/child — so Drive, Gmail, GitHub, chat, and uploads behave consistently.

**Storage tiers (conceptual):**

```text
VM disk     = working corpus (raw/sources + wiki) — LLM Wiki works here
Object store = S3/R2/MinIO — durable blob archive (optional later)
Database    = metadata/state — not primary home for PDFs
```

**V1 recommendation:** skip S3/R2/MinIO; use **Google Drive as durable archive/backup** while **VM disk is the live working copy**. Rebuild VM from Drive if needed.

---

<h2 id="7-storage-and-deployment-v1" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Storage and deployment (V1)</h2>

Sketch for **~$15/mo Hostinger VPS** (Ubuntu 24.04 + Docker) — **Hermes deployment location is flexible** (local, AWS, etc.); this is one option from the chat.

**Do not install yet (V1):** Kubernetes, Kafka, Airflow, MinIO, separate vector DB, Postgres/Redis unless a concrete need appears.

**Suggested layout:**

```text
/srv/second-brain/
  raw/sources/{personal,uploads,drive,gmail,github,web,chat}
  wiki/
  manifests/
  archive/
  backup/

/home/james/.hermes/   ← agent state (separate from corpus)
```

**Google Drive:**

- `My Second Brain/Raw Archive/` — originals without another durable home
- `My Second Brain/Backups/` — **versioned** backup of `wiki/` (compiled brain is the long-term asset)

**Critical open deployment question:** `nashsu/llm_wiki` is **Tauri desktop-first** (Linux `.deb`/AppImage). Verify **headless** compiler/watch/API/MCP on Ubuntu **before** assuming `Hermes container + LLM-Wiki container`. May require LLM Wiki on Mac/PC and harness on VPS until headless story is clear.

**Everyday flow (target UX):** message harness (e.g. Telegram) “add to my brain” → hash/dedup/provenance → optional Drive archive → write under `raw/sources/` → LLM Wiki watcher → compiled `wiki/*.md` → Obsidian + MCP.

---

<h2 id="8-agent-harness-replaceability" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. Agent harness replaceability</h2>

**Test for replacement:** can the harness cover **① intent → ② acquisition → (LLM Wiki) → ③ query/act via MCP → ④ gap research → raw sources**?

<h3 id="81-initial-six-harnesses" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">8.1 Initial six harnesses (Oct 3 2026)</h3>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Rank</th><th>Harness</th><th>Replace Hermes?</th><th>Notes (from chat)</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">1</td><td style="background:#e8f5e9">OpenClaw 2.0+</td><td style="background:#e8f5e9">Yes, easily</td><td style="background:#e8f5e9">Self-host, MCP, SKILL.md, plugins, automations; closest substitute; Hermes <code>hermes claw migrate</code> imports OpenClaw config</td></tr>
<tr><td style="background:#e3f2fd">2</td><td style="background:#fff3e0">Claude / Cowork</td><td style="background:#fff3e0">Mostly</td><td style="background:#fff3e0">Remote MCP to LLM Wiki strong; weaker on owned ingestion/fs vs Hermes/OpenClaw</td></tr>
<tr><td style="background:#e3f2fd">3</td><td style="background:#fff3e0">Grok Bot</td><td style="background:#fff3e0">Mostly</td><td style="background:#fff3e0">Strong action/cloud computer; less open as long-term control plane</td></tr>
<tr><td style="background:#e3f2fd">4</td><td style="background:#fff3e0">OpenAI Dots</td><td style="background:#fff3e0">Potentially</td><td style="background:#fff3e0">Very new; watch, don’t architect core on it yet</td></tr>
<tr><td style="background:#e3f2fd">5</td><td style="background:#ffebee">Meta Muse</td><td style="background:#ffebee">Partial</td><td style="background:#ffebee">Managed personal agent, not open programmable harness around your corpus</td></tr>
</tbody>
</table>

**First-class harness targets for this project:** **Hermes + OpenClaw**; Claude/Cowork via remote MCP; DSH/Pi added in a later turn (below).

<h3 id="82-dsh-and-pi-oct-2026" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">8.2 DeepSeek Harness (DSH) and Pi (Oct 2026)</h3>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Rank</th><th>Harness</th><th>Second Brain fit (chat)</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">1</td><td style="background:#e8f5e9">DeepSeek Harness</td><td style="background:#e8f5e9">Excellent architecture (“everything is a plugin”, <code>dsh-mcp-client</code>); immature runtime / preview breakage</td></tr>
<tr><td style="background:#e3f2fd">2</td><td style="background:#e8f5e9">OpenClaw 2.x</td><td style="background:#e8f5e9">Best mature personal-agent fit</td></tr>
<tr><td style="background:#e3f2fd">3</td><td style="background:#fff3e0">Hermes</td><td style="background:#fff3e0">Very good / simple</td></tr>
<tr><td style="background:#e3f2fd">4</td><td style="background:#fff3e0">Pi</td><td style="background:#fff3e0">Excellent DIY foundation; assembly required</td></tr>
</tbody>
</table>

**Principle:**

> **LLM Wiki remains the brain; DSH/Hermes/OpenClaw/Pi remain replaceable nervous systems.** Do not bind durable knowledge to DSH-specific APIs during preview instability.

**Serious experimentation shortlist (chat):** OpenClaw, DSH, Hermes; Pi as underlying DIY runtime, not default finished product.

---

<h2 id="9-existing-nashsu-integrations" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">9. Existing Nashsu integrations</h2>

Search target: integrations with **`nashsu/llm_wiki` specifically**, not generic Karpathy wiki repos.

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Harness</th><th>Existing integration</th><th>Uses Nashsu app?</th><th>Recommendation (chat)</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Hermes</td><td style="background:#e8f5e9">Bundled LLM Wiki research skill + Nashsu MCP/skill ecosystem</td><td style="background:#e8f5e9">Yes / compatible</td><td style="background:#e8f5e9">Use Nashsu official skill + MCP; don’t rebuild agent↔wiki wire-up</td></tr>
<tr><td style="background:#e3f2fd">OpenClaw</td><td style="background:#e8f5e9">SKILL.md + MCP; community skills</td><td style="background:#e8f5e9">Can use Nashsu directly</td><td style="background:#e8f5e9">Nashsu official skill + MCP</td></tr>
<tr><td style="background:#e3f2fd">DeepSeek Harness</td><td style="background:#fff3e0">Native <code>llm-wiki</code> plugins (often separate implementations)</td><td style="background:#fff3e0">Mostly no</td><td style="background:#fff3e0">Connect Nashsu via MCP, don’t substitute DSH wiki plugins for Nashsu compiler</td></tr>
</tbody>
</table>

**Portable boundary:** standardize on **`SKILL.md` + MCP + raw-source contract** so switching Hermes ⇄ OpenClaw ⇄ DSH is mostly adapter work. Custom work concentrates on **ingestion workflows**, not agent↔wiki plumbing.

**Packaged Second Brain shape (conceptual):**

```text
second-brain/
  ingestion/{drive,gmail,github,web}
  skills/{ingest-to-brain,audit-brain,research-gap}
  mcp/llm-wiki
```

---

<h2 id="10-hermes-built-in-skill-vs-nashsu-stack" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">10. Hermes built-in skill vs Nashsu stack</h2>

**They are not the same thing:**

| Piece | What it is | Who compiles? |
|-------|------------|---------------|
| [Hermes `llm-wiki` skill](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/llm-wiki/SKILL.md) | ~500-line procedure: Hermes builds/maintains Markdown wiki | **Hermes** |
| [hermes_LLMwiki_Obsidian](https://github.com/zianCAU/hermes_LLMwiki_Obsidian) | Opinionated Hermes + Obsidian second-brain workflow | **Hermes** |
| [nashsu/llm_wiki_skill](https://github.com/nashsu/llm_wiki_skill) | Thin API/MCP instructions | **`nashsu/llm_wiki` app** |

**`hermes_LLMwiki_Obsidian`:** related ecosystem, **not** a hard dependency of the bundled Hermes skill.

**Capability comparison (summary):** Nashsu app wins on ingest queue, watch, hybrid retrieval, LanceDB, graph/Louvain, native review, HTTP API, **native MCP**, compiler independent of harness. Hermes built-in skill is capable but **couples compiler to harness**.

**For the HERMES-1…4 architecture:** bundled Hermes `llm-wiki` skill can cover many stages technically, but **architecturally avoid it** when Nashsu is the canonical compiler.

**Do not run two compilers:**

```text
WRONG: Hermes llm-wiki skill AND Nashsu both editing wiki/

RIGHT: Harness → raw/sources → Nashsu only → compiled wiki → MCP → harness
```

| Component | Use for this project? |
|-----------|----------------------|
| Hermes harness | Yes (default) |
| Hermes bundled `llm-wiki` skill | **Disable / avoid** (duplicates compiler) |
| `hermes_LLMwiki_Obsidian` as core | No (borrow ideas only) |
| `nashsu/llm_wiki` | **Yes — canonical compiler** |
| `nashsu/llm_wiki_skill` + Nashsu MCP | **Yes** |
| Custom ingestion skills | Yes (connectors → raw) |

**Nashsu skill caveat:** documented skill surface is **mostly read-only** (search, read, graph, rescan); **adding knowledge** = drop files in `raw/sources/` (or rescan), not direct wiki rewrite via skill alone. Richer write paths go through Nashsu’s own ingest pipeline and MCP agent chat/review flows.

---

<h2 id="11-wiki-compiler-plain-language" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">11. Wiki compiler (plain language)</h2>

**Wiki compiler** = component that reads raw material and produces/maintains the organized, linked wiki (architectural term; not necessarily a Nashsu class name).

| Approach | Wiki compiler is… |
|----------|-------------------|
| Hermes `llm-wiki` skill | **Hermes** (skill = “you translate yourself”) |
| Nashsu stack | **`nashsu/llm_wiki` application** (skill = “here’s how to use Google Translate”) |

**Analogy:** Hermes-with-skill = assistant translating by textbook; Nashsu = assistant operating **Google Translate** (`nashsu/llm_wiki`).

---

<h2 id="12-llm-configuration-in-nashsu" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">12. LLM configuration in Nashsu</h2>

Yes — **`nashsu/llm_wiki` calls LLMs** for analysis and generation. Configure **provider, API key, model** in app settings (chat cites support for OpenAI, Anthropic, Google, Ollama, custom endpoints; separate ingest vs chat model selection).

Harness does **not** need to supply compilation intelligence unless you deliberately use Hermes-as-compiler ( rejected architecture).

Nashsu API described as **localhost + token** for external agents — compiler stays an independent service.

---

<h2 id="13-performance-trade-offs" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">13. Performance trade-offs</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Downside</th><th>Impact</th><th>Comment</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Extra API/MCP hops</td><td style="background:#fff3e0">Low</td><td style="background:#fff3e0">Not the main cost</td></tr>
<tr><td style="background:#e3f2fd">More LLM calls in Nashsu ingest</td><td style="background:#fff3e0">Medium</td><td style="background:#fff3e0">Analysis + reconciliation + generation</td></tr>
<tr><td style="background:#e3f2fd">Token cost at scale</td><td style="background:#fff3e0">Medium→high</td><td style="background:#fff3e0">Large wiki ⇒ heavier “affected pages” analysis</td></tr>
<tr><td style="background:#e3f2fd">Duplicate reasoning</td><td style="background:#fff3e0">Medium</td><td style="background:#fff3e0">Nashsu compiles, then harness LLM reasons again on wiki</td></tr>
<tr><td style="background:#e3f2fd">Eventual consistency</td><td style="background:#fff3e0">Low–medium</td><td style="background:#fff3e0">New raw file ≠ instant compiled update</td></tr>
<tr><td style="background:#e3f2fd">Two processes / failure modes</td><td style="background:#fff3e0">Low–medium</td><td style="background:#fff3e0">More moving parts than all-in-Hermes wiki</td></tr>
<tr><td style="background:#e3f2fd">Wiki-only answers lose nuance</td><td style="background:#fff3e0">Medium</td><td style="background:#fff3e0">Mitigate: wiki-first, then drill to raw sources</td></tr>
</tbody>
</table>

**Verdict in chat:** acceptable trade — gains persistence, provenance, specialization, harness independence; biggest cost is **LLM/token duplication**, not MCP latency.

---

<h2 id="14-second-brain-contract" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">14. Second-Brain contract</h2>

The contract is the **stable boundary** between replaceable harnesses and the durable brain. Full diagram and decision quotes are in [§1.1 Final baseline confirmation](#11-final-baseline-confirmation).

**Contract layers (compact):**

| Layer | Responsibility | Stable artifact |
|-------|----------------|-----------------|
| INPUT | Acquire sources with provenance | Files under `raw/sources/` |
| KNOWLEDGE | Compile and maintain wiki | `nashsu/llm_wiki` → Markdown tree |
| AGENT INTERFACE | Machine access to compiled brain | MCP / localhost API |
| WORKFLOWS | Project-defined operations | `ingest-to-brain`, `query-brain`, `audit-brain`, `research-gap` |

**Harness adapters:** Hermes (default), OpenClaw, and DSH each implement thin adapters to the same four workflows—not a fork of the wiki or raw corpus per harness.

---

<h2 id="15-open-risks-and-next-investigations" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">15. Open risks and next investigations</h2>

1. **Headless Nashsu on Linux/VPS** — Tauri desktop vs server deployment for watch/ingest/MCP/API.
2. **Scale bottleneck** — how Nashsu selects existing wiki pages to retrieve/rewrite during ingest at 1k / 10k / 100k pages.
3. **Durable raw archive policy** — Drive-only vs later S3/R2/MinIO for immutable versioning.
4. **RAGFlow bake-off** — incremental maintenance vs generated dataset views.
5. **YouTube reference** — user-linked Karpathy-style video was **not** retrieved in chat; add transcript/title if that content should inform design.

---

<h2 id="16-reference-links" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">16. Reference links</h2>

| Resource | URL |
|----------|-----|
| ChatGPT source conversation | https://chatgpt.com/share/6ac0a93d-aee4-83e8-bb20-02de4c2dbbd2 |
| Nashsu LLM Wiki | https://github.com/nashsu/llm_wiki |
| Nashsu agent skill | https://github.com/nashsu/llm_wiki_skill |
| Hermes agent (LLM Wiki skill path) | https://github.com/NousResearch/hermes-agent/blob/main/skills/research/llm-wiki/SKILL.md |
| Hermes + Obsidian community workflow | https://github.com/zianCAU/hermes_LLMwiki_Obsidian |
| RAGFlow | https://github.com/infiniflow/ragflow |
| Repo extraction HOWTO | `utils/chatgpt/HOWTO_EXTRACT_CHATGPT.md` |
| Implementation plan (this repo) | [`docs/PLAN_SECOND_BRAIN_HERMES_V1.md`](./PLAN_SECOND_BRAIN_HERMES_V1.md) |

---

<h2 id="17-implementation-plan" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">17. Implementation plan</h2>

A phased, CLI-oriented rollout for building the Second Brain **inside this repository** (default Hermes, Nashsu compiler, local-first topology) lives in **[`PLAN_SECOND_BRAIN_HERMES_V1.md`](./PLAN_SECOND_BRAIN_HERMES_V1.md)**.
