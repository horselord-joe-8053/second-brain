<h1 id="realign-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Realignment — refactor goals (diagram chat)</h1>

**Source:** [ChatGPT share](https://chatgpt.com/share/6adb338c-a8e0-83ec-88aa-f633463cb70e) from user message *“I am trying hard to make what we want to refactor/improve more concrete and clear…”* (2026-10-23).  
**Transcript:** `utils/chatgpt/transcripts/refactor_three_tracks_cos_6adb338c-a8e0-83ec-88aa-f633463cb70e.txt` (from line ~3157).  
**Executable plan:** [`REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md`](../../ref_plan/new/REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md).

<h2 id="realign-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [What was wrong](#realign-wrong) — messy objective.
2. [Part A — three systems](#realign-a) — refactor separately.
3. [Shared components](#realign-shared) — three Python modules.
4. [Part B — COS](#realign-b) — integrate after A.
5. [Build order](#realign-order) — what to implement first.
6. [What we stopped mixing](#realign-stop) — explicit cuts.

---

<h2 id="realign-wrong" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. What was wrong</h2>

One refactor plan tried to simultaneously:

- Upgrade raw Lance search, wiki harness modes, wiki+raw **combined**, verifier, wiki audit, and FastAPI COS.

That conflated **three different Q&amp;A products** with **integration (COS)** before any single track had a clear win on its own metric. Your diagrams fixed the structure: **A first, B second**.

---

<h2 id="realign-a" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Part A — three systems</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>ID</th><th>System</th><th>Focus</th><th>Main enhancements (chat)</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>A1</strong></td><td>LLM Wiki Q&amp;A (product PDFs → wiki)</td><td>Relationships, org knowledge; watch incompleteness</td><td>Claim audit at compile; EvidenceVerifier; trust status on claims</td></tr>
<tr><td style="background:#e8f5e9"><strong>A2</strong></td><td>Manual RAG (product PDFs → index)</td><td>Precise, complete customer Q&amp;A</td><td>SKU filter, BM25+vector+RRF, rerank, **Agentic RAG** (bounded), verifier</td></tr>
<tr><td style="background:#fff3e0"><strong>A3</strong></td><td>Ticket RAG</td><td>Past cases → suggestion</td><td>Keep hybrid search; optional rerank; agentic case search; applicability verifier</td></tr>
</tbody>
</table>

**A2** is what the **90-question refrigerator benchmark** measures today. **A1** and **A3** need **their own** scoreboards.

---

<h2 id="realign-shared" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Shared components</h2>

Chat agreed these are **wise**, with different **policies** per track:

| Component | Role |
|-----------|------|
| **EvidenceRetriever** | Search orchestration (manual index, ticket index, wiki HTTP) |
| **EvidenceVerifier** | Claim vs evidence (manual coverage, ticket applicability, wiki claim audit) |
| **AgenticRetrievalController** | Missing-evidence loop — **A2 and A3 only**; start with **one** extra targeted search |

Reranking ≠ agentic: rerank **reorders** the pool; agentic **asks again** with a new query when coverage fails.

---

<h2 id="realign-b" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Part B — Chief of Staff</h2>

After A1–A3 work and are measured:

1. **COS** uses wiki for **understanding** (relationships, orientation).
2. **Search system** (A2 + A3 retriever) for **completeness and verification**.
3. Two response modes for management:
   - **Provisional** — wiki synthesis, clearly labeled.
   - **Evidence-backed** — retriever + verifier; not “wiki + warning only” for important facts.

Integration diagram in chat: orchestrator → wiki (fast insight) + EvidenceRetriever (manuals, tickets, other records) → EvidenceVerifier → answer or escalate.

---

<h2 id="realign-order" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Build order</h2>

Chat sequence (adopted in refactor plan):

1. **A2 Manual RAG** — 90-Q on **D2.B** (`brain/retail-md`); beat Lane **B** wiki + raw baselines (**R10**); **D2.D** later.
2. **A3 Ticket RAG** — extend libs; **D2 n/a** (tickets only). **Before A1** (**R25** in refactor plan).
3. **A1 LLM Wiki** — audit + harness wiki Q&amp;A on **D2.B** only for now; **D2.D** later.
4. **B COS + thin API** — wire proven pieces only.

**Why A3 before A1 (conscious choice, 2026-10-25):** Tickets and manuals both touch product knowledge, but **A2 and A3 share the same retrieval *style*** — hybrid search over an **index** (raw Lance vs Postgres), not the **LLM-Wiki** compile + **`llm_wiki`** HTTP path (**A1**). We finish hardening rerank · verifier · agentic on **non-wiki search** for manuals **then** tickets **before** investing in wiki audit and wiki harness modes.

**Note:** Older summaries cited “beat Lane D **31/60**” — that was the aggregate **D2.D** wiki high-water mark; **promotion bar is Lane B** until you explicitly reopen D.

---

<h2 id="realign-stop" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. What we stopped mixing</h2>

| Removed from “Phase 1 everything” | Now lives |
|----------------------------------|-----------|
| `wiki_leads_raw` combined mode | Part **B** (COS uses wiki as **lead**, not merged benchmark arm) |
| FastAPI orchestrator in same phase as rerank | **Phase 4** |
| Wiki `sources_rerank` vs raw hybrid in one promotion bar | **A1** vs **A2** scoreboards |
| Ticket index changes | **Phase 2 (A3)** only |

**Dimensions:** [`REALIGNMENT_DIMENSIONS.md`](./REALIGNMENT_DIMENSIONS.md) (D1–D6, run profiles). **Plan:** [`REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md`](../../ref_plan/new/REFACTOR_PLAN_MAIN_1_FURTHER_ENHANCEMENT_GPT.md) §1–3 + phases §10–13. **Code:** **`implref` Phase 1 first**; **HG-P*** in plan §14.
