# Overview

## Purpose

This reference set moves front-matter writing judgment out of `scripts/run.py` and into compact, selective guidance.

Use it to keep the current pipeline behavior compatible while reducing hardcoded prose pressure.

## What stays in code

Keep scripts responsible for:
- discovering inputs and output paths
- validating approval and prerequisites
- counting / parsing metadata
- writing files that already have approved content

Keep scripts out of:
- fixed domain defaults
- canned front-matter paragraphs
- reader-facing opener banks
- list-shaped prose skeletons that force every paper into the same shape

## What lives in these references

- `abstract_archetypes.md`: how to choose an abstract shape without freezing a sentence template
- `context_projection.md`: how chapter-level structure should be projected into front-matter context values
- `introduction_jobs.md`: paragraph jobs for Introduction and the single methodology note
- `related_work_positioning.md`: how to position related work through a lens instead of a survey dump
- `forbidden_stems.md`: high-signal phrases to rewrite or avoid
- `examples_good.md`: compact positive examples (paraphrase, don’t copy)
- `examples_bad.md`: compact negative examples and why they fail

## Load order

Recommended selective reading order:
1. Read this file.
2. If writing `Abstract`, read `abstract_archetypes.md`.
3. If writing `Introduction`, read `introduction_jobs.md` and `forbidden_stems.md`.
4. If writing `Related Work`, read `related_work_positioning.md` and `forbidden_stems.md`.
5. If checking voice or examples, read `examples_good.md` and `examples_bad.md`.

## Compatibility notes

This pack assumes the current pipeline contract still holds:
- outputs remain `sections/abstract.md`, `sections/S<sec_id>.md`, `sections/discussion.md`, `sections/conclusion.md`
- the methodology note appears once, in normal prose, usually in Introduction or Related Work
- citations must already exist in `citations/ref.bib`
- no internal pipeline jargon should appear in reader-facing text

## Reader-facing hygiene

For front matter, prioritize:
- content-bearing opening sentences over self-narration
- one clear survey lens over many axis lists
- one methodology paragraph over repeated evidence disclaimers
- gap statements tied to comparison meaning, not generic “more research is needed” closers
