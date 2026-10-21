from __future__ import annotations

import argparse
import sys
from pathlib import Path


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
    from tooling.tutorial_workflows import build_source_tutorial_spec, render_source_tutorial_spec_markdown

    workspace = Path(args.workspace).resolve()
    outputs = parse_semicolon_list(args.outputs) or ["output/TUTORIAL_SPEC.md"]
    out_path = workspace / outputs[0]
    ensure_dir(out_path.parent)

    spec = build_source_tutorial_spec(workspace)
    atomic_write_text(out_path, render_source_tutorial_spec_markdown(spec).rstrip() + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
