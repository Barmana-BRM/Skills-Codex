# Deliverable Self-Loop — Overview

## What this skill does

The deliverable self-loop is the final quality convergence gate for **non-survey pipeline deliverables** (snapshots, tutorials, synthesis reports, brainstorm memos). It runs a diagnose → fix → re-check loop until the deliverable reaches a publishable bar.

## Trace chain (ideation path)

The brainstorm memo bundle follows a strict trace chain:

```
IDEA_SIGNAL_TABLE → IDEA_DIRECTION_POOL → IDEA_SCREENING_TABLE → IDEA_SHORTLIST → REPORT + APPENDIX
```

Each artifact in the chain must exist and be non-empty before the deliverable is considered complete.

## Convergence model

1. **Diagnose**: run the gate script or manually inspect the deliverable against the quality checklist.
2. **Fix**: address the specific failing checks (missing artifacts, thin sections, templated language).
3. **Re-check**: rerun until the report says `- Status: PASS`.

## When to route upstream

- If the trace chain is incomplete (missing `IDEA_SIGNAL_TABLE`, `IDEA_DIRECTION_POOL`, etc.), fix the upstream skill (`idea-signal-mapper`, `idea-direction-generator`, `idea-screener`, `idea-shortlist-curator`) before rerunning this gate.
- If the `REPORT.md` is thin because the shortlist is weak, improve the shortlist first.
