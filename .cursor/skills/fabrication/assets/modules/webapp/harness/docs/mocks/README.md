# UI mock artifacts (portable)

Static **look-and-feel previews** for the **UI-CHOOSE** factory step (`docs/specs/ui-factory-convention.md`).

- **Cursor:** prefer one `.canvas.tsx` (see `ui-choose-look` skill); HTML here is the fallback.
- **Other harnesses:** add `docs/mocks/<feature>-ui-options.html` — one file, 1–3 labeled sections, self-contained CSS.

Do not import these files into the Vite app; they are decision aids only.
