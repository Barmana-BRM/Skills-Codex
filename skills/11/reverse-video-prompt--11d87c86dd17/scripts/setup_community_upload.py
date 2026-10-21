#!/usr/bin/env python3
"""Enable or disable opt-in community uploads for reverse-video-prompt."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = SKILL_DIR / "config" / "community-upload.local.json"
DEFAULT_REPO = "zhengzhentao86/reverse-video-prompt"


BRAND_NOTICE = """\
由【镇涛 AI 实战笔记】免费开源，加微信 7838053 学习更多 AI 落地干货

AI 电商实战知识库：https://bvvp9yto7k.feishu.cn/wiki/ZIbrwShfkirvVok3hIHcUz5nnTc
"""


PRIVACY_NOTICE = """\
Community upload is opt-in.

When enabled, reverse-video-prompt may automatically submit iteration cases to
the configured GitHub repository after you use the skill. Submitted content can
include prompt text, product category, reference/generated-video descriptions or
authorized links, user feedback, diagnosis, and reusable-rule notes.

It does not upload raw local video files by default.
Do not include private customer material, unauthorized videos, faces, voices, or
local file paths unless you have the right to share them publicly.
"""


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def gh_is_logged_in() -> bool:
    if shutil.which("gh") is None:
        return False
    proc = run(["gh", "auth", "status", "--hostname", "github.com"], check=False)
    return proc.returncode == 0


def ensure_gh_login(skip_login: bool) -> None:
    if shutil.which("gh") is None:
        raise SystemExit("GitHub CLI `gh` is not installed. Install it first, then rerun setup.")
    if gh_is_logged_in():
        return
    if skip_login:
        raise SystemExit("GitHub CLI is not logged in. Run `gh auth login` first.")
    subprocess.run(
        ["gh", "auth", "login", "--hostname", "github.com", "--web", "--git-protocol", "https"],
        check=True,
    )


def write_config(repo: str, enabled: bool, consent: bool) -> None:
    config: dict[str, Any] = {
        "enabled": enabled,
        "auto_submit": enabled,
        "consent_acknowledged": consent,
        "backend": "github_issue",
        "repo": repo,
        "labels": ["iteration-case", "auto-submitted"],
        "include_prompt": True,
        "include_raw_media": False,
        "include_local_media_paths": False,
        "state_dir": "iteration-cases/.community-state",
        "privacy_notice": "This opt-in uploader submits prompt text, descriptions, links, feedback, and reusable-rule notes to the configured GitHub repository. It does not upload raw local video files.",
    }
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Configure opt-in community uploads.")
    parser.add_argument("--enable", action="store_true", help="Enable automatic GitHub issue submission.")
    parser.add_argument("--disable", action="store_true", help="Disable automatic community uploads.")
    parser.add_argument("--repo", default=DEFAULT_REPO, help=f"Target GitHub repo. Default: {DEFAULT_REPO}")
    parser.add_argument("--yes", action="store_true", help="Acknowledge the privacy notice non-interactively.")
    parser.add_argument("--skip-login", action="store_true", help="Do not launch gh auth login automatically.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(BRAND_NOTICE)

    if args.enable and args.disable:
        raise SystemExit("Use either --enable or --disable, not both.")

    if args.disable:
        write_config(args.repo, enabled=False, consent=False)
        print(f"Community upload disabled: {CONFIG_PATH}")
        return

    if not args.enable:
        raise SystemExit("Choose --enable or --disable.")

    print(PRIVACY_NOTICE)
    if not args.yes:
        answer = input("Type YES to enable automatic community uploads: ").strip()
        if answer != "YES":
            raise SystemExit("Cancelled. Community upload was not enabled.")

    ensure_gh_login(skip_login=args.skip_login)
    write_config(args.repo, enabled=True, consent=True)
    print(f"Community upload enabled: {CONFIG_PATH}")
    print(f"Target repository: {args.repo}")


if __name__ == "__main__":
    main()
