# README — Source-isolated Prompt A technician knowledge bases

Four **separately authored** Markdown knowledge bases are provided, one for each source PDF. The original model folder structure and source basenames are retained, with `.pdf` replaced by `.md` and a small `assets/` directory of selectively cropped source figures. The ZIP deliberately **does not include** the original PDFs or their accompanying `.mul.txt` files, and ignores macOS ZIP metadata.

| Output relative path | PDF scope | Source-language pages |
|---|---|---|
| `fridge-docs/ge_GNE27JYMFS/user-guide.md` | GE/GE Profile bottom-freezer user manual | English 1–52 of 156 |
| `fridge-docs/kitchenaid_KRFF507HPS/user-guide.md` | KitchenAid French-door bottom-mount owner manual | English 1–43 of 43 |
| `fridge-docs/samsung_RF28K9070SG/user-guide.md` | Samsung refrigerator user manual | English 1–76 of 220 |
| `fridge-docs/samsung_RF28K9070SG/repair-guide.md` | Samsung technician repair / service sheet | 1–12 of 12 |

## Evidence and isolation rules

- **[DOCUMENTED]** indicates a manufacturer statement from that document; **[UNKNOWN]** flags information absent or insufficiently supported. No technical data or troubleshooting guidance from another PDF was imported into a sibling output.
- A shared model directory is **not** a source-merging permission. `repair-guide.md` is independently based on the repair PDF; `user-guide.md` is independently based on the user PDF.
- The Markdown is a reorganized technician learning/reference resource, **not** a verbatim transcription, and does not include original full-page PDF images.
- Selected diagrams are provided as local relative links. The source PDF remains authoritative if a label, dimension arrow, or diagram needs closer inspection.
- Some manuals apply to **multiple related models and optional features**. Do not assume every optional feature applies to the folder model/suffix without direct support.
- **The Samsung repair guide is intended for trained service technicians only**, not customer DIY electrical diagnostics.

## Validation and limits

- Confirmed all four files are present, UTF-8-readable, include explicit source knowledge/limits and section/page coverage, and every Markdown image link resolves to a valid image.
- Checked sampled high-risk source pages, numeric limits, error tables, filter data and selected procedures, including additional visual inspection for poorly encoded PDF tables.
- **This is not a guaranteed line-by-line audit of all 183 English PDF pages**. Source diagrams and dense data tables may contain details that require a qualified reader to verify against the original PDF before high-stakes use.
- Printed warranty terms and support contacts reflect the source edition and have not been checked for current validity.
