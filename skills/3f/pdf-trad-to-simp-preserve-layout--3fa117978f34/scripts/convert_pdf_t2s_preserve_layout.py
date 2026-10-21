#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import fitz
from opencc import OpenCC

from font_utils import cleanup_temp_font, resolve_font_path


def pdf_color_to_rgb(value: int | None) -> tuple[float, float, float]:
    if value is None:
        return (0.0, 0.0, 0.0)
    return (
        ((value >> 16) & 255) / 255.0,
        ((value >> 8) & 255) / 255.0,
        (value & 255) / 255.0,
    )


def is_horizontal(line: dict) -> bool:
    direction = line.get("dir")
    if not direction:
        return True
    dx, dy = direction
    return abs(dx) > 0.99 and abs(dy) < 0.01


def line_text(spans: list[dict]) -> str:
    return "".join(span.get("text", "") for span in spans)


def convert_metadata(doc: fitz.Document, cc: OpenCC) -> None:
    metadata = dict(doc.metadata or {})
    for key in ("title", "author", "subject", "keywords"):
        value = metadata.get(key)
        if value:
            metadata[key] = cc.convert(value)
    doc.set_metadata(metadata)


def convert_page(
    page: fitz.Page,
    cc: OpenCC,
    font_path: Path,
    font_name: str,
    font_size_scale: float,
    baseline_y_shift: float,
) -> int:
    replacements = []
    modified_lines = 0

    blocks = page.get_text("dict").get("blocks", [])
    for block in blocks:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            spans = [span for span in line.get("spans", []) if span.get("text")]
            if not spans or not is_horizontal(line):
                continue

            original = line_text(spans)
            simplified = cc.convert(original)
            if simplified == original:
                continue

            bbox = fitz.Rect(line["bbox"])
            if bbox.is_empty:
                continue

            anchor_span = next((span for span in spans if span.get("text", "").strip()), spans[0])
            origin = anchor_span.get("origin") or (bbox.x0, bbox.y1)
            replacements.append(
                {
                    "point": fitz.Point(origin[0], origin[1] + baseline_y_shift),
                    "text": simplified,
                    "fontsize": anchor_span.get("size", 12.0) * font_size_scale,
                    "color": pdf_color_to_rgb(anchor_span.get("color")),
                }
            )
            page.add_redact_annot(bbox, fill=(1, 1, 1))
            modified_lines += 1

    if not replacements:
        return 0

    page.apply_redactions(images=0, graphics=0, text=0)
    page.insert_font(fontname=font_name, fontfile=str(font_path))
    for item in replacements:
        page.insert_text(
            item["point"],
            item["text"],
            fontsize=item["fontsize"],
            fontname=font_name,
            color=item["color"],
            overlay=True,
        )
    return modified_lines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Convert a traditional Chinese PDF to simplified Chinese while "
            "preserving layout, images, and selectable text where possible."
        )
    )
    parser.add_argument("input_pdf", help="Source PDF")
    parser.add_argument("output_pdf", help="Destination PDF")
    parser.add_argument(
        "--opencc-config",
        default="t2s",
        help="OpenCC config name. Default: t2s",
    )
    parser.add_argument(
        "--font-path",
        help="Path to a full Chinese font file (.ttf/.otf).",
    )
    parser.add_argument(
        "--font-ttc",
        help="Path to a .ttc collection to extract a font from on the fly.",
    )
    parser.add_argument(
        "--font-face-index",
        type=int,
        help="Specific TTC face index to use when extracting from a .ttc file.",
    )
    parser.add_argument(
        "--family-hint",
        default="Songti SC",
        help="Preferred font family when auto-selecting a TTC face.",
    )
    parser.add_argument(
        "--font-style",
        default="light",
        help="Preferred font style. Common values: light, regular, bold.",
    )
    parser.add_argument(
        "--font-size-scale",
        type=float,
        default=1.0,
        help="Multiply the detected font size by this value.",
    )
    parser.add_argument(
        "--baseline-y-shift",
        type=float,
        default=0.0,
        help="Add a Y offset to every replacement line baseline.",
    )
    parser.add_argument(
        "--skip-metadata-conversion",
        action="store_true",
        help="Leave PDF metadata unchanged.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    input_pdf = Path(args.input_pdf)
    output_pdf = Path(args.output_pdf)
    if not input_pdf.exists():
        parser.error(f"Input PDF not found: {input_pdf}")

    font_path, temp_dir = resolve_font_path(
        font_path=args.font_path,
        font_ttc=args.font_ttc,
        face_index=args.font_face_index,
        family_hint=args.family_hint,
        style_hint=args.font_style,
    )

    cc = OpenCC(args.opencc_config)
    doc = fitz.open(input_pdf)
    font_name = "customzhfont"

    modified_pages = 0
    modified_lines = 0

    try:
        for page in doc:
            line_count = convert_page(
                page,
                cc,
                font_path=font_path,
                font_name=font_name,
                font_size_scale=args.font_size_scale,
                baseline_y_shift=args.baseline_y_shift,
            )
            if line_count:
                modified_pages += 1
                modified_lines += line_count

        if not args.skip_metadata_conversion:
            convert_metadata(doc, cc)

        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        doc.save(output_pdf, garbage=4, deflate=True)
    finally:
        doc.close()
        cleanup_temp_font(temp_dir)

    print(f"saved={output_pdf}")
    print(f"modified_pages={modified_pages}")
    print(f"modified_lines={modified_lines}")


if __name__ == "__main__":
    main()
