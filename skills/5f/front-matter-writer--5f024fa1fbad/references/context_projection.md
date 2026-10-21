# Context Projection

## Purpose

Front matter should not infer its comparative lens from hidden Python heuristics.
The projection from chapter briefs into `chapter_theme`, `chapter_focus_summary`, `chapter_key_contrast`, and the global summary values should be inspectable.

## What belongs in the asset

`assets/front_matter_context_projection.json` should own:
- title-keyword -> `chapter_theme` rules
- how many `throughline` / `key_contrasts` items survive into front matter
- how chapters are grouped for repeated related-work positioning
- how many focus / contrast items contribute to `lens_summary` and `comparison_summary`

## Script boundary

`scripts/run.py` should only:
- read the projection asset
- apply the declared rules deterministically
- pass the projected values into the renderer

It should not silently decide new theme buckets or grouping policies in code.
