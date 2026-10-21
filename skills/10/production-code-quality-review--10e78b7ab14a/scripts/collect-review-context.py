#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
import sys


sys.dont_write_bytecode = True
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import review_skill_lib as lib


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect structured review context for a git repo.")
    parser.add_argument("--repo", default=".", help="Path to the git repository.")
    parser.add_argument(
        "--base",
        default=None,
        help="Optional explicit base ref override, such as HEAD or origin/main.",
    )
    parser.add_argument(
        "--scope",
        choices=["branch", "working_tree"],
        default=None,
        help="Optional review scope mode override.",
    )
    args = parser.parse_args()

    repo = pathlib.Path(args.repo).resolve()
    context = lib.collect_review_context(
        repo,
        base_ref_override=args.base,
        scope_mode_override=args.scope,
    )
    sys.stdout.write(lib.to_pretty_json(context))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
