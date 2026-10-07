<h1 id="todo-ideas-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">TODO — ideas ledger</h1>

**Purpose:** Captured ideas from **`ctodo`** prompts; one section per idea.  
**Rule:** `.cursor/rules/ctodo-ideas-capture-list.mdc`

<h2 id="todo-ideas-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Active entries](#todo-ideas-entries) — newest at bottom unless user reorders.

---

<h2 id="todo-ideas-entries" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Active entries</h2>

<h3 id="ctodo-001-configurable-graph-search-hops" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">CTODO-001 — Configurable wikilink graph hops in hybrid search</h3>

```yaml
id: CTODO-001
slug: configurable-graph-search-hops
added: 2026-10-06
last-modified: 2026-10-06
status: new
related-plans: []
```

**Summary** — Make the **graph expansion depth** in LLM Wiki hybrid search (`llm_wiki_search` / `POST …/search`) **user-configurable** instead of a fixed **one-hop** wikilink neighbor blend.

**Analysis**

- **Intent** — Today Nashsu search merges keyword ± vector hits with a **fixed one-hop** graph expansion (wikilink neighbors of top seeds, ~15–30% of the result window). That is simple and fast but cannot reach related pages **two+ links away** when seeds miss the right cluster. A configurable hop count (0 = off, 1 = current default, 2+ = wider) would improve recall for sparse wikis at the cost of latency, noise, and tuning.
- **Scope** — **Upstream `nu_llm_wiki`** (likely `search.rs` `blend_graph_results` + Settings → Search or Embeddings-adjacent UI + API/MCP optional param). Second Brain would **document** the setting and optionally pass hop override via MCP if exposed. Out of scope: replacing hybrid search or indexing L2 raw.
- **Dependencies** — Nashsu fork `../nu_llm_wiki/`; understanding current quotas (`MIN/MAX_GRAPH_RESULT_RATIO`, `MAX_GRAPH_SEEDS`); acceptance via search quality on project **brain** (e.g. concept pages linked only through an intermediate entity).
- **Risks / open questions**
  - Diminishing returns and **result pollution** beyond 1–2 hops on dense graphs.
  - **API surface:** global setting vs per-request `graphHops` on search (better for Hermes Pattern A).
  - Whether **MCP `llm_wiki_search`** should expose `graph_hops` or only app settings.
  - Performance on large `wiki/` trees (BFS cap per query).
- **Suggested next step** — Spike in `nu_llm_wiki`: read `blend_graph_results` / adjacency build; prototype `graphHops: 0|1|2` in app settings; compare NB-SB1-style queries at 1 vs 2 hops. If valuable, open upstream issue or fork PR; link plan here and set **`status: planned`**.

**Source prompt** — User asked whether hardcoded **1-hop** graph blend in hybrid search (as described for `llm_wiki_search`) is weaker than **configurable hop count**; if so, capture as **`ctodo`** idea: “the # of hops configurable”.
