# Overview

## Purpose

This pack moves subsection-writing judgment out of `scripts/run.py` and into compact references.

Compatibility mode:
- keep the current pipeline contract and output paths
- keep the helper script for manifest generation and missing-file bootstrap
- stop treating the script as the source of paragraph shape or prose policy

## What stays in code

Keep scripts responsible for:
- approval / prerequisite checks
- manifest generation
- missing-file discovery
- writing a minimal bootstrap when a section file does not exist yet

Keep scripts out of:
- fixed paragraph counts
- canned opener banks
- reusable synthesis shell sentences
- reusable limitation / implementation shell closers
- filler paragraphs added only to satisfy a quota

## What lives in references

- `paragraph_jobs.md`: subsection-level jobs and move coverage
- `paragraph_job_archetypes.md`: semantic intent and anti-patterns for each paragraph family
- `bootstrap_assembly.md`: what the compatibility bootstrap may assemble and where that wording now lives
- `opener_catalog.md`: opener modes and when to use them
- `contrast_moves.md`: safe A-vs-B comparison patterns
- `eval_anchor_patterns.md`: protocol-aware evaluation anchoring
- `limitation_moves.md`: ways to state limitations without slot phrases
- `examples_good.md`: compact positive patterns
- `examples_bad.md`: compact anti-patterns

## Load order

Recommended selective reading:
1. Read this file.
2. Read `paragraph_jobs.md` before drafting or rewriting an H3.
3. Read `paragraph_job_archetypes.md` when a paragraph family starts sounding templated or too similar across H3s.
4. Read `bootstrap_assembly.md` when inspecting or revising the compatibility bootstrap.
5. Read `opener_catalog.md` when paragraph 1 sounds generic.
6. Read `contrast_moves.md` and `eval_anchor_patterns.md` when writing comparison-heavy paragraphs.
7. Read `limitation_moves.md` before closing or qualifying a subsection.
8. Read `examples_good.md` / `examples_bad.md` only for calibration.

## Compatibility note

The current script may still create missing H3 files, but the durable contract is:
- H3 prose quality is decided by evidence + references + later self-loops
- the script is a bootstrap helper, not the writing authority
