#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from font_utils import extract_ttc_face, list_ttc_faces, select_face_index


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="List or extract a face from a TTC collection."
    )
    parser.add_argument("ttc_path", help="Path to a .ttc font collection")
    parser.add_argument(
        "output_path",
        nargs="?",
        help="Output .ttf path. Omit it when using --list-only.",
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Print available TTC faces and exit.",
    )
    parser.add_argument(
        "--face-index",
        type=int,
        help="Extract a specific face index instead of auto-selecting one.",
    )
    parser.add_argument(
        "--family-hint",
        default="Songti SC",
        help="Preferred family name when auto-selecting a face.",
    )
    parser.add_argument(
        "--style-hint",
        default="light",
        help="Preferred style when auto-selecting a face. Common values: light, regular, bold.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    ttc_path = Path(args.ttc_path)
    if not ttc_path.exists():
        parser.error(f"TTC not found: {ttc_path}")

    faces = list_ttc_faces(ttc_path)
    for face in faces:
        print(f"[{face.index}] {face.full_name} | family={face.family} | style={face.subfamily}")

    if args.list_only:
        return

    if not args.output_path:
        parser.error("output_path is required unless --list-only is used")

    chosen_index = select_face_index(
        ttc_path,
        face_index=args.face_index,
        family_hint=args.family_hint,
        style_hint=args.style_hint,
    )
    output_path = Path(args.output_path)
    extract_ttc_face(
        ttc_path,
        output_path,
        face_index=chosen_index,
        family_hint=args.family_hint,
        style_hint=args.style_hint,
    )
    print(f"Extracted face {chosen_index} to {output_path}")


if __name__ == "__main__":
    main()
