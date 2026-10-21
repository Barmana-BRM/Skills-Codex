---
name: pdf-trad-to-simp-preserve-layout
description: Convert traditional Chinese PDFs to simplified Chinese while preserving page size, images, selectable text, and overall layout as much as possible. Use when Codex is asked to directly convert a source PDF from 繁体 to 简体 without rebuilding the book, to keep the original PDF structure and pictures, to replace an image-only cover after conversion, or to make the body font lighter after text-layer replacement.
---

# PDF Trad To Simp Preserve Layout

## Overview

Use this skill when layout fidelity matters more than reflowed typography. The bundled scripts keep the original PDF page geometry and images, replace only the text layer on text-based pages, and handle image-only cover pages as a separate replacement step.

## Follow This Workflow

1. Inspect whether the PDF already has a usable text layer.
- Run `pdftotext -f 5 -l 5 input.pdf - | sed -n '1,20p'`.
- If you get readable text, use `scripts/convert_pdf_t2s_preserve_layout.py`.
- If the whole file is scan-only, stop and use OCR first. This skill is not an OCR workflow.

2. Choose a full Chinese font before writing simplified text back into the PDF.
- Do not reuse the source PDF's embedded subset font. Many book PDFs embed only the traditional glyph subset, so simplified text will render incorrectly or disappear.
- Prefer a lighter Songti-style font for book body text.
- On macOS, extract a face from `Songti.ttc` with `scripts/extract_ttc_font.py`, or let the converter auto-detect it.

3. Install the bundled dependencies once.

```bash
SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/pdf-trad-to-simp-preserve-layout"
"$SKILL_DIR/scripts/install_deps.sh"
source "$SKILL_DIR/.venv/bin/activate"
```

4. Convert the text layer without rebuilding the book.

```bash
python "$SKILL_DIR/scripts/convert_pdf_t2s_preserve_layout.py" \
  input.pdf output.pdf \
  --font-style light
```

- Pass `--font-path /path/to/font.ttf` if you already have a suitable full font.
- Pass `--font-ttc /path/to/Songti.ttc --font-style regular` to override automatic font discovery.
- Use `--font-size-scale` or `--baseline-y-shift` only for small visual tuning passes.

5. Replace image-only cover pages separately when needed.

```bash
python "$SKILL_DIR/scripts/replace_pdf_cover.py" \
  output.pdf final.pdf cover.png
```

- Use this when the cover is a full-page image and therefore cannot be fixed by text-layer replacement.
- The replacement preserves page count and the rest of the document.

6. Verify the result before declaring success.
- Run `pdfinfo final.pdf`.
- Run `pdftotext -f 9 -l 9 final.pdf - | sed -n '1,20p'`.
- Render a few pages and compare cover, body text weight, and image pages.
- Read [references/workflow.md](references/workflow.md) for troubleshooting and a more detailed checklist.

## Use These Bundled Tools

- `scripts/install_deps.sh`: Create a skill-local virtual environment and install the required Python packages.
- `scripts/extract_ttc_font.py`: List or extract faces from a `.ttc` collection.
- `scripts/convert_pdf_t2s_preserve_layout.py`: Convert text-layer pages from traditional to simplified Chinese while preserving layout as much as possible.
- `scripts/replace_pdf_cover.py`: Replace a cover or other full-page image page without disturbing the rest of the PDF.
- `references/workflow.md`: Read for preflight checks, font choices, failure modes, and verification steps.
