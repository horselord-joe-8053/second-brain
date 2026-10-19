# Updated Prompt A — Strict, source-only technician knowledge base

## Input handling and output paths

- Accept individual PDFs or a ZIP containing multiple PDFs, including nested folders. Process the PDFs only. If the input is a ZIP, retain every PDF's relative directory path.
- **Execute this prompt independently for each PDF:** start afresh with that PDF as the only technical source; do not consult or reuse content, interpretations or outputs from any other PDF or earlier execution. Check each output against its own source before moving on.
- Establish each PDF's actual title, edition, covered models and English-language page range from that PDF. Process English content by default unless the user requests another scope; do not assume GE or a fixed page count.
- **Mirror each PDF's input path and basename:** `fridge-docs/model-X/user-guide.pdf` → `fridge-docs/model-X/user-guide.md`. Keep spelling, case and directories. When this prompt calls for HTML, name it `user-guide.html`; when a separate QA report is required, name it `user-guide_QA_Report.md`. Place permitted images in `assets/user-guide/` beside that Markdown, using working relative links. Apply the same pattern to any PDF stem; never mix or overwrite different documents' assets.
- For ZIP input, deliver one output ZIP containing the corresponding files in the **same folder structure**, without merged documents or flattened paths. A “single Markdown file” requirement means **one `.md` per PDF**, not one for the entire ZIP; do not create sidecar content forbidden by this prompt. For an individual PDF, return its corresponding files directly (plus packaging when assets require it).
- Perform coverage, fidelity and asset checks separately for each PDF; disclose per-document limitations without borrowing information from others.

## Mission and parameters
Act as a senior technician leaving a company permanently. Your only handover is a knowledge base that must prepare a reasonably intelligent English-speaking high-school graduate **or AI customer-support agent** to support the refrigerator models or other appliance models actually covered by the currently processed PDF.

**Sole technical authority:** Only the currently processed PDF; verify its actual cover title and publication details. No internet, other documentation, memorized appliance engineering facts, inferred manufacturer specifications, or fabricated troubleshooting procedures. Common-sense language, clear explanations and rearrangement of supplied material are allowed. The successor cannot consult the original PDF.

**Scope for a production run:** All English-language pages of the currently processed PDF, including diagrams and dense tables. For a bounded test, change this to “PDF pages 1–15 only” and prominently indicate what is out of scope.

## Definition of success
Produce a **comprehensively explained technician handbook optimized for AI retrieval** and readable by beginners. Preserve **as much useful knowledge as the source contains**: model applicability, component/feature descriptions, exact operating instructions, numerical limits, safety, option differences, exceptions, maintenance, installation, troubleshooting, warranties, contacts, relevant regulatory information and support implications. Not every source sentence needs preservation; every substantive useful fact needs a findable, accurately expressed home. Do not arbitrarily summarize, condense difficult pages away or fill gaps with guesses.

## Evidence discipline — exactly two labels
- **[DOCUMENTED]**: Technical claim, procedure or interpretation explicitly supported by a page, table or figure from the manual. Plain-English rewording, definition of terms in context, reorganizing steps and turning stated facts into an easier-to-follow explanation remain DOCUMENTED only when they preserve the original meaning without adding new factual conclusions.
- **[UNKNOWN]**: Technical detail not established by the source, unresolved option/model applicability, conflicting statements, or question requiring an unavailable service manual. State what evidence is missing; don't pretend knowledge is complete.

**No DERIVED category and no speculative diagnostic extensions** in Prompt A. In particular, never invent component failures, error codes, test voltages, repair instructions, manufacturer intentions, model compatibility, workaround steps or likely root causes. Where a manual expressly says a condition is normal, reflect that; where it says a remedy may help, retain its uncertainty. Safety restrictions and repair/authorized-service boundaries have priority over completing a ticket.

## Processing workflow
1. Establish the actual English page range and source publication details. Make a page-by-page coverage checklist before authoring.
2. **Examine each source page, including rendered figures, callouts, footnotes and tables.** PDF extraction may contain scrambled font encodings; compare with the page image. If a number, label or instruction cannot be confirmed, mark it unresolved instead of guessing.
3. Identify every model family, physical variant and feature condition. Never convert “some models” into “all models.” If full suffix-to-feature mapping is absent, say so and instruct a check of the customer's actual appliance.
4. Build source-grounded knowledge units by topic, with stable searchable headings, `model_scope`, evidence label, source page(s), user/customer vocabulary, prerequisites, exact steps, expected outcomes **only when stated**, warnings, exceptions and clear UNKNOWN boundaries where needed.
5. Reorganize the material for how a technician would work: identify model → assess safety → explain components → choose control variant → perform allowed operating procedure → interpret normal behavior → route troubleshooting → escalate.
6. Preserve numerical specs, timings, button presses, direction of turn, quantities, warnings and jurisdiction notes exactly. Explain beginner terminology in clear English based on context without injecting unstated technical theory.
7. Turn source troubleshooting content into **symptom-based records and customer Q&A**, citing supporting pages. Avoid parroting source rows without explaining them. Never promise outcomes not established.
8. Extract **only useful technical figures** (e.g., panel labels, switch placement, complex mechanism locations). Crop tightly; add useful figure captions and explanatory text. **Do not attach whole PDF page screenshots, page transcriptions, bulk OCR dumps or a copy of the manual** to satisfy completeness requirements. If a diagram cannot be interpreted, flag it rather than pasting an entire page.
9. Build an exhaustive source-page **coverage audit**: for each substantive section/table/figure, list its resulting knowledge section and any intentionally omitted low-value material or unresolved ambiguity. Treat coverage as verified *content transformation*, not merely presence of source pages.
10. Review for hallucinations, unsafe directions, mixed-up control variants, mismatched numeric values, broken links, missing sections, and accurate cross-references. Check Markdown and HTML contents agree.

## Deliverables
- `<PDF_STEM>.md`: **canonical** human-readable Markdown for ingestion into LLM Wiki. Semantic headings and complete self-contained answer units matter more than decorative presentation.
- `assets/<PDF_STEM>/`: only necessary crops of technical diagrams, linked with relative paths from that PDF's Markdown.
- `<PDF_STEM>.html`: generated **from that Markdown**, a standalone offline HTML document with the same technical content, its selective images embedded, navigable headings, usable tables and typography. No remote dependencies.
- For each PDF, include `<PDF_STEM>_QA_Report.md`; package all permitted outputs into a ZIP (one aggregate ZIP for ZIP input). Include hashes and content/asset checks when possible.

## Acceptance criteria
- Each useful claim comes from the PDF and has a page reference or nearby section-level provenance.
- Every source page is considered **semantically**, and major tables/figures are reconstructible from the explanation or a selectively cropped diagram.
- No transcript atlas, whole-page screenshots or unreviewed machine text are included in the knowledge base.
- A beginner can follow customer-safe instructions without the PDF. An AI retriever can find the answer by symptom, control, model or part name.
- The two formats represent the same knowledge. Image links resolve; HTML is self-contained; generated packages open successfully.
- Never claim a full manual was processed if only a pilot range was processed. Report remaining unknowns and honestly distinguish automatic checks from human technical verification.

**Execute diligently, rather than padding with source reproduction to imitate completeness.**
