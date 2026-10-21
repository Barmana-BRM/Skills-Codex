---
name: visual-acceptance-review
description: |
  This skill should be used after spec-compliance-review and before
  visual-diff-fix. It captures or analyzes actual browser screenshots and
  compares them against the reference design, responsive spec, visual tokens,
  layout spec, component tree, UI type, layout paradigm, and asset strategy.
  It outputs structured visual diff reports and fix-tasks without modifying code.

argument-hint: "[dev-server-url-or-actual-screenshot]"
---

Version: 2.0.0

# visual-acceptance-review

Validate real browser rendering against the approved visual contract.

This skill performs screenshot-based visual acceptance and produces structured fix tasks.

It does not modify code.
It does not redesign UI.
It does not replace spec-compliance-review.

## Trigger Conditions

Use this skill when:

- implementation exists
- spec-compliance-review has passed or user requests diagnostic-only review
- a dev server URL is available
- Playwright or screenshot capability is available
- user asks to compare implementation against reference image
- user asks for visual acceptance report or visual diff tasks

## Required Inputs

- `reference.png`
- dev server URL or actual screenshot
- UI workflow files under `ui/03_visual_spec/`
- visual spec review files under `ui/04_visual_spec_review/`
- design system files under `ui/05_design_system/`

Recommended:

- spec compliance outputs under `ui/06_spec_review/`
- `package.json`
- `playwright.config.*`

## Preflight Gates

Stop if:

- `ui/04_visual_spec_review/spec-review-report.md` says Fail
- `ui/06_spec_review/compliance-report.md` says Fail, unless user explicitly requests diagnostic-only mode
- no screenshot capability exists and no actual screenshot is provided

## Source of Truth

1. `reference.png`
2. actual browser screenshot
3. `visual-analysis.md / UI Type Classification`
4. `layout-spec.md / Layout Paradigm`
5. `implementation-risks.md / Asset Strategy`
6. `component-tree.md`
7. `tokens.json`
8. `responsive-spec.md`
9. `05_design_system/`
10. browser health logs

## Main Workflow

1. Run preflight gates.
2. Capture or load screenshots.
3. Compare overall visual match.
4. Validate UI Type, Layout Paradigm, and Asset Strategy.
5. Compare regions using layout-spec.md.
6. Compare components using component-tree.md.
7. Compare colors, typography, spacing, and density.
8. Validate responsive screenshots against responsive-spec.md.
9. Capture browser health issues.
10. Generate reports and `fix-tasks.json`.

## Hard Rules

- Do not modify code.
- Do not modify visual spec files.
- Do not modify design system files.
- Do not modify OpenSpec files.
- Do not redesign UI.
- Do not claim pixel-precision if no script-backed comparison exists.
- Do not compare mobile/tablet directly against desktop reference.png.
- Do not allow actual rendering to change UI Type, Layout Paradigm, or Asset Strategy.
- Do not treat passing tests as visual acceptance.
- Do not treat internal spec consistency as visual acceptance.
- If a photorealistic/panorama/scene-led main visual is missing or redrawn with CSS/SVG/chart/map, mark as Fail.

## Output

Write:

```text
07_validation/visual_acceptance/
  screenshots/
    reference.png
    actual-desktop-hd.png
    actual-desktop.png
    actual-tablet.png
    actual-mobile.png
  comparison-report.md
  acceptance-summary.md
  fix-tasks.json
  region-diffs/
    overview.md
    layout.md
    components.md
    colors.md
    typography.md
    spacing.md
    responsive.md
    asset-strategy.md
    browser-health.md
  console-errors.log
  network-errors.log
  blocked-report.md
```

`blocked-report.md` is only required when preflight blocks the review.

## Supporting Files

Read these references directly:

- `references/acceptance-workflow.md`
- `references/preflight-gates.md`
- `references/screenshot-rules.md`
- `references/comparison-rules.md`
- `references/ui-type-asset-validation.md`
- `references/confidence-rules.md`
- `references/fix-task-schema.md`
- `references/external-reviewer-usage.md`
- `references/output-files.md`

Examples:

- `examples/acceptance-summary.example.md`
- `examples/comparison-report.example.md`
- `examples/region-diff.example.md`
- `examples/fix-tasks.example.json`
- `examples/blocked-report.example.md`
