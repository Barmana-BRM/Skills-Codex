from __future__ import annotations

import argparse
import sys
from pathlib import Path


VALID_KINDS = {"webpage", "pdf", "markdown", "repo", "docs_site", "video"}
PLACEHOLDER_TOKENS = {"todo", "tbd", "example-source", "replace-me", "https://example.com/source"}


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

    from tooling.common import atomic_write_text, ensure_dir, load_yaml

    workspace = Path(args.workspace).resolve()
    manifest_path = workspace / "sources" / "manifest.yml"
    ensure_dir(manifest_path.parent)

    if not manifest_path.exists():
        atomic_write_text(manifest_path, _template_manifest())
        print(f"Scaffolded {manifest_path}. Replace the example source with real URLs/files and rerun.", file=sys.stderr)
        return 2

    try:
        data = load_yaml(manifest_path)
    except Exception as exc:
        print(f"Invalid YAML in {manifest_path}: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    sources = data.get("sources") if isinstance(data, dict) else None
    if not isinstance(sources, list) or not sources:
        print(f"{manifest_path} must contain a non-empty `sources:` list.", file=sys.stderr)
        return 2

    valid_count = 0
    errors: list[str] = []
    for idx, rec in enumerate(sources, start=1):
        if not isinstance(rec, dict):
            errors.append(f"source #{idx} is not a mapping")
            continue
        source_id = str(rec.get("source_id") or "").strip()
        kind = str(rec.get("kind") or "").strip()
        locator = str(rec.get("locator") or "").strip()
        label = str(rec.get("label") or "").strip()
        transcript_locator = str(rec.get("transcript_locator") or "").strip()

        if not source_id or not label or not locator:
            errors.append(f"source #{idx} is missing required fields")
            continue
        if kind not in VALID_KINDS:
            errors.append(f"source #{idx} has invalid kind `{kind}`")
            continue
        if kind == "video":
            provider = _video_provider(locator)
            if provider == "youtube" and not transcript_locator:
                errors.append(f"source #{idx} is a YouTube video and requires `transcript_locator`")
                continue
            if provider not in {"youtube", "bilibili"} and not transcript_locator:
                errors.append(f"source #{idx} is a generic video source and requires `transcript_locator`")
                continue
        if _looks_like_placeholder(source_id) or _looks_like_placeholder(locator):
            errors.append(f"source #{idx} still contains placeholder values")
            continue
        valid_count += 1

    if errors or valid_count == 0:
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        if valid_count == 0:
            print("No valid sources found in manifest.", file=sys.stderr)
        return 2

    return 0


def _looks_like_placeholder(value: str) -> bool:
    low = str(value or "").strip().lower()
    return any(token in low for token in PLACEHOLDER_TOKENS)


def _video_provider(locator: str) -> str:
    low = str(locator or "").lower()
    if "youtube.com" in low or "youtu.be" in low:
        return "youtube"
    if "bilibili.com" in low or "b23.tv" in low:
        return "bilibili"
    return ""


def _template_manifest() -> str:
    return (
        "sources:\n"
        "  - source_id: example-source\n"
        "    kind: webpage\n"
        "    locator: https://example.com/source\n"
        "    label: Replace With A Real Source\n"
        "    required: true\n"
        "    notes: Replace this scaffold entry with a real URL or local file path.\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
