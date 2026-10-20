## Source-to-knowledge coverage and QA appendix

**Current Prompt C v4 shard-export audit:**
- Input: `fridge-docs/samsung_RF28K9070SG/repair-guide.pdf` within the original source ZIP.
- Authorized English pages: 12; source PDF exists and cover/last-English-page text was checked programmatically.
- Delivered Markdown shards: **8** (1 preamble, 6 thematic parts, 1 QA appendix).
- Carried-forward substantive knowledge units: **66** (all existing C v3 units retained exactly once).
- Every existing knowledge unit is nested under a `###` heading; major sections begin with `##`.
- This run uses the v4-authorized merger of previously generated C v3 Markdown shards. Technical statements were **not independently re-authored** or fully re-verified against every PDF page.
- No images, HTML, external assets, or linked screenshot files are included.
- The historical QA notes below describe checks carried out during the previous C v3 drafting process; its references to prior shard counts are **historical**, not the present C v4 count.

### QA-APPENDIX — Source-to-knowledge coverage and limitations

**Reference:** Samsung Fast Track Troubleshooting, production DRRF28K9070-060616, 12-page PDF.

**Authorized scope:** PDF pages 1–12.

**Coverage by source page:** 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12.

**Pages without dedicated knowledge units:** None. Administrative, repeated or blank pages may appear here; this is a mapping check, not proof of fully exhaustive technical transcription.

**Shards:** 66 substantive knowledge units, plus preamble and this QA appendix.

**Validation record:**
- Each technical unit is attributed to the Samsung 12-page Fast Track Troubleshooting PDF; no technical claims imported from another model manual.
- All 12 source pages mapped to one or more knowledge units; pages 2 and 9–12 have visual-only or partly rasterized content inspected against rendered original pages.
- 35 printed diagnostic-number records (pages 4–6), 26 load-mode records (page 3), and 68 tabulated sensor values (page 2) transcribed; 68 values need independent second-pass numerical audit before warranty-grade service use.
- The page-12 wiring diagram cannot be translated into a fully verified text-only netlist; a precise original-PDF reference is supplied instead. Such limitations are not disguised as complete wire-level coverage.
- UNKNOWN/answerability controls encoded as distinct units; no live ticket-ranking test was run, so false-abstention rates are not measured.
