# Idea Memo Writer — Reference-First Overview

## Purpose

This skill produces a structured research idea report from an ideation pipeline's
trace artifacts (`IDEA_SHORTLIST.jsonl`, signal tables, screening tables, etc.).

## Load Order

Always read:
- `references/overview.md` (this file) — orientation
- `references/report_structure.md` — expected sections and formatting

Machine-readable assets:
- `assets/report_schema.json` — JSON schema for the structured report payload

## Script Boundary

Use `scripts/run.py` only for:
- deterministic assembly of the report from trace artifacts
- calling `tooling/ideation.py` library functions for rendering

Do not treat `run.py` as the place for:
- ideation heuristics or scoring logic (those belong in the upstream ideation pipeline)
- hardcoded report prose templates
