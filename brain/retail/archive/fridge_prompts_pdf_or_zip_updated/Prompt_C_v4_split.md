<h1 id="pc4-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Prompt C v4 split — coarse shards (4–10 per PDF) + strict technician KB</h1>

*(Based on [Prompt C v3 split](./Prompt_C_v3_split.md). **v4 replaces only the shard export contract:** **4–10** ingest files per PDF, split on **coarse** `##` parts—not one file per knowledge unit.)*

**Why v4:** v3 split every top-level `##` → ~60–120 shards per long manual → ~1 LLM ingest minute **per file** → multi-hour queues. v4 keeps **many** knowledge units **inside** each shard using `###` headings so retrieval text stays rich while **ingest count** stays practical.

## Document outline

1. [What changed from v3](#pc4-delta) — shard count and heading levels.
2. [Input handling](#pc4-input) — paths, ZIP, independence per PDF.
3. [Shard export for LLM Wiki (v4)](#pc4-shard-export) — **4–10** files, merge rules, naming.
4. [Heading levels inside a shard](#pc4-headings) — `##` part vs `###` unit.
5. [Default part map (user guides)](#pc4-part-map) — logical grouping template.
6. [Mission, evidence, UNKNOWN](#pc4-mission) — same discipline as v3 (summary).
7. [Processing workflow](#pc4-workflow) — draft → merge audit → export.
8. [Acceptance criteria](#pc4-acceptance) — counts, caps, QA.

---

<h2 id="pc4-delta" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. What changed from v3</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Topic</th><th>v3</th><th>v4 (use this)</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Split boundary</td><td style="background:#ffebee">Every <code>^## </code> line → new file</td><td style="background:#e8f5e9"><strong>Only</strong> coarse part <code>##</code> → new file (<strong>4–10</strong> per PDF)</td></tr>
<tr><td style="background:#e3f2fd">Knowledge units</td><td style="background:#fff3e0">Often own <code>##</code> (1 file each)</td><td style="background:#e8f5e9"><code>###</code> (and deeper) <strong>inside</strong> one part file</td></tr>
<tr><td style="background:#e3f2fd">Typical shard count</td><td style="background:#ffebee">50–120+ per manual</td><td style="background:#e8f5e9"><strong>4–10</strong> per PDF (hard max <strong>10</strong>)</td></tr>
<tr><td style="background:#e3f2fd">Evidence / UNKNOWN / no hallucination</td><td style="background:#e8f5e9">Unchanged</td><td style="background:#e8f5e9">Same as v3 — see [§6](#pc4-mission)</td></tr>
<tr><td style="background:#e3f2fd">Downstream ingest</td><td style="background:#e8f5e9">LLM Wiki <code>full-copy</code> + <code>service-manual</code> cards</td><td style="background:#e8f5e9">Same</td></tr>
</tbody>
</table>

---

<h2 id="pc4-input" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Input handling and output paths</h2>

(Same as v3 unless noted.)

- Accept individual PDFs or a ZIP; process **each PDF independently**; mirror path: `fridge-docs/model-X/user-guide.pdf` → directory `fridge-docs/model-X/user-guide/` (or `fridge-docs_md_learned/...` when specified) containing **multiple** `.md` shards per [§3](#pc4-shard-export).
- Do **not** deliver one monolithic `<stem>.md` as the only ingest artifact.
- ZIP output preserves folder structure; no flattening.

---

<h2 id="pc4-shard-export" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Shard export for LLM Wiki (v4)</h2>

After drafting handbook content for **one PDF**, export shards for auto-ingest:

### 3.1 Targets and hard limits

| Rule | Value |
|------|--------|
| **Target** | **4–8** shard files per PDF for typical user/repair guides |
| **Allowed range** | **4–10** inclusive (count **every** delivered `.md` shard under `<pdf-stem>/`) |
| **Hard maximum** | **10** — if a draft would exceed 10, **merge** adjacent parts until ≤10 before delivery |
| **Hard minimum** | **4** for any PDF with ≥20 printed pages of English body (merge tiny parts; do not over-split) |

**Practical check:** ~254 shards for four fridge PDFs (~63/PDF) is **non-compliant** with v4. A compliant GE user-guide should land near **6–9** files, not **70+**.

### 3.2 Split boundary (coarse parts only)

1. **New shard file** starts only at a **part-level** line matching `^## ` whose purpose is a **major manual division** (install, operation, troubleshooting block, warranty, etc.)—see [§5 default map](#pc4-part-map).
2. **Do not** promote every symptom, filter step, or knowledge id to its own `##` for export. Those belong under **`###`** inside the parent part.
3. Content before the first part `##` → `<pdf-stem>--preamble.md` (counts as **one** shard toward the 4–10 budget).
4. Optional `<pdf-stem>--qa-appendix.md` only if QA material does not fit preamble; prefer keeping QA in **preamble** to save a shard slot.

### 3.3 Merge logic (when the draft has too many `##`)

Before export, run a **merge pass**:

1. List all candidate part titles in reading order.
2. If count **> 10**, merge **smallest adjacent** pairs that are thematically adjacent (e.g. “Care” + “Cleaning”; two warranty fragments).
3. If count **> 10** still, merge all **symptom** subsections into **one** `## Troubleshooting and documented checks` part (symptoms stay `###`).
4. Never merge **Safety** into **Installation**; never merge unrelated manufacturers’ scopes.

### 3.4 Shard filename

- Pattern: `<pdf-stem>--<slug>.md`
- `<slug>`: kebab-case from the **part** `##` title; prefer a short stable token (`install`, `operation`, `troubleshooting`, `water-ice-filter`, `warranty-support`).
- Optional numeric prefix for sort order: `<pdf-stem>--part-03-operation.md`
- Collisions: append `-2`, `-3`.

### 3.5 Shard body

- Each file is **standalone Markdown**: repeat the part’s **`##` heading** as the first line, then all `###` units and body for that part.
- Preserve tables, lists, UNKNOWN blocks, and Knowledge ID lines under the appropriate `###` unit.
- **No** downstream wiki firewall meta (same as v3).

### 3.6 Cross-shard references

- Use stable unit ids (`GE-FILTER-001`, `UNKNOWN-XWFE-ELECTRONICS`) and plain English; do not forbid wiki linking in shard bodies.

---

<h2 id="pc4-headings" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Heading levels inside a shard</h2>

| Level | Role | Export impact |
|-------|------|----------------|
| `#` | Optional single title at top of shard (part name) | Inside file only |
| `##` | **Part boundary** — one per ingest file | **Starts new shard** |
| `###` | **Knowledge unit** (symptom, procedure, UNKNOWN record, feature) | Stays in parent shard |
| `####`+ | Sub-steps, table groups | Stays in parent shard |

Each `###` unit should still carry v3-style fields where applicable: `Knowledge ID:`, `Evidence:`, `Applies to:`, `Source:`, customer phrasing, etc.

**Symptom routing:** Do **not** use `## GE-SYMPTOM-036` per symptom. Use:

```markdown
## Troubleshooting — documented symptoms and checks

### GE-TROUBLE-036 — Ice maker not producing (example)
Knowledge ID: GE-TROUBLE-036
Evidence: [DOCUMENTED]
...
```

---

<h2 id="pc4-part-map" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Default part map (user guides)</h2>

Pick **4–8** of these **part-level** `##` sections; adapt names to the PDF; **combine** thin sections:

1. **Preamble shard** (`--preamble.md`): source identity, model scope, navigation, response policy for UNKNOWN vs DOCUMENTED, glossary highlights.
2. **Safety and service boundaries**
3. **Installation, leveling, doors, water line, electrical**
4. **Controls, settings, normal operation, alarms**
5. **Water, ice, dispenser, filters** (XWFE etc.)
6. **Features, care, cleaning, maintenance**
7. **Troubleshooting** (all symptoms as `###`; split into **two** part files only if the manual is very long **and** you are still ≤10 total)
8. **Specifications, warranty, regulatory, support contacts**
9. **QA appendix** (only if not in preamble)

**Repair guides:** often **4–6** parts: preamble, safety, diagnostics/error codes, test procedures, parts/service boundaries, warranty/QA.

---

<h2 id="pc4-mission" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Mission, evidence, UNKNOWN (unchanged from v3)</h2>

Apply **all** of Prompt C v3 for:

- Sole source = current PDF; no outside technical facts; **[DOCUMENTED]** vs **[UNKNOWN]** only.
- Retrieval-first completeness (semantic coverage, not OCR dump).
- UNKNOWN answerability rules, customer aliases, conservative negatives.
- Diagram handling: text first, then literal PDF page/figure reference when needed.
- No images/HTML in Markdown; no shard-body “do not link” firewall.

If v3 and v4 conflict on **headings**, **v4 wins** for `##` vs `###` and shard count.

---

<h2 id="pc4-workflow" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Processing workflow</h2>

1. Inventory PDF (v3 steps 1–7): coverage, units as **`###` drafts** grouped under planned **parts**.
2. **Plan the part map first** — write down **4–10** part titles before filling body text.
3. Draft content; keep symptoms and small topics at **`###`**.
4. **Shard-count audit:** count `.md` files you would emit; merge until **4–10**.
5. Export shards per [§3](#pc4-shard-export); QA in preamble or `--qa-appendix.md`.
6. Deliver ZIP or folder tree; **no** monolith-only delivery.

---

<h2 id="pc4-acceptance" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">8. Acceptance criteria</h2>

- **4–10** `.md` files per PDF under `<pdf-stem>/` (document the count in preamble).
- **No** export split on every knowledge unit; **≥80%** of units live under **`###`** inside part files.
- Full semantic coverage (v3 standard); traceable values; UNKNOWN discipline intact.
- Filename pattern `<pdf-stem>--<slug>.md`; UTF-8; no embedded images.
- Ready for LLM Wiki **`full-copy`** + **`service-manual`** ingest (one ingest job per shard, not hundreds).

**Operator expectation:** Re-run this prompt on the four PDFs **or** manually merge existing v3 shards into v4 part files before re-ingest. Replacing `fridge-docs-split/` without canceling the queue may leave orphan wiki pages until P5 cleanup lands in LLM Wiki.
