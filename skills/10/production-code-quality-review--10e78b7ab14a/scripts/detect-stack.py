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
    parser = argparse.ArgumentParser(description="Detect repo stack and suggested references.")
    parser.add_argument("--repo", default=".", help="Path to the git repository.")
    args = parser.parse_args()

    repo = pathlib.Path(args.repo).resolve()
    context = lib.collect_review_context(repo)
    payload = {
        "repo": str(repo),
        "detected_stack": context["detected_stack"],
        "suggested_references": context["suggested_references"],
    }
    sys.stdout.write(lib.to_pretty_json(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
