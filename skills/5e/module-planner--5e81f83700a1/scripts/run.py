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

    from tooling.common import dump_yaml, load_yaml, parse_semicolon_list
    from tooling.tutorial_workflows import build_module_plan, load_source_tutorial_spec_data

    workspace = Path(args.workspace).resolve()
    inputs = parse_semicolon_list(args.inputs) or ["outline/concept_graph.yml"]
    outputs = parse_semicolon_list(args.outputs) or ["outline/module_plan.yml"]
    graph_path = workspace / inputs[0]
    out_path = workspace / outputs[0]

    graph = load_yaml(graph_path)
    if not isinstance(graph, dict):
        raise SystemExit(f"Invalid concept graph: {graph_path}")

    spec_data = None
    spec_path = workspace / "output" / "TUTORIAL_SPEC.md"
    if spec_path.exists():
        spec_data = load_source_tutorial_spec_data(spec_path)

    plan = build_module_plan(graph, spec_data=spec_data)
    dump_yaml(out_path, plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
