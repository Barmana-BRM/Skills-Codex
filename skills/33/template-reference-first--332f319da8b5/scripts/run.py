#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CANONICAL_FILES = [
    "SKILL.md",
    "references/overview.md",
    "references/examples_good.md",
    "references/examples_bad.md",
    "assets/schema.json",
    "scripts/run.py",
]

PLACEHOLDER_MARKERS = [
    "…",
    "TODO",
    "TBD",
    "FIXME",
    "SCAFFOLD",
    "<one paragraph>",
    "<bullet list>",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and summarize a reference-first skill package.")
    parser.add_argument(
        "--package-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Skill package root to inspect.",
    )
    parser.add_argument(
        "--write-manifest",
        default="",
        help="Optional path to write the generated manifest JSON.",
    )
    parser.add_argument(
        "--validate-manifest",
        default="",
        help="Optional path to a manifest JSON file to validate. Defaults to the generated manifest.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if placeholder-style markers appear in text files.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_manifest(package_root: Path) -> dict[str, Any]:
    return {
        "skill_name": package_root.name,
        "purpose": "Demonstrate the reference-first layout for a reusable skill package.",
        "reader_facing": True,
        "references": [
            {
                "path": "references/overview.md",
                "purpose": "Explain role split, progressive disclosure, and customization rules.",
                "load_when": "Read before editing or reusing the template.",
            },
            {
                "path": "references/examples_good.md",
                "purpose": "Show concrete patterns worth copying into new skills.",
                "load_when": "Read when the target skill emits reader-facing text or routes another writer.",
            },
            {
                "path": "references/examples_bad.md",
                "purpose": "Show structural and voice anti-patterns to remove.",
                "load_when": "Read when cleaning up overloaded instructions, hidden defaults, or weak final outputs.",
            },
        ],
        "assets": [
            {
                "path": "assets/schema.json",
                "role": "Machine-readable contract for a reference-first skill manifest.",
            }
        ],
        "script_capabilities": [
            "discovery",
            "validation",
            "manifest",
        ],
        "script_non_goals": [
            "Do not encode domain defaults.",
            "Do not ship reader-facing prose templates.",
            "Do not hide judgment rules that belong in references.",
        ],
        "guardrails": [
            "Keep SKILL.md lean and explicit about which references to read.",
            "Keep references one hop away from SKILL.md.",
            "Keep reader-facing examples complete and free of unresolved placeholders.",
        ],
        "reader_facing_hygiene": {
            "ban_internal_jargon": True,
            "ban_unresolved_placeholders": True,
            "require_complete_examples": True,
        },
    }


def scan_placeholders(package_root: Path) -> list[str]:
    findings: list[str] = []
    files_to_scan = [
        "SKILL.md",
        "references/overview.md",
        "references/examples_good.md",
        "references/examples_bad.md",
    ]
    for rel in files_to_scan:
        path = package_root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        for line_no, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            if "..." in line:
                findings.append(f"{rel}:{line_no}: contains three-dot truncation marker")
            for marker in PLACEHOLDER_MARKERS:
                if marker in line:
                    findings.append(f"{rel}:{line_no}: contains marker {marker!r}")
    return findings


def validate_manifest(manifest: dict[str, Any], schema: dict[str, Any], package_root: Path) -> list[str]:
    errors: list[str] = []
    required = schema.get("required", [])
    for key in required:
        if key not in manifest:
            errors.append(f"manifest missing required key: {key}")

    if not isinstance(manifest.get("references"), list) or not manifest.get("references"):
        errors.append("manifest.references must be a non-empty list")
    if not isinstance(manifest.get("assets"), list) or not manifest.get("assets"):
        errors.append("manifest.assets must be a non-empty list")
    if not isinstance(manifest.get("script_capabilities"), list) or not manifest.get("script_capabilities"):
        errors.append("manifest.script_capabilities must be a non-empty list")

    for rel in CANONICAL_FILES:
        if not (package_root / rel).exists():
            errors.append(f"missing canonical file: {rel}")

    reference_paths = {item.get("path") for item in manifest.get("references", []) if isinstance(item, dict)}
    if "references/overview.md" not in reference_paths:
        errors.append("manifest must include references/overview.md")
    if manifest.get("reader_facing"):
        if "references/examples_good.md" not in reference_paths:
            errors.append("reader-facing manifest must include references/examples_good.md")
        if "references/examples_bad.md" not in reference_paths:
            errors.append("reader-facing manifest must include references/examples_bad.md")

    asset_paths = {item.get("path") for item in manifest.get("assets", []) if isinstance(item, dict)}
    if "assets/schema.json" not in asset_paths:
        errors.append("manifest must include assets/schema.json")

    return errors


def main() -> int:
    args = parse_args()
    package_root = Path(args.package_root).resolve()
    schema_path = package_root / "assets" / "schema.json"

    if not schema_path.exists():
        raise SystemExit(f"missing schema: {schema_path}")

    schema = load_json(schema_path)
    generated_manifest = build_manifest(package_root)

    if args.write_manifest:
        manifest_path = Path(args.write_manifest).resolve()
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(generated_manifest, indent=2) + "\n", encoding="utf-8")

    manifest = generated_manifest
    if args.validate_manifest:
        manifest = load_json(Path(args.validate_manifest).resolve())

    errors = validate_manifest(manifest, schema, package_root)
    if args.strict:
        errors.extend(scan_placeholders(package_root))

    report = {
        "package_root": str(package_root),
        "status": "PASS" if not errors else "FAIL",
        "canonical_files": CANONICAL_FILES,
        "errors": errors,
    }
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
