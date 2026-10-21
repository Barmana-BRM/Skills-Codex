from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def _ordered_options(seed: str, options: list[str]) -> list[str]:
    if not options:
        return []
    idx = sum(ord(ch) for ch in (seed or '')) % len(options)
    return options[idx:] + options[:idx]


def _clean(text: str) -> str:
    return re.sub(r'\s+', ' ', str(text or '').strip())


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not path.exists() or path.stat().st_size <= 0:
        return out
    for raw in path.read_text(encoding='utf-8', errors='ignore').splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            rec = json.loads(raw)
        except Exception:
            continue
        if isinstance(rec, dict):
            out.append(rec)
    return out


def _load_outline(path: Path) -> list[dict[str, Any]]:
    try:
        import yaml  # type: ignore
    except Exception:
        return []
    if not path.exists() or path.stat().st_size <= 0:
        return []
    data = yaml.safe_load(path.read_text(encoding='utf-8', errors='ignore'))
    return data if isinstance(data, list) else []


def _terms(brief: dict[str, Any]) -> list[str]:
    vals: list[str] = []
    for key in ('bridge_terms', 'axes'):
        for item in (brief.get(key) or []):
            term = _clean(str(item or '')).lower().replace('/', ' and ')
            if not term:
                continue
            if term not in vals:
                vals.append(term)
    return vals


def _pick_shared(a: dict[str, Any], b: dict[str, Any]) -> str:
    a_terms = _terms(a)
    b_terms = _terms(b)
    for term in a_terms:
        if term in b_terms:
            return term
    return b_terms[0] if b_terms else (a_terms[0] if a_terms else 'the same comparative pressure')


def _transition(a: dict[str, str], b: dict[str, str], a_brief: dict[str, Any], b_brief: dict[str, Any]) -> str:
    a_title = _clean(a.get('title') or '').lower()
    b_title = _clean(b.get('title') or '').lower()
    shared = _pick_shared(a_brief, b_brief)
    options = [
        'The same pressure reappears in {b_title}, where {shared} becomes harder to separate from the rest of the evidence.',
        'That comparison becomes sharper in {b_title}, because {shared} now has to be read under a different set of assumptions.',
        'The next issue is {b_title}, where the earlier tension around {shared} becomes more concrete.',
        '{b_title_cap} turns the earlier concern about {shared} into a more explicit comparison problem.',
    ]
    template = _ordered_options(f"{a.get('id')}->{b.get('id')}", options)[0]
    return template.format(
        a_title=a_title,
        b_title=b_title,
        b_title_cap=(b_title[:1].upper() + b_title[1:]) if b_title else _clean(b.get('title') or ''),
        shared=shared,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', required=True)
    parser.add_argument('--unit-id', default='')
    parser.add_argument('--inputs', default='')
    parser.add_argument('--outputs', default='')
    parser.add_argument('--checkpoint', default='')
    args = parser.parse_args()

    repo_root = Path(__file__).resolve()
    for _ in range(10):
        if (repo_root / 'AGENTS.md').exists():
            break
        parent = repo_root.parent
        if parent == repo_root:
            break
        repo_root = parent
    sys.path.insert(0, str(repo_root))

    from tooling.common import atomic_write_text, ensure_dir, parse_semicolon_list
    from tooling.quality_gate import check_unit_outputs, write_quality_report

    workspace = Path(args.workspace).resolve()
    unit_id = str(args.unit_id or 'U098').strip() or 'U098'
    outputs = parse_semicolon_list(args.outputs) or ['outline/transitions.md']
    out_rel = outputs[0] if outputs else 'outline/transitions.md'
    out_path = workspace / out_rel
    ensure_dir(out_path.parent)

    outline = _load_outline(workspace / 'outline' / 'outline.yml')
    briefs = {str(rec.get('sub_id') or '').strip(): rec for rec in _load_jsonl(workspace / 'outline' / 'subsection_briefs.jsonl') if str(rec.get('sub_id') or '').strip()}

    lines: list[str] = []
    for sec in outline:
        if not isinstance(sec, dict):
            continue
        subs = [sub for sub in (sec.get('subsections') or []) if isinstance(sub, dict) and str(sub.get('id') or '').strip() and str(sub.get('title') or '').strip()]
        if len(subs) < 2:
            continue
        for a, b in zip(subs, subs[1:]):
            a_id = str(a.get('id') or '').strip()
            b_id = str(b.get('id') or '').strip()
            sentence = _transition(a, b, briefs.get(a_id) or {}, briefs.get(b_id) or {})
            lines.append(f'- {a_id} -> {b_id}: {sentence}')

    atomic_write_text(out_path, '\n'.join(lines).rstrip() + '\n')

    issues = check_unit_outputs(skill='transition-weaver', workspace=workspace, outputs=[out_rel])
    if issues:
        write_quality_report(workspace=workspace, unit_id=unit_id, skill='transition-weaver', issues=issues)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
