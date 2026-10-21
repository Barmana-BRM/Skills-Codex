# Bootstrap Assembly

## Purpose

This file describes the compatibility-mode bootstrap that `scripts/run.py` uses when an H3 body file is missing.

The bootstrap is intentionally conservative:
- it assembles a minimal subsection from pack fields
- it does not decide the final prose quality bar
- it exists to create a usable starting file and keep the manifest contract stable

## Assembly contract

The bootstrap should act like a deterministic assembler, not a hidden writing method store.

It may:
- normalize pack fields
- select a small set of comparison, anchor, evaluation, and limitation items
- render those items through machine-readable templates in `assets/`
- write the first-pass subsection file if it does not exist yet

It should not:
- invent new prose policy that is not visible in `references/` or `assets/`
- enforce a hidden paragraph quota
- smuggle in reusable sentence banks from Python constants
- lean on one reusable implementation / caveat closer across many H3s

## Paragraph jobs in bootstrap mode

The bootstrap aims to cover these jobs when the pack supports them:
- opener and thesis
- concrete comparison items
- cross-paper synthesis
- local conclusion or cautious fallback

It does not guarantee a publishable subsection by itself.
Later polishing and writer self-loops still own that quality bar.

## Fallback rule

When a pack is thin:
- keep the subsection conservative
- prefer fewer paragraphs over padded ones
- keep synthesis bounded to what the pack can support

## Where the wording lives now

Reusable bootstrap wording should live in:
- `assets/bootstrap_paragraph_templates.json`
- `assets/paragraph_job_templates.json` for job-level semantic move families

That keeps the script focused on choosing fields and assembling them, while keeping reusable policy inspectable without reading all Python.
