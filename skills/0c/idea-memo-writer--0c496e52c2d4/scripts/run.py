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

    from tooling.common import load_workspace_pipeline_spec, parse_semicolon_list
    from tooling.ideation import appendix_markdown, build_report_payload, extract_goal_from_goal_md, read_core_set, read_jsonl, report_markdown, resolve_idea_contract, write_json, write_markdown

    workspace = Path(args.workspace).resolve()
    if load_workspace_pipeline_spec(workspace) is None:
        raise SystemExit('Missing or invalid active pipeline contract; fix PIPELINE.lock.md and pipeline metadata before ideation C5.')
    outputs = parse_semicolon_list(args.outputs) or ["output/REPORT.md", "output/APPENDIX.md", "output/REPORT.json"]
    report_rel = next((x for x in outputs if x.endswith('REPORT.md')), 'output/REPORT.md')
    appendix_rel = next((x for x in outputs if x.endswith('APPENDIX.md')), 'output/APPENDIX.md')
    json_rel = next((x for x in outputs if x.endswith('REPORT.json')), 'output/REPORT.json')
    report_path = workspace / report_rel
    appendix_path = workspace / appendix_rel
    json_path = workspace / json_rel

    shortlist_path = workspace / 'output' / 'trace' / 'IDEA_SHORTLIST.jsonl'
    shortlist = [r for r in read_jsonl(shortlist_path) if isinstance(r, dict)]
    try:
        contract = resolve_idea_contract(workspace)
    except Exception as exc:
        raise SystemExit(f'Invalid ideation runtime contract: {exc}')
    core_titles = {row.get('paper_id', ''): row.get('title', row.get('paper_id', '')) for row in read_core_set(workspace / 'papers' / 'core_set.csv') if row.get('paper_id')}
    topic = extract_goal_from_goal_md(workspace / 'GOAL.md')

    report_top_n = int(contract['report_top_n'])
    top = shortlist[:report_top_n]
    deferred = shortlist[report_top_n:]
    for record in deferred:
        if not record.get('why_not_prioritized'):
            record['why_not_prioritized'] = 'worth keeping in mind, but not in the lead discussion set right now.'

    trace_paths = {
        'brief': 'output/trace/IDEA_BRIEF.md',
        'signal_table': 'output/trace/IDEA_SIGNAL_TABLE.md',
        'direction_pool': 'output/trace/IDEA_DIRECTION_POOL.md',
        'screening_table': 'output/trace/IDEA_SCREENING_TABLE.md',
        'shortlist': 'output/trace/IDEA_SHORTLIST.md',
    }
    payload = build_report_payload(topic=topic, shortlist=top, deferred=deferred, trace_paths=trace_paths)

    write_markdown(report_path, report_markdown(payload))
    write_markdown(appendix_path, appendix_markdown(payload, core_titles=core_titles))
    write_json(json_path, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
