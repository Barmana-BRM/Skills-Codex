from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows).rstrip() + ("\n" if rows else ""), encoding="utf-8")


def _load_fallback_asset() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "assets" / "fallback_subsections.json"
    if not path.exists() or path.stat().st_size <= 0:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _fallback_subsection_seeds(*, section_title: str, target_h3: int, existing_titles: list[str], asset: dict[str, Any]) -> list[dict[str, str]]:
    title_low = str(section_title or "").strip().lower()
    existing = {str(item or "").strip().lower() for item in existing_titles if str(item or "").strip()}
    seeds: list[dict[str, str]] = []

    for rule in asset.get("rules") or []:
        if not isinstance(rule, dict):
            continue
        match_any = [str(item or "").strip().lower() for item in (rule.get("match_any") or []) if str(item or "").strip()]
        if match_any and not any(term in title_low for term in match_any):
            continue
        for item in rule.get("items") or []:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "").strip()
            rationale = str(item.get("rationale") or "").strip()
            if not title or title.lower() in existing:
                continue
            seeds.append(
                {
                    "title": title,
                    "rationale": (rationale or "{title} within {section_title}").format(title=title, section_title=section_title),
                }
            )
            existing.add(title.lower())
            if len(seeds) >= target_h3:
                return seeds

    for item in asset.get("generic_fallbacks") or []:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        rationale = str(item.get("rationale") or "").strip()
        if not title or title.lower() in existing:
            continue
        seeds.append(
            {
                "title": title,
                "rationale": (rationale or "{title} within {section_title}").format(title=title, section_title=section_title),
            }
        )
        existing.add(title.lower())
        if len(seeds) >= target_h3:
            break

    return seeds


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

    from tooling.common import load_yaml, parse_semicolon_list, read_jsonl

    workspace = Path(args.workspace).resolve()
    inputs = parse_semicolon_list(args.inputs) or ["outline/chapter_skeleton.yml", "outline/section_bindings.jsonl", "GOAL.md"]
    outputs = parse_semicolon_list(args.outputs) or ["outline/section_briefs.jsonl"]
    skeleton_path = workspace / inputs[0]
    bindings_path = workspace / inputs[1]
    goal_path = workspace / inputs[2] if len(inputs) > 2 else workspace / "GOAL.md"
    out_path = workspace / outputs[0]

    skeleton = load_yaml(skeleton_path) if skeleton_path.exists() else None
    if not isinstance(skeleton, list) or not skeleton:
        raise SystemExit(f"Invalid chapter skeleton in {skeleton_path}")
    fallback_asset = _load_fallback_asset()
    binding_rows = [row for row in read_jsonl(bindings_path) if isinstance(row, dict)]
    binding_by_id = {str(row.get("section_id") or "").strip(): row for row in binding_rows}
    goal_line = ""
    if goal_path.exists():
        for raw in goal_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if line and not line.startswith("#"):
                goal_line = line
                break

    rows: list[dict[str, Any]] = []
    for chapter in skeleton:
        if not isinstance(chapter, dict):
            continue
        section_id = str(chapter.get("id") or "").strip()
        title = str(chapter.get("title") or "").strip()
        rationale = str(chapter.get("rationale") or "").strip()
        target_h3 = int(chapter.get("target_h3_count") or 3)
        seeds = [str(x).strip() for x in (chapter.get("seed_topics") or []) if str(x).strip()]
        binding = binding_by_id.get(section_id) or {}
        binding_status = str(binding.get("binding_status") or binding.get("status") or "").strip().upper()
        if binding_status not in {"PASS", "BLOCKED", "REROUTE"}:
            if binding.get("blocking_gaps"):
                binding_status = "BLOCKED"
            elif str(binding.get("decomposition_recommendation") or "").strip().lower() == "hold_or_merge":
                binding_status = "REROUTE"
            else:
                binding_status = "PASS"
        decomposition_recommendation = str(binding.get("decomposition_recommendation") or "").strip().lower()
        if decomposition_recommendation not in {"decompose", "hold_or_merge"}:
            decomposition_recommendation = "hold_or_merge" if binding_status == "REROUTE" else "decompose"
        subsection_seeds = [
            {
                "title": seed,
                "rationale": f"{seed} within {title}",
            }
            for seed in seeds[:target_h3]
        ]
        if len(subsection_seeds) < target_h3:
            extra = _fallback_subsection_seeds(
                section_title=title,
                target_h3=target_h3 - len(subsection_seeds),
                existing_titles=[item.get("title") or "" for item in subsection_seeds],
                asset=fallback_asset,
            )
            subsection_seeds.extend(extra)
        rows.append(
            {
                "section_id": section_id,
                "section_title": title,
                "section_rationale": rationale or (f"{title} within {goal_line}" if goal_line else title),
                "contrast_lens": [
                    f"{title} as a chapter-level comparison lens",
                    "cross-paper contrast before H3 stabilization",
                ],
                "must_cover": seeds[: max(2, min(len(seeds), target_h3 + 1))] or [title],
                "target_h3_count": target_h3,
                "subsection_seeds": subsection_seeds,
                "status": binding_status,
                "binding_status": binding_status,
                "decomposition_recommendation": decomposition_recommendation,
                "blocking_gaps": binding.get("blocking_gaps") or [],
            }
        )

    _write_jsonl(out_path, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
