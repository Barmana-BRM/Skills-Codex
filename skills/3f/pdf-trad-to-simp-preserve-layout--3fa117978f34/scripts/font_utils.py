#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import tempfile

from fontTools.ttLib import TTCollection


DEFAULT_TTC_CANDIDATES = (
    Path("/System/Library/Fonts/Supplemental/Songti.ttc"),
    Path("/Library/Fonts/Songti.ttc"),
)

STYLE_PRESETS = {
    "light": ("light", "thin", "ultralight"),
    "regular": ("regular", "book", "roman"),
    "bold": ("bold", "semibold", "demibold", "heavy"),
}


@dataclass(frozen=True)
class TtcFace:
    index: int
    family: str
    subfamily: str
    full_name: str


def _pick_name(name_table, name_id: int) -> str:
    preferred = []
    fallback = []
    for record in name_table.names:
        if record.nameID != name_id:
            continue
        try:
            text = record.toUnicode().strip()
        except Exception:
            continue
        if not text:
            continue
        if record.platformID == 3:
            preferred.append(text)
        else:
            fallback.append(text)
    if preferred:
        return preferred[0]
    if fallback:
        return fallback[0]
    return ""


def list_ttc_faces(ttc_path: str | Path) -> list[TtcFace]:
    collection = TTCollection(str(ttc_path))
    faces = []
    for index, font in enumerate(collection.fonts):
        name_table = font["name"]
        family = _pick_name(name_table, 1)
        subfamily = _pick_name(name_table, 2)
        full_name = _pick_name(name_table, 4) or f"{family} {subfamily}".strip()
        faces.append(
            TtcFace(
                index=index,
                family=family,
                subfamily=subfamily,
                full_name=full_name,
            )
        )
    return faces


def guess_default_ttc() -> Path | None:
    for path in DEFAULT_TTC_CANDIDATES:
        if path.exists():
            return path
    return None


def _score_face(face: TtcFace, family_hint: str | None, style_hint: str | None) -> int:
    haystack = f"{face.family} {face.subfamily} {face.full_name}".lower()
    score = 0

    if family_hint:
        family_lower = family_hint.lower()
        if family_lower in haystack:
            score += 100
        family_tokens = [token for token in re.split(r"[^a-z0-9]+", family_lower) if token]
        score += 10 * sum(1 for token in family_tokens if token in haystack)

    if style_hint:
        style_lower = style_hint.lower()
        preset = STYLE_PRESETS.get(style_lower)
        if preset:
            if any(token in haystack for token in preset):
                score += 50
        elif style_lower in haystack:
            score += 50

    if "songti" in haystack:
        score += 20
    if "sc" in haystack:
        score += 10

    return score


def select_face_index(
    ttc_path: str | Path,
    face_index: int | None = None,
    family_hint: str | None = "Songti SC",
    style_hint: str | None = "light",
) -> int:
    faces = list_ttc_faces(ttc_path)
    if not faces:
        raise ValueError(f"No faces found in TTC: {ttc_path}")

    if face_index is not None:
        if face_index < 0 or face_index >= len(faces):
            raise ValueError(f"Face index {face_index} is out of range for {ttc_path}")
        return face_index

    ranked = sorted(
        ((face, _score_face(face, family_hint, style_hint)) for face in faces),
        key=lambda item: (item[1], -item[0].index),
        reverse=True,
    )
    return ranked[0][0].index


def extract_ttc_face(
    ttc_path: str | Path,
    output_path: str | Path,
    face_index: int | None = None,
    family_hint: str | None = "Songti SC",
    style_hint: str | None = "light",
) -> Path:
    source = Path(ttc_path)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    collection = TTCollection(str(source))
    chosen_index = select_face_index(
        source,
        face_index=face_index,
        family_hint=family_hint,
        style_hint=style_hint,
    )
    collection.fonts[chosen_index].save(str(destination))
    return destination


def resolve_font_path(
    font_path: str | Path | None = None,
    font_ttc: str | Path | None = None,
    face_index: int | None = None,
    family_hint: str | None = "Songti SC",
    style_hint: str | None = "light",
) -> tuple[Path, str | None]:
    if font_path:
        return Path(font_path), None

    ttc_path = Path(font_ttc) if font_ttc else guess_default_ttc()
    if ttc_path is None or not ttc_path.exists():
        raise FileNotFoundError(
            "No usable font was found. Pass --font-path or --font-ttc, "
            "or install a Songti-style TTC locally."
        )

    temp_dir = Path(tempfile.mkdtemp(prefix="pdf-t2s-font-"))
    temp_font = temp_dir / "selected-font.ttf"
    extract_ttc_face(
        ttc_path,
        temp_font,
        face_index=face_index,
        family_hint=family_hint,
        style_hint=style_hint,
    )
    return temp_font, str(temp_dir)


def cleanup_temp_font(temp_dir: str | None) -> None:
    if temp_dir:
        shutil.rmtree(temp_dir, ignore_errors=True)
