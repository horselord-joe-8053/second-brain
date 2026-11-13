# Prompt C v2 — Strict text-only technician knowledge base, retrieval-safe UNKNOWN handling

## Input handling and output paths

- Accept individual PDFs or a ZIP containing multiple PDFs, including nested folders. Process the PDFs only. If the input is a ZIP, retain every PDF's relative directory path.
- **Execute this prompt independently for each PDF:** start afresh with that PDF as the only technical source; do not consult or reuse content, interpretations or outputs from any other PDF or earlier execution. Check each output against its own source before moving on.
- Establish each PDF's actual title, edition, covered models and English-language page range from that PDF. Process English content by default unless the user requests another scope; do not assume GE or a fixed page count.
- **Mirror each PDF's input path and basename:** `fridge-docs/model-X/user-guide.pdf` → `fridge-docs/model-X/user-guide.md`. Keep spelling, case and directories. When this prompt calls for HTML, name it `user-guide.html`; when a separate QA report is required, name it `user-guide_QA_Report.md`. Place permitted images in `assets/user-guide/` beside that Markdown, using working relative links. Apply the same pattern to any PDF stem; never mix or overwrite different documents' assets.
- For ZIP input, deliver one output ZIP containing the corresponding files in the **same folder structure**, without merged documents or flattened paths. A “single Markdown file” requirement means **one `.md` per PDF**, not one for the entire ZIP; do not create sidecar content forbidden by this prompt. For an individual PDF, return its corresponding files directly (plus packaging when assets require it).
- Perform coverage, fidelity and asset checks separately for each PDF; disclose per-document limitations without borrowing information from others.

## Mission and parameters
Act as a senior refrigerator technician leaving a company permanently. Your **only handover** is a single Markdown knowledge-base file that must equip a reasonably intelligent English-speaking high-school graduate **or an AI customer-support agent** to support the models actually covered by the currently processed PDF.

**Sole technical authority:** The currently processed PDF alone. Determine its actual English-language document title, edition, manufacturer and model scope from its **cover and contents**, not from its PDF filename. Do not use details from another PDF.

**No outside technical information:** Do not use the internet, other manuals, remembered appliance engineering facts, external repair practices, invented specifications, new diagnostic procedures, or external assumptions about model compatibility. Common-sense editorial organization, accessible language, and careful explanations of the manual's content are permitted. The Markdown must not quietly incorporate technical conclusions beyond what this source establishes.

**Production scope:** All English-language pages in the currently processed PDF, including diagrams, tables, footnotes, warnings, and model variants. If specifically asked to run a pilot (for example, pages 1–15), process only those pages, identify the limitation prominently, and never imply coverage of pages not examined.

**Special operating assumption:** The downstream LLM Wiki may use only basic text chunking, lexical search, and/or text embeddings, and may **not** interpret images, HTML, attachments, or sophisticated metadata. The customer **does have the same edition of the original PDF**, so a customer-facing answer may give a precise human-readable reference to a figure or diagram in that manual when needed. The knowledge-base file itself must remain useful without access to the picture.

## Definition of success
Produce **a comprehensively explained, accurate, retrieval-first technician handbook**, not an OCR transcription, a reduced summary, or a reformatted user manual. Preserve **as much useful information as the manual contains**: model scope and differences, control layouts, features, locations, normal operation, full procedures, exact button sequences, timing and numeric limits, warnings, installation and service boundaries, care, troubleshooting, specifications, water and ice, warranties, jurisdictions, contacts, and meaningful regulatory details.

Every important fact must be easy for a text-only retriever to find, correctly scoped to the models or feature variants to which it applies, and explained in ordinary English. Difficult pages deserve more interpretation and organization—not omission. Completeness is measured by **semantic coverage**, not by reproduced source pages or sheer word count.

## Evidence discipline — exactly two categories
- **[DOCUMENTED]**: A claim, procedure, value, or explanation explicitly supported by the manual's words, tables, or visually verified diagrams. Clear paraphrasing, beginner-friendly definitions grounded in context, and reorganization of stated procedures are DOCUMENTED only if they do **not** add a new technical conclusion.
- **[UNKNOWN]**: A fact, root cause, repair method, model applicability, measurement, or customer answer not established by the permitted manual pages; also use when the source is ambiguous, contradictory, illegible, or incomplete. Say precisely what the manual does not establish.

**No DERIVED category, conjectural diagnoses, or inferred fixes** in this edition. Do not invent causes, error codes, tests, voltages, service procedures, manufacturer recommendations, part compatibility, or expected outcomes. Do not turn “some models,” “may,” or “normal” into absolute statements. Respect all safety warnings and requirements for qualified or authorized service.

## Retrieval-safe UNKNOWN design (mandatory in Version C v2)
The technical knowledge and permitted sources do **not** change. Improve only how the knowledge base exposes and answers evidence gaps. **UNKNOWN means insufficient evidence, not that a product or feature is proved absent, broken, unsafe, or incompatible.**

1. **Answerability-first routing.** Tell the downstream agent to identify the model and fitted feature; locate the closest DOCUMENTED instructions; then check explicit UNKNOWN boundaries before answering. A customer question may be partly answerable: give the documented part, explicitly withhold the unsupported part. Do not answer a fully documented question with a generic "not in the manual" just because an UNKNOWN chunk was retrieved first. Missing retrieval evidence alone is not proof of absence: if a broader source/manual has not been examined, say the **current knowledge-base scope** lacks the information.
2. **Balance affirmative and negative retrieval.** Add 1–3 natural, non-speculative customer-question synonyms to important **DOCUMENTED** procedure sections as well as to UNKNOWN boundaries. A basic retriever should find the correct operating answer at least as easily as a missing-evidence warning. Avoid repeating full documented instructions in UNKNOWN sections: summarize the established boundary briefly and point precisely to the documented section and page. For a user asking a known question, a negative record must not outrank or replace the supported fact whenever avoidable.
3. **Selective, standalone UNKNOWN knowledge units.** For recurring or high-risk gaps, add concise, searchable sections using this common field layout:

   ```markdown
   ### UNKNOWN-<DOMAIN>-<ISSUE> — <plain-English question/topic>
   Evidence: [UNKNOWN] | Scope: <exact models/variants or pilot limit>
   Customer question aliases: <2–5 plausible distinct phrasings>
   What IS documented: <nearby verified source facts and page references>
   What is NOT established: <specific missing value, procedure, compatibility, diagnosis or applicability>
   Safe response: <brief customer-facing statement and only documented checks, with service escalation where the manual requires it>
   Related documented unit: <one or more stable section identifiers>
   ```

   Keep each record reasonably self-contained for naive text chunkers. Include an **Applicability guard** when the record is easy to confuse with a documented variant (e.g. rotary Sabbath UNKNOWN must never govern external-control Sabbath DOCUMENTED). All claims about what the manual does not say must actually be checked against the **entire authorized source scope**. Do not assert a source-wide negative based on a partial sample.
4. **Precision over keyword stuffing.** Add customer phrasings as retrieval hooks, not as evidence. Do not repeat entire paragraphs, generate hundreds of hypothetical missing topics, or duplicate a vague UNKNOWN warning on every page. Prioritize safety-critical diagnostics, model-feature ambiguity, control sequence limitations, warranty/scope boundaries, and common unsupported troubleshooting requests. Place short local UNKNOWN notes in documented sections when useful, but link each to the specific standalone unknown unit where one exists.
5. **Distinguish two different reasons for missing evidence:**
   - `NOT DOCUMENTED IN AUTHORIZED SOURCE`: The authorized pages were inspected and do not provide that specific answer.
   - `OUTSIDE CURRENT PILOT / SOURCE NOT REVIEWED`: Pages or separately referenced manuals that might address it were **not processed**. Never claim that the full manufacturer manual lacks the answer.
   Both remain evidence category **[UNKNOWN]**. The secondary status describes only *why* the information is unknown; it is not a third epistemic category.
6. **Conservative negative claims.** A manual not showing Sabbath Mode on rotary controls does not prove that the feature is absent. A manual not providing a compressor test does not establish a compressor fault. Manufacturer nonqualification of third-party filters does not prove universal incompatibility. Use wording such as "This manual does not establish..." rather than "Your product cannot...".
7. **Clear conflict resolution for a simple RAG system.** Add a short response policy near the handbook beginning: Prefer exact applicable DOCUMENTED evidence for known questions; use a targeted UNKNOWN record only for unsupported portions; if known and unknown records both appear, combine them without treating the unknown record as canceling the known fact; ask for model/control-type clarification when necessary; never invent an internal repair step.
8. **Probe the UNKNOWN coverage during QA.** Alongside the semantic coverage audit, check representative documented, unsupported, ambiguous-model, safety and mixed-answer questions. Inspect cases where an UNKNOWN record outranks the correct documented procedure (**false abstention**) and where a related documented paragraph hides an important missing limitation (**false confidence**). Do not claim actual LLM answer reliability unless an answer-generation test was run. State the test scope and shortcomings in the single Markdown QA appendix.

## Output format — exactly ONE Markdown file per PDF
Create **only one Markdown content file per input PDF**, named `<PDF_STEM>.md` and saved beside that PDF's input-relative directory path. For ZIP input, the output ZIP may contain multiple such `.md` files, one per source PDF, and no other content artifacts.

The file must:
- Be ordinary, UTF-8, **standalone Markdown** with headings, paragraphs, lists, and simple readable tables where helpful.
- Contain **no embedded images**, HTML, SVG, base64, diagrams as attached files, Markdown image links (`![...](...)`), external assets, iframes, or dependencies on `assets/`.
- Do not generate an HTML edition, image directory, companion report, extracted screenshots, or other per-PDF content artifacts. A single aggregate ZIP is permitted **only as a delivery container** for ZIP input. Put each PDF's coverage/QA report **inside its own Markdown** as a final appendix.
- Prefer simple, widely supported Markdown syntax over elaborate HTML, complex nested tables, special rendering features, or machine-only metadata.
- Be usable for basic text-only RAG indexing without a multimodal pipeline or special preprocessor.

## How to handle diagrams, figures, pictures, and visual instructions
**First convert the useful knowledge in each relevant visual into clear, accurate text.** Read labels, callouts, positions, arrows, indicated controls, and relationships from the PDF page image when necessary. Describe in words what is actually shown and what a technician needs to know. Use a simple textual sequence or list for visual procedures where it is reliable to do so. Avoid introducing conclusions or unseen details.

**Only when the original visual genuinely adds value**—for example, complex control placement, a mechanical arrangement, or distinguishing several similar parts—include a **literal, human-readable reference to the customer’s original PDF**. Such references are supplemental, **not substitutes** for the textual explanation.

Every visual reference must contain, in normal prose:
1. The **real cover title** of the PDF (establish it at the beginning; use the same title consistently).
2. The **printed manual page number**, verified against the PDF. If the PDF viewer's physical page index differs from the printed page number, indicate both when needed for unambiguous navigation.
3. The **exact printed figure identifier or caption**, **only if one actually exists**. Never invent one.
4. If the picture is **unlabeled**, explicitly say **“unlabeled illustration”** and locate it using the **exact nearby section heading**, plus a concise grounded description of what it depicts.
5. Which models/variants the reference actually applies to, if this matters.

**Reference style examples from a GE manual, for illustration of formatting ONLY** (never copy these GE facts, labels, title or page numbers unless the current PDF independently confirms them):

- Labeled diagram: `For the location of these controls, see “Figure B” on printed page 8 of *REFRIGERATORS — Bottom Freezer: OWNER’S MANUAL & INSTALLATION INSTRUCTIONS* (GE and GE Profile; publication 49-1000472 Rev. 9, 04-26).` Use “Figure B” only where the manual actually prints that label.
- Unlabeled diagram: `For a visual guide to the quarter-turn installation, see the unlabeled filter-installation illustration under “INSTALLING THE FILTER IN A BOTTOM FREEZER REFRIGERATOR” on printed page 14 of *REFRIGERATORS — Bottom Freezer: OWNER’S MANUAL & INSTALLATION INSTRUCTIONS* (GE and GE Profile; publication 49-1000472 Rev. 9, 04-26).` This identifies the neighboring heading; **do not present the heading as a figure label**.

If a complex visual cannot be interpreted confidently, describe only its verified content and mark the unresolved technical detail **[UNKNOWN]**. Do not silently “complete” the diagram using outside knowledge. Never say “see image above/below,” “refer to attached diagram,” or give an image filename: the Markdown has no images.

## Retrieval-first handbook structure
Use independently understandable knowledge units with stable, specific headings. Organize the material around how support actually works: **identify model → recognize safety restrictions → identify fitted features/control layout → explain operation → guide documented checks/procedures → recognize normal conditions → escalate unresolved problems**.

Include, as supported by the permitted pages:
1. Source identity, document scope, covered models, how to locate model/serial number, and how to navigate customer references to the original PDF.
2. Beginner orientation and a manual-grounded glossary for relevant parts and controls.
3. Explicit model and feature applicability matrix; distinguish the control types and options actually shown in the current PDF (for example rotary, top, or external controls where applicable), and all “on some models” limitations without inventing mappings.
4. Safety instructions, hazard escalation, electrical/refrigerant requirements, and service boundaries.
5. Operating controls, settings, mode transitions, button combinations, alarms, indicators, special modes, and normal timing.
6. Water, ice, dispenser and filter procedures, limits, symptoms, and variants.
7. Interior features, maintenance, cleaning, installation, measurements, relevant regulatory details, warranty, and support channels.
8. One **symptom-oriented troubleshooting knowledge unit** per meaningful issue; include the exact documented checks/remedies and conditions, not just keyword tags.
9. Plain-English customer-answer examples where they help; do not promise an outcome the manual does not establish.
10. An **UNKNOWN / escalation register** with concise **independently retrievable question-alias records** for material unsupported topics, including precise documented boundaries, scope qualification, and safe response policies. Avoid a lone undifferentiated bulleted list.
11. A final **source-to-knowledge coverage and QA appendix**, included in this same `.md` file.

For each major unit, provide enough **local context** to make it useful when retrieved alone, such as:
- `Knowledge ID:` an intuitive stable text identifier (for example, `WATER-FILTER-XWFE-REPLACE`).
- `Evidence: [DOCUMENTED]` or `[UNKNOWN]`.
- `Applies to:` exact model identifiers or a rigorously worded feature condition; do not overclaim.
- `Source:` printed page number(s) and, when important, a table/section/printed figure name.
- `Customer phrasing:` plausible simple symptom aliases and product terms **only as retrieval vocabulary**, not as invented factual examples.
- `What it means:` beginner-friendly explanation faithful to the manual.
- `What to do:` all stated steps in correct order, including prerequisites and safety warnings.
- `Expected result:` **only when documented**.
- `Exceptions and limits:` variant restrictions, caveats, conditions, and unknowns.
- `Original PDF visual reference:` **only when a diagram is genuinely useful** and the locator has been verified.

The labels are an organizing aid, not a mandatory repetitive template: use the right structure for tables, specifications, hazard notes, and short facts. Prefer the complete relevant context close to the claim rather than a detached citation appendix. Make sections reasonably sized for naive RAG chunking; split long topics under meaningful headings, repeating essential model constraints and safety warnings where necessary. Avoid artificial micro-chunks that omit indispensable context. Do not repeat entire sections or add transcript padding simply to improve keyword matching.

## Processing workflow
1. Verify the actual cover title, edition, printed page numbering, and authorized English-page scope. Build a page-by-page inventory of **all substantive text, tables, drawings, callouts, conditions, and warnings** before drafting.
2. Read and understand each page, including visual inspection when extraction is corrupted or a diagram is essential. Verify potentially garbled numbers and labels visually; mark anything unresolved as UNKNOWN rather than guessing.
3. Identify every model and variant boundary and every value whose meaning depends on a control design or installed option.
4. Convert each useful source fact into an explained, independently retrievable knowledge unit. Translate complex tables into clear tables or fact records without losing distinctions; translate useful diagram content into grounded English.
5. Add **selective verified prose references** to diagrams in the original PDF only when they provide meaningful additional help to the customer. Use **exact printed labels**, or “unlabeled illustration” plus an exact nearby heading. Do not manufacture names for pictures.
6. Review technical exactness: temperatures, pressure ranges, dimensions, units, button combinations, time intervals, rotation directions, warnings, jurisdictional warranty details, and model/feature conditions.
7. Perform a **semantic coverage audit**, mapping every substantive source section, table, and figure to knowledge units in the Markdown or explaining its legitimate omission. Count a diagram as covered only when its **useful content** has been explained, not merely referenced.
8. Verify UNKNOWN routing with supported, unsupported, mixed and model-ambiguous ticket questions; check both false abstention and unsupported over-answering. Then inspect the final `.md` for unsupported claims, unresolved ambiguities, inconsistent model scope, broken internal references, accidental image/HTML content, redundant OCR text, source dumping, and overly long or contextless retrieval sections.
9. Put a concise but precise **QA appendix in the same Markdown**: pages processed, coverage by source section/page, substantive figures translated to text, visuals cited by reference only, unresolved items, and checks actually performed. State clearly whether the audit was structural/spot-check or exhaustive; do not claim more validation than performed.

## Acceptance criteria
- Exactly **one `.md` content file per PDF**, even when the inputs come from a ZIP. No images, HTML, embedded artifacts, supplemental content files, or package dependencies; an aggregate ZIP is packaging only.
- **Complete semantic coverage** of useful information in every authorized English page, as far as the source is legible and interpretable. Comprehensive explanation, not verbatim source reproduction.
- Every technical instruction and numerical value is traceable to the original PDF; no external technical information or fabricated service procedures.
- Accurate, explicit model/feature applicability, with safety warnings located near the relevant procedures.
- Simple textual structure optimized for unsophisticated lexical/vector RAG; meaningful self-contained symptom, feature, procedure, and selective UNKNOWN-answerability sections.
- UNKNOWN records specify common query aliases, precisely scoped absent evidence, nearest DOCUMENTED checks, and safe answer wording; unknown records must not suppress supported answers.
- QA checks both UNKNOWN-boundary discovery **and retention of ordinary documented-answer retrieval**, including mixed questions that need a partial answer rather than a flat refusal.
- Relevant figures are **explained in text first**; only when useful, also cited by a **human-locatable literal reference** to the real title, printed page, and genuine label or precise unlabeled-figure description.
- A customer who has the **same edition** of the manual can locate any cited illustration without opening other generated artifacts. When editions differ, do not assume pagination still matches.
- No original-page screenshot atlas, OCR dump, copy of the PDF, or copied page transcriptions disguised as knowledge coverage.
- No claimed full-manual completeness if only a page-limited pilot was processed.

**Build the single text-only handbook an excellent technician would leave—not a reformatted manual. It should be consumable by a basic LLM Wiki and teach a human reader too.**
