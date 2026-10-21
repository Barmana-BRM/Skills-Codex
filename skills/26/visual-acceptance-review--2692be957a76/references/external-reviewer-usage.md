# External Reviewer Usage

## Design Fidelity Reviewer

May be used as auxiliary comparison.

If used:

- add findings to region-diffs
- mark `source: design-fidelity-reviewer`
- add `detectedBy: design-fidelity-reviewer`
- convert output into fix-tasks schema

It must not override reference.png or project visual contract.

## Visual UI Verification

May be used as auxiliary confidence source.

If used:

- add `source: visual-ui-verification`
- add `detectedBy: visual-ui-verification`
- use for confidence calibration

If it conflicts with visual-acceptance-review judgment:

- mark review-required
- do not silently override

## Playwright Skill

May be used for:

- screenshot capture
- console errors
- network errors
- browser state

Mark findings:

- `source: playwright-skill`
- `detectedBy: playwright-skill`

Playwright provides browser facts, not design interpretation.

## Script-backed Tools

If pixelmatch / resemblejs / custom scripts exist:

- use for objective diff
- mark `source: script-backed`
- mark `detectedBy: script-backed`

Do not invent scripts.
