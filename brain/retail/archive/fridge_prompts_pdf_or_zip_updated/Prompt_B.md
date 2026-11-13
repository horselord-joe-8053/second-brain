# Updated Prompt B — Source-only, reasoning-enhanced technician knowledge base

## Input handling and output paths

- Accept individual PDFs or a ZIP containing multiple PDFs, including nested folders. Process the PDFs only. If the input is a ZIP, retain every PDF's relative directory path.
- **Execute this prompt independently for each PDF:** start afresh with that PDF as the only technical source; do not consult or reuse content, interpretations or outputs from any other PDF or earlier execution. Check each output against its own source before moving on.
- Establish each PDF's actual title, edition, covered models and English-language page range from that PDF. Process English content by default unless the user requests another scope; do not assume GE or a fixed page count.
- **Mirror each PDF's input path and basename:** `fridge-docs/model-X/user-guide.pdf` → `fridge-docs/model-X/user-guide.md`. Keep spelling, case and directories. When this prompt calls for HTML, name it `user-guide.html`; when a separate QA report is required, name it `user-guide_QA_Report.md`. Place permitted images in `assets/user-guide/` beside that Markdown, using working relative links. Apply the same pattern to any PDF stem; never mix or overwrite different documents' assets.
- For ZIP input, deliver one output ZIP containing the corresponding files in the **same folder structure**, without merged documents or flattened paths. A “single Markdown file” requirement means **one `.md` per PDF**, not one for the entire ZIP; do not create sidecar content forbidden by this prompt. For an individual PDF, return its corresponding files directly (plus packaging when assets require it).
- Perform coverage, fidelity and asset checks separately for each PDF; disclose per-document limitations without borrowing information from others.

## Mission and parameters
Act as a departing senior technician whose entire transfer of expertise must fit into a knowledge base for a reasonably intelligent English-speaking high-school graduate **or AI customer-support agent**. The only technical source is the PDF currently being processed, whose actual title, edition and covered models must be verified from that PDF. The successor has no original manual or outside documentation.

**Production scope:** All English-language pages of the currently processed PDF, including figures and tables. A pilot may explicitly restrict pages, but must not silently treat missing chapters as known.

**Outside information is prohibited:** No web, external service manuals, remembered model-specific facts, general repair techniques, outside diagnostic thresholds, repair procedures, or fabricated specifications. You may use everyday language, source-grounded teaching explanations, and logical inference **solely from facts in this PDF**, subject to the rules below.

## First build the same complete documented foundation as Prompt A
Thoroughly inspect every permitted page visually and textually (PDF extraction can corrupt characters). Build a genuinely explanatory, **AI-retrieval-optimized** knowledge base—not an OCR transcript or screenshot archive. Cover as completely as possible every useful manufacturer fact: model/feature routing; components; safe use; exact settings/buttons; alerts; water/ice; cleaning; installation; dimensions; maintenance; normal behaviors; symptom/causes/actions; warranties; contacts; safety and regulatory material.

Make each knowledge unit independently retrievable with a clear heading, model applicability, evidence category, original manual page reference, relevant customer terms/symptom synonyms, precise procedure or answer, warnings, and links to neighboring topics. Teach contextual terms to a beginner. Where an option is described as “some models,” never generalize it to the entire product family.

## Evidence policy — three categories
- **[DOCUMENTED]**: Expressly established by a verifiable source page/table/diagram, including faithful plain-English explanation and restructuring.
- **[DERIVED]**: Logically defensible conclusion **only from specifically cited DOCUMENTED premises**. Must include: (a) premise identifiers/pages, (b) short explicit reasoning, (c) confidence/uncertainty or conditions, and (d) what was *not* established. A derivation is not manufacturer instruction, field-confirmed repair, or demonstrated cause. Keep it separate from manufacturer facts in storage and presentation.
- **[UNKNOWN]**: Missing, ambiguous or unsupported facts/diagnoses. Do not resolve by guessing; specify what would have to be verified elsewhere.

**Critical rules for DERIVED:** Inference can reorganize multiple stated procedures into a question/decision sequence, identify logically relevant customer questions, distinguish mutually exclusive branches when the manual supports them, and explain implications of documented conditions. It cannot introduce undocumented measurements, hidden hardware design, likely failure rates, novel component tests, service actions, replacement compatibility, safety-critical remedies, or assert a definite root cause where the source does not establish it. Do not promote any DERIVED hypothesis to DOCUMENTED, even if it sounds reasonable or is repeated in support conversations. An unknown or plausible cause must never be presented as confirmed repair advice.

## Required construction and review steps
1. Inventory every English page and content unit (including control variants, tables, safety warnings, pictures, footnotes), noting source references.
2. Extract and **understand** content, verify garbled machine extraction against page visuals, and rewrite into coherent technician knowledge. Make traceability part of the text, not a huge copied appendix.
3. Produce a detailed model/feature routing section, beginner primer, operating-procedure library, searchable customer symptom index, troubleshooting decision structures, full technical specification register, hazards/escalation, and warranty/support reference.
4. First write all **DOCUMENTED** content to completion, exactly to Prompt A's technical standard, then add separate **DERIVED** support units with explicit premise links and limitations. Do not dilute documentation quality because reasoning is allowed.
5. Produce a complete **UNKNOWN** register for all unresolved customer questions and unspecified repair/diagnostic details. Preserve manufacturer safety constraints and recommend qualified-service escalation whenever the source requires it.
6. Only crop diagrams when they genuinely improve spatial/mechanical comprehension. Explain them. Do not place entire pages, page-by-page transcriptions, raw OCR, or a PDF-image atlas into the knowledge base.
7. Perform a page-by-page semantic coverage audit, a premise-to-derivation validation audit, model applicability audit, and cross-format parity / package integrity tests. Report test limitations honestly.

## Deliverables
- `<PDF_STEM>.md`: authoritative Markdown suitable for retrieval and human learning, with separable DOCUMENTED/DERIVED/UNKNOWN sections.
- `assets/<PDF_STEM>/`: select original figures cropped to relevant content and linked relatively.
- `<PDF_STEM>.html`: complete standalone HTML generated from the Markdown, with embedded figures and offline navigation.
- `<PDF_STEM>_QA_Report.md` for each PDF, plus one ZIP containing all permitted outputs (mirrored folders for ZIP input).

## Acceptance criteria
Comprehensive **semantic** coverage of every useful manual section, accurate page-grounded instructions/figures, no external technical input, source-consistent model applicability, clear derived premise trails, no covert inference in documented sections, no fabricated service knowledge, no bulk transcript/image padding, retrievable symptom-oriented units, beginner readability, and consistent Markdown/HTML outputs. If only part of the PDF was authorized, clearly report remaining coverage as UNKNOWN / out of scope.

**Build the handbook an excellent technician would leave—not a reformatted user guide and not a speculative repair manual.**
