# PDF to Markdown + Referenced Images — Faithful Extraction

## Input handling and output paths

- Accept individual PDFs or a ZIP containing multiple PDFs, including nested folders. Process the PDFs only. If the input is a ZIP, retain every PDF's relative directory path.
- **Execute this prompt independently for each PDF:** start afresh with that PDF as the only technical source; do not consult or reuse content, interpretations or outputs from any other PDF or earlier execution. Check each output against its own source before moving on.
- Establish each PDF's actual title, edition, covered models and English-language page range from that PDF. Process English content by default unless the user requests another scope; do not assume GE or a fixed page count.
- **Mirror each PDF's input path and basename:** `fridge-docs/model-X/user-guide.pdf` → `fridge-docs/model-X/user-guide.md`. Keep spelling, case and directories. When this prompt calls for HTML, name it `user-guide.html`; when a separate QA report is required, name it `user-guide_QA_Report.md`. Place permitted images in `assets/user-guide/` beside that Markdown, using working relative links. Apply the same pattern to any PDF stem; never mix or overwrite different documents' assets.
- For ZIP input, deliver one output ZIP containing the corresponding files in the **same folder structure**, without merged documents or flattened paths. A “single Markdown file” requirement means **one `.md` per PDF**, not one for the entire ZIP; do not create sidecar content forbidden by this prompt. For an individual PDF, return its corresponding files directly (plus packaging when assets require it).
- Perform coverage, fidelity and asset checks separately for each PDF; disclose per-document limitations without borrowing information from others.

## Objective

Convert each provided PDF into a structured Markdown (`.md`) file with referenced image assets.

This is strictly a **document extraction and format-conversion task**, NOT a summarization, interpretation, rewriting or knowledge-generation task.

## 1. Scope

- Process the English-language portion only, unless otherwise specified.
- Preserve all relevant textual content in its original order.
- Preserve original section headings, instructions, warnings, specifications, tables, lists and model identifiers.
- Do not introduce information from external sources or other documents.

## 2. Text extraction

- Extract text as faithfully as possible.
- Preserve the original wording, numbers, units, symbols and technical terminology.
- Repair corrupted PDF font encodings where the original characters can be recovered reliably.
- Use OCR or visual inspection when the embedded PDF text is unreliable.
- Reconstruct the logical reading order of multi-column pages.
- Do NOT summarize, paraphrase, translate, simplify, interpret or add explanations.
- Do NOT silently correct suspected errors in the original document.
- Mark text as `[UNREADABLE; page N]` if it cannot be recovered reliably.

## 3. Markdown structure

- Convert document headings into appropriate Markdown headings (`#`, `##`, `###`).
- Preserve numbered procedures as numbered lists.
- Preserve bullet points as lists.
- Convert tables into Markdown tables, maintaining the original row and column relationships.
- Preserve warning, caution and note labels.
- Include source PDF page references throughout the document.
- Do not merge unrelated sections or reorder information based on inferred meaning.

## 4. Figures and images

- Preserve important visual information, including diagrams, technical drawings, labelled illustrations and charts.
- Extract only important images, figures, diagrams, technical drawings, labelled illustrations and charts as carefully cropped PNG assets. **Do NOT include full-page images, full-page screenshots or entire rendered PDF pages as image assets.**
- Crop each figure carefully: preserve the complete visual, labels, arrows, legends and relevant callouts; exclude unrelated page text, headers, footers and surrounding content. If a reliable crop cannot be made, report the issue rather than substituting a full-page image.
- Store images in that PDF's `assets/<PDF_STEM>/` directory (relative to its `.md` file).
- Reference each image from its corresponding Markdown section using relative Markdown links.

Example:

```markdown id="caoy3h"
## Features

[Original extracted text]

![Features diagram — PDF page 6](assets/user-guide/page_006_figure_01.png)
```

- Never invent a diagram or image description.
- Do not substitute an AI-generated illustration for an original figure.
- Avoid duplicating images unnecessarily.

## 5. Output files

For each input PDF, produce the same relative path and filename stem as the source. Example for `fridge-docs/model-X/user-guide.pdf`:

```text id="4p36gh"
fridge-docs/
└── model-X/
    ├── user-guide.md
    └── assets/
        └── user-guide/
            ├── page_006_figure_01.png
            ├── page_007_figure_01.png
            └── ...
```

For ZIP input, package all converted documents into one ZIP retaining their input paths; for one PDF, package its Markdown and referenced assets together if needed. Do not use a fixed `document.md` name or flatten directories.

Provide links to the resulting `.md` file(s) and to the final ZIP containing the Markdown and all referenced images when packaging is needed.

Ensure every relative image reference resolves correctly inside the ZIP.

## 6. Quality assurance

Before delivering:

- Verify that every page in the requested scope has been processed.
- Check for omissions, duplicated paragraphs and incorrect reading order.
- Check that important numbers, model codes and units are preserved.
- Verify that tables have not lost or incorrectly combined cells.
- Check for residual corrupted text caused by PDF font encoding.
- Verify that all referenced image files exist.
- Verify that each image is a carefully cropped, complete relevant figure—not a full-page image—and that important labels and callouts have not been cut off.
- Report any pages or sections that could not be faithfully extracted.

## 7. Processing principles

- Prefer deterministic extraction and character repair.
- Use OCR only where necessary.
- Use visual verification to resolve extraction problems, not to rewrite the author's content.
- Do not perform semantic enrichment, technical interpretation or knowledge compilation.
- Do not add external information.
- Do not omit difficult content silently.

**The final Markdown should represent the original document, not what an LLM thinks the document ought to say.**

Execute the conversion, create the files, and provide the download links. Do not merely describe how to perform it.
