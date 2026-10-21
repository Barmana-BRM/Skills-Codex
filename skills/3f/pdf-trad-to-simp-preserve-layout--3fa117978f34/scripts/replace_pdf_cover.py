#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import fitz


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Replace a PDF page with a full-page image while preserving the rest of the document."
    )
    parser.add_argument("input_pdf", help="Source PDF")
    parser.add_argument("output_pdf", help="Destination PDF")
    parser.add_argument("cover_image", help="Replacement image path")
    parser.add_argument(
        "--page-number",
        type=int,
        default=1,
        help="1-based page number to replace. Default: 1",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    input_pdf = Path(args.input_pdf)
    output_pdf = Path(args.output_pdf)
    image_path = Path(args.cover_image)
    page_index = args.page_number - 1

    if not input_pdf.exists():
        parser.error(f"Input PDF not found: {input_pdf}")
    if not image_path.exists():
        parser.error(f"Cover image not found: {image_path}")

    source = fitz.open(input_pdf)
    if page_index < 0 or page_index >= source.page_count:
        source.close()
        parser.error(f"Page number {args.page_number} is out of range for {input_pdf}")

    metadata = dict(source.metadata or {})
    toc = source.get_toc()
    target_rect = source[page_index].rect

    rebuilt = fitz.open()
    try:
        if page_index > 0:
            rebuilt.insert_pdf(source, from_page=0, to_page=page_index - 1)

        page = rebuilt.new_page(width=target_rect.width, height=target_rect.height)
        page.insert_image(target_rect, filename=str(image_path), keep_proportion=False, overlay=True)

        if page_index < source.page_count - 1:
            rebuilt.insert_pdf(source, from_page=page_index + 1, to_page=source.page_count - 1)

        if toc:
            rebuilt.set_toc(toc)
        rebuilt.set_metadata(metadata)
        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        rebuilt.save(output_pdf, garbage=4, deflate=True)
    finally:
        rebuilt.close()
        source.close()

    print(f"saved={output_pdf}")
    print(f"replaced_page={args.page_number}")


if __name__ == "__main__":
    main()
