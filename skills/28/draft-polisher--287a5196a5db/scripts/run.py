from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

_CONCRETE_MARKER_RE = re.compile(
    r"\b\d+(?:\.\d+)?%?\b|"
    r"\b[A-Z]{2,}(?:-[A-Z0-9]+)*\b|"
    r"\b[A-Z][a-z]+[A-Z][A-Za-z0-9-]*\b|"
    r"\b[A-Z][A-Za-z0-9]+-[A-Z0-9][A-Za-z0-9-]*\b"
)
_LEADING_WRAPPER_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?i)^A useful reference point is that\s+"), ""),
    (re.compile(r"(?i)^In one representative setting,\s+"), ""),
    (re.compile(r"(?i)^The main qualification is\s+"), ""),
    (re.compile(r"(?i)^Interpretation remains conditional on\s+"), ""),
]


def _sha1(text: str) -> str:
    return hashlib.sha1((text or "").encode("utf-8", errors="ignore")).hexdigest()


def _extract_cites(text: str) -> list[str]:
    keys: set[str] = set()
    for m in re.finditer(r"\[@([^\]]+)\]", text or ""):
        inside = (m.group(1) or "").strip()
        for key in re.findall(r"[A-Za-z0-9:_-]+", inside):
            if key:
                keys.add(key)
    return sorted(keys)


def _merge_adjacent_citation_blocks(text: str) -> str:
    pattern = re.compile(r"(?:\[@[^\]]+\]\s*){2,}")

    def repl(match: re.Match[str]) -> str:
        keys: list[str] = []
        seen: set[str] = set()
        for inside in re.findall(r"\[@([^\]]+)\]", match.group(0)):
            for key in re.findall(r"[A-Za-z0-9:_-]+", inside):
                if key and key not in seen:
                    seen.add(key)
                    keys.append(key)
        return f"[@{'; '.join(keys)}]" if keys else match.group(0)

    merged = pattern.sub(repl, text or "")
    return re.sub(r"\s+([,.;:])", r"\1", merged)


def _h3_citation_sets(md: str) -> dict[str, set[str]]:
    cur_title = ""
    cur_lines: list[str] = []
    out: dict[str, set[str]] = {}

    def flush() -> None:
        nonlocal cur_title, cur_lines
        if not cur_title:
            return
        out[cur_title] = set(_extract_cites("\n".join(cur_lines)))

    for raw in (md or "").splitlines():
        if raw.startswith("### "):
            flush()
            cur_title = raw[4:].strip()
            cur_lines = []
            continue
        if raw.startswith("## "):
            flush()
            cur_title = ""
            cur_lines = []
            continue
        if cur_title:
            cur_lines.append(raw)

    flush()
    return out


def _split_h3_blocks(md: str) -> list[tuple[str | None, list[str]]]:
    blocks: list[tuple[str | None, list[str]]] = []
    current_title: str | None = None
    current_lines: list[str] = []
    for raw in (md or "").splitlines():
        if raw.startswith("### "):
            if current_title is not None:
                blocks.append((current_title, current_lines))
            current_title = raw[4:].strip()
            current_lines = [raw]
            continue
        if raw.startswith("## "):
            if current_title is not None:
                blocks.append((current_title, current_lines))
                current_title = None
                current_lines = []
            blocks.append((None, [raw]))
            continue
        if current_title is not None:
            current_lines.append(raw)
        else:
            if not blocks:
                blocks.append((None, [raw]))
            else:
                blocks[-1][1].append(raw)
    if current_title is not None:
        blocks.append((current_title, current_lines))
    return blocks


def _merge_is_pass(workspace: Path) -> bool:
    report_path = workspace / "output" / "MERGE_REPORT.md"
    if not report_path.exists() or report_path.stat().st_size <= 0:
        return False
    text = report_path.read_text(encoding="utf-8", errors="ignore")
    return "- Status: PASS" in text


def _baseline_should_refresh(*, draft_text: str, baseline_path: Path) -> bool:
    if not baseline_path.exists() or baseline_path.stat().st_size <= 0:
        return True
    expected_sha = _sha1(draft_text)
    for raw in baseline_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            rec = json.loads(raw)
        except Exception:
            return True
        if isinstance(rec, dict) and rec.get("kind") == "meta":
            return str(rec.get("draft_sha1") or "") != expected_sha
        return True
    return True


def _load_writer_packs(path: Path) -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    if not path.exists() or path.stat().st_size <= 0:
        return out
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            rec = json.loads(raw)
        except Exception:
            continue
        if not isinstance(rec, dict):
            continue
        title = str(rec.get("title") or "").strip()
        if title:
            out[title] = rec
    return out


def _clean_phrase(text: str, *, limit: int = 180) -> str:
    cleaned = re.sub(r"\s+", " ", str(text or "").strip())
    cleaned = cleaned.replace("/", " and ")
    cleaned = cleaned.strip(" \"'`")
    if len(cleaned) <= limit:
        return cleaned
    clipped = cleaned[:limit].rsplit(" ", 1)[0].strip()
    return clipped if clipped else cleaned[:limit].strip()


def _cite_block(keys: list[str], limit: int = 4) -> str:
    uniq: list[str] = []
    seen: set[str] = set()
    for key in keys:
        cleaned = str(key or "").strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        uniq.append(cleaned)
        if len(uniq) >= limit:
            break
    return f"[@{'; '.join(uniq)}]" if uniq else ""


def _section_chars_without_cites(text: str) -> int:
    return len(re.sub(r"\[@[^\]]+\]", "", text or ""))


def _normalize_sentence_case(text: str) -> str:
    s = re.sub(r"\s+", " ", str(text or "").strip())
    if not s:
        return ""
    if s[0].islower():
        s = s[0].upper() + s[1:]
    return s


def _strip_leading_wrapper(text: str) -> str:
    s = re.sub(r"\s+", " ", str(text or "").strip())
    if not s:
        return ""
    original = s
    for pattern, repl in _LEADING_WRAPPER_RULES:
        s2 = pattern.sub(repl, s).strip()
        if s2 != s:
            s = s2
            break
    s = _normalize_sentence_case(s)
    if s and s[-1] not in ".!?":
        s += "."
    return s or original


def _looks_like_low_value_generic_paragraph(text: str) -> bool:
    s = re.sub(r"\s+", " ", str(text or "").strip())
    if not s:
        return True
    bare = re.sub(r"\[@[^\]]+\]", "", s).strip()
    if len(bare) < 80:
        return False
    if _CONCRETE_MARKER_RE.search(bare):
        return False
    generic_patterns = [
        r"(?i)^evaluations are critical to assess progress",
        r"(?i)^recent work has advanced such general robot policies",
        r"(?i)^internet-scale data has enabled broad reasoning capabilities",
        r"(?i)^mobile manipulation is the fundamental challenge",
        r"(?i)^foundational datasets, benchmarks, and simulation platforms",
        r"(?i)^the main contribution is a detailed breakdown",
    ]
    return any(re.search(pat, bare) for pat in generic_patterns)


def _paragraph_sent_count(text: str) -> int:
    compact = re.sub(r"\[@[^\]]+\]", "", text or "")
    compact = re.sub(r"\s+", " ", compact).strip()
    if not compact:
        return 0
    return len([s for s in re.split(r"(?<=[.!?])\s+", compact) if s.strip()])


def _paragraph_is_short(text: str) -> bool:
    compact = re.sub(r"\[@[^\]]+\]", "", text or "")
    compact = re.sub(r"\s+", " ", compact).strip()
    if not compact:
        return False
    sent_n = _paragraph_sent_count(compact)
    return sent_n <= 1 or (sent_n <= 2 and len(compact) < 180)


def _fuse_short_h3_block(block_text: str) -> str:
    parts = [p.strip() for p in re.split(r"\n\s*\n", block_text or "") if p.strip()]
    if not parts:
        return block_text
    heading = parts[0] if parts[0].startswith("### ") else ""
    body = parts[1:] if heading else parts[:]
    if len(body) < 4:
        return block_text

    changed = True
    while changed:
        changed = False
        for idx in range(1, len(body)):
            prev = body[idx - 1]
            cur = body[idx]
            prev_len = _section_chars_without_cites(prev)
            cur_len = _section_chars_without_cites(cur)
            if not (_paragraph_is_short(prev) or _paragraph_is_short(cur)):
                continue
            if prev_len + cur_len > 1050:
                continue
            body[idx - 1] = prev.rstrip() + " " + cur.lstrip()
            del body[idx]
            changed = True
            break

    chunks = [heading] if heading else []
    chunks.extend(body)
    return "\n\n".join([c for c in chunks if c]).rstrip()


def _normalize_heading_lines(text: str) -> str:
    lines: list[str] = []
    for raw in (text or "").splitlines():
        if raw.startswith("## ") or raw.startswith("### "):
            head = re.sub(r"\.+\s*$", "", raw.rstrip())
            lines.append(head)
            continue
        lines.append(raw)
    return "\n".join(lines)


def _polish_draft_text(text: str) -> str:
    blocks = re.split(r"(\n\s*\n)", text or "")
    out: list[str] = []
    for block in blocks:
        if not block or re.fullmatch(r"\n\s*\n", block):
            out.append(block)
            continue
        stripped = block.strip()
        if not stripped:
            out.append(block)
            continue
        if stripped.startswith(("#", "|", "```")):
            out.append(block)
            continue
        polished = _strip_leading_wrapper(stripped)
        out.append(polished)
    merged = "".join(out)
    merged = re.sub(r"(?<!\n)(\s+)(###\s+)", r"\n\n\2", merged)
    merged = re.sub(r"(?<!\n)(\s+)(##\s+)", r"\n\n\2", merged)
    parts = [part for part in re.split(r"\n\s*\n", merged) if part.strip()]
    fused: list[str] = []
    for part in parts:
        stripped = part.strip()
        if not fused:
            fused.append(stripped)
            continue
        prev = fused[-1]
        if stripped.startswith("#") or prev.startswith("#"):
            fused.append(stripped)
            continue
        prev_len = _section_chars_without_cites(prev)
        curr_len = _section_chars_without_cites(stripped)
        if prev_len < 500 and curr_len < 500 and (prev_len + curr_len) < 900:
            fused[-1] = prev.rstrip() + " " + stripped.lstrip()
            continue
        fused.append(stripped)
    merged = "\n\n".join(fused)
    merged = _normalize_heading_lines(merged)
    merged = re.sub(r"\n{3,}", "\n\n", merged).rstrip() + "\n"
    return merged


def _top_up_h3_sections(*, draft: str, packs: dict[str, dict[str, object]]) -> str:
    blocks = _split_h3_blocks(draft)
    if not blocks:
        return draft
    out_parts: list[str] = []
    for title, lines in blocks:
        block = "\n".join(lines).rstrip()
        if title is None:
            out_parts.append(block)
            continue
        out_parts.append(_fuse_short_h3_block(block))
    return "\n".join([part for part in out_parts if part is not None]).rstrip() + "\n"


def _top_up_global_citations(*, draft: str, packs: dict[str, dict[str, object]], target: int = 165) -> str:
    return draft


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--unit-id", default="")
    parser.add_argument("--inputs", default="")
    parser.add_argument("--outputs", default="")
    parser.add_argument("--checkpoint", default="")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve()
    for _ in range(10):
        if (repo_root / "AGENTS.md").exists():
            break
        parent = repo_root.parent
        if parent == repo_root:
            break
        repo_root = parent
    sys.path.insert(0, str(repo_root))

    from tooling.common import atomic_write_text, ensure_dir, parse_semicolon_list
    from tooling.quality_gate import check_unit_outputs, write_quality_report

    workspace = Path(args.workspace).resolve()
    unit_id = str(args.unit_id or "U110").strip() or "U110"

    outputs = parse_semicolon_list(args.outputs) or ["output/DRAFT.md"]
    out_rel = outputs[0] if outputs else "output/DRAFT.md"
    draft_path = workspace / out_rel
    packs = _load_writer_packs(workspace / "outline" / "writer_context_packs.jsonl")

    if draft_path.exists() and draft_path.stat().st_size > 0:
        draft_text = draft_path.read_text(encoding="utf-8", errors="ignore")
        draft_text = _polish_draft_text(draft_text)
        draft_text = _top_up_h3_sections(draft=draft_text, packs=packs)
        draft_text = _merge_adjacent_citation_blocks(draft_text)
        if draft_text != draft_path.read_text(encoding="utf-8", errors="ignore"):
            atomic_write_text(draft_path, draft_text)

    baseline_rel = "output/citation_anchors.prepolish.jsonl"
    baseline_path = workspace / baseline_rel
    if draft_path.exists() and draft_path.stat().st_size > 0:
        draft = draft_path.read_text(encoding="utf-8", errors="ignore")
        if _merge_is_pass(workspace) and not re.search(r"(?m)^TODO:\s+MISSING\s+`", draft) and _baseline_should_refresh(draft_text=draft, baseline_path=baseline_path):
            ensure_dir(baseline_path.parent)
            sets = _h3_citation_sets(draft)
            header = {
                "kind": "meta",
                "draft_rel": out_rel,
                "draft_sha1": _sha1(draft),
                "h3_count": len(sets),
            }
            records = [{"kind": "h3", "title": title, "cite_keys": sorted(keys)} for title, keys in sorted(sets.items(), key=lambda kv: kv[0].lower())]
            lines = [json.dumps(header, ensure_ascii=False)] + [json.dumps(rec, ensure_ascii=False) for rec in records]
            atomic_write_text(baseline_path, "\n".join(lines).rstrip() + "\n")

    issues = check_unit_outputs(skill="draft-polisher", workspace=workspace, outputs=[out_rel])
    if issues:
        write_quality_report(workspace=workspace, unit_id=unit_id, skill="draft-polisher", issues=issues)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
