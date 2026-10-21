# Workflow Notes

## Preflight Checks

1. Confirm that the source PDF is text-layer based:
- `pdftotext -f 5 -l 5 input.pdf - | sed -n '1,20p'`
- If the output is empty or unreadable across multiple sample pages, use OCR before this skill.

2. Confirm whether the cover is image-only:
- `pdfimages -list input.pdf | sed -n '1,40p'`
- If page 1 is a full-page image, expect to replace it separately.

3. Confirm page geometry before and after conversion:
- `pdfinfo input.pdf`
- `pdfinfo output.pdf`

## Font Rules

- Do not write simplified text back with the source PDF's embedded subset font.
- Prefer a full Songti-style font for book text.
- On macOS, `Songti.ttc` is a good source. Use `Light` for most body pages.
- Switch to `Regular` if the converted body text looks too faint.

## What The Converter Actually Does

1. Read each text block with PyMuPDF.
2. Convert each line with OpenCC.
3. Redact only the old text line, while leaving images and graphics alone.
4. Reinsert the simplified line at the original baseline with a replacement font.
5. Save a new PDF with the same page count and page size.

This works well for text-layer PDFs with stable, horizontal book text. It is less reliable for:
- vertical text
- complex mixed-font magazine layouts
- text printed over photographs or colored backgrounds

## Verification Checklist

1. Check text extraction:
- `pdftotext -f 9 -l 9 output.pdf - | sed -n '1,20p'`
- Confirm that no duplicate traditional text remains.

2. Check visual fidelity:
- Render the cover, one body page, and one image-heavy page.
- Confirm that images are still present.
- Confirm that body text is not overly bold.

3. Check metadata if it matters:
- `pdfinfo output.pdf | sed -n '1,20p'`

## Troubleshooting

### Simplified text does not render correctly

- Use a full font via `--font-path`.
- Or point `--font-ttc` to a local TTC and pick a valid face with `scripts/extract_ttc_font.py --list-only`.

### Body text looks too bold

- Retry with `--font-style light`.
- Or use `--font-style regular --font-size-scale 0.98`.

### Baselines look slightly high or low

- Retry with a small offset like `--baseline-y-shift -0.5`.

### Some pages remain traditional

- Those pages may be image-only.
- Replace those pages with `scripts/replace_pdf_cover.py` after generating updated artwork.
