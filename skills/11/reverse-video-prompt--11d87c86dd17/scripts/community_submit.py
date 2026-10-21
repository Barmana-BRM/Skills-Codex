#!/usr/bin/env python3
"""Submit reverse-video-prompt iteration data to the configured community backend."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = SKILL_DIR / "config" / "community-upload.local.json"
CHANGE_LEVELS = [
    "prompt-only",
    "candidate skill rule",
    "reference-template update",
    "eval case",
    "tooling",
]


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "iteration-case"


def read_value(text: str | None, file_path: str | None) -> str:
    if text and file_path:
        raise SystemExit("Use either inline text or file input, not both.")
    if file_path:
        return Path(file_path).expanduser().read_text(encoding="utf-8")
    return text or ""


def load_config(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, f"config not found: {path}"
    config = json.loads(path.read_text(encoding="utf-8"))
    if not config.get("enabled"):
        return None, "community upload disabled"
    if not config.get("auto_submit"):
        return None, "auto_submit disabled"
    if not config.get("consent_acknowledged"):
        return None, "consent not acknowledged"
    if config.get("backend") != "github_issue":
        return None, f"unsupported backend: {config.get('backend')}"
    return config, None


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise SystemExit(f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr or proc.stdout}")
    return proc.stdout.strip()


def run_issue_create(cmd: list[str], labels: list[str]) -> str:
    proc = subprocess.run(cmd, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode == 0:
        return proc.stdout.strip()
    if not labels:
        raise SystemExit(f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr or proc.stdout}")

    fallback = []
    skip_next = False
    for item in cmd:
        if skip_next:
            skip_next = False
            continue
        if item == "--label":
            skip_next = True
            continue
        fallback.append(item)

    fallback_proc = subprocess.run(fallback, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if fallback_proc.returncode != 0:
        raise SystemExit(
            f"Command failed ({fallback_proc.returncode}): {' '.join(fallback)}\n"
            f"{fallback_proc.stderr or fallback_proc.stdout}"
        )
    return fallback_proc.stdout.strip()


def section(title: str, value: str) -> list[str]:
    if not value:
        return []
    return [f"### {title}", "", value.strip(), ""]


def build_body(args: argparse.Namespace, prompt_used: str) -> str:
    created_at = datetime.now(timezone.utc).isoformat()
    lines = [
        "## reverse-video-prompt Community Case",
        "",
        f"- Stage: `{args.stage}`",
        f"- Case ID: `{args.case_id}`",
        f"- Submitted at: `{created_at}`",
        "",
        "> This case was submitted after local opt-in. Raw local video files are not uploaded by this script.",
        "",
    ]
    fields = [
        ("Product category", args.product_category),
        ("Target platform/model", args.target_platform),
        ("Reference", args.reference_desc),
        ("Reference link", args.reference_link),
        ("Generated attempt", args.generated_desc),
        ("Generated attempt link", args.generated_link),
        ("Observed failure", args.observed_failure),
        ("User feedback", args.user_feedback),
        ("Root cause", args.root_cause),
        ("Reusable rule", args.reusable_rule),
        ("Prompt fix summary", args.prompt_fix_summary),
        ("Change level", args.change_level),
        ("Privacy note", args.privacy_note),
    ]
    for title, value in fields:
        lines.extend(section(title, value or ""))
    if prompt_used:
        lines.extend(["### Prompt used", "", "```text", prompt_used.strip(), "```", ""])
    lines.extend(
        [
            "### Safety checklist",
            "",
            "- [x] The uploader did not attach raw local media files.",
            "- [x] The uploader used an explicit local opt-in config.",
            "- [ ] Maintainer reviewed whether this should become a reusable rule, eval case, or prompt-only learning.",
            "",
        ]
    )
    return "\n".join(lines)


def state_path(config: dict[str, Any], case_id: str) -> Path:
    state_dir = Path(config.get("state_dir", "iteration-cases/.community-state"))
    if not state_dir.is_absolute():
        state_dir = SKILL_DIR / state_dir
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / f"{slugify(case_id)}.json"


def load_state(config: dict[str, Any], case_id: str) -> dict[str, Any]:
    path = state_path(config, case_id)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(config: dict[str, Any], case_id: str, state: dict[str, Any]) -> None:
    path = state_path(config, case_id)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_issue_number(url: str) -> str:
    match = re.search(r"/issues/(\d+)(?:$|[?#])", url)
    if not match:
        raise SystemExit(f"Could not parse issue number from: {url}")
    return match.group(1)


def write_temp_body(body: str) -> str:
    tmp = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md")
    with tmp:
        tmp.write(body)
    return tmp.name


def submit(config: dict[str, Any], args: argparse.Namespace, body: str) -> dict[str, Any]:
    repo = config["repo"]
    labels = config.get("labels", [])
    state = load_state(config, args.case_id)
    issue_number = args.issue_number or state.get("issue_number")
    body_file = write_temp_body(body)

    if issue_number:
        run(["gh", "issue", "comment", str(issue_number), "--repo", repo, "--body-file", body_file])
        issue_url = state.get("issue_url") or f"https://github.com/{repo}/issues/{issue_number}"
        state.update({"issue_number": str(issue_number), "issue_url": issue_url, "repo": repo})
        save_state(config, args.case_id, state)
        return {"created": False, "issue_number": str(issue_number), "issue_url": issue_url}

    cmd = [
        "gh",
        "issue",
        "create",
        "--repo",
        repo,
        "--title",
        args.title,
        "--body-file",
        body_file,
    ]
    for label in labels:
        cmd.extend(["--label", label])
    issue_url = run_issue_create(cmd, labels)
    issue_number = parse_issue_number(issue_url)
    state.update({"issue_number": issue_number, "issue_url": issue_url, "repo": repo})
    save_state(config, args.case_id, state)
    return {"created": True, "issue_number": issue_number, "issue_url": issue_url}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit an opt-in community iteration case.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--dry-run", action="store_true", help="Print the issue/comment body without uploading.")
    parser.add_argument("--stage", choices=["prompt", "feedback", "success", "manual"], default="manual")
    parser.add_argument("--title", required=True)
    parser.add_argument("--case-id")
    parser.add_argument("--issue-number")
    parser.add_argument("--product-category", default="")
    parser.add_argument("--target-platform", default="")
    parser.add_argument("--prompt-text")
    parser.add_argument("--prompt-file")
    parser.add_argument("--reference-desc", default="")
    parser.add_argument("--reference-link", default="")
    parser.add_argument("--generated-desc", default="")
    parser.add_argument("--generated-link", default="")
    parser.add_argument("--observed-failure", default="")
    parser.add_argument("--user-feedback", default="")
    parser.add_argument("--root-cause", default="")
    parser.add_argument("--reusable-rule", default="")
    parser.add_argument("--prompt-fix-summary", default="")
    parser.add_argument("--change-level", choices=CHANGE_LEVELS, default="prompt-only")
    parser.add_argument(
        "--privacy-note",
        default="No raw local media files were uploaded. Any links or screenshots should be shared only with permission.",
    )
    args = parser.parse_args()
    args.case_id = args.case_id or slugify(args.title)
    return args


def main() -> None:
    args = parse_args()
    config, skip_reason = load_config(Path(args.config).expanduser())
    prompt_used = read_value(args.prompt_text, args.prompt_file)
    body = build_body(args, prompt_used)

    if args.dry_run:
        print(body)
        return

    if config is None:
        print(json.dumps({"ok": True, "skipped": True, "reason": skip_reason}, ensure_ascii=False))
        return

    result = submit(config, args, body)
    print(json.dumps({"ok": True, "skipped": False, **result}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
