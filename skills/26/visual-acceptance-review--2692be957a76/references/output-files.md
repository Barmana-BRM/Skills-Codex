# Output Files

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

## acceptance-summary.md

Required sections:

```markdown
# Visual Acceptance Summary

## Result

## Acceptance Mode

## Inputs

## Screenshots Captured

## Overall Scores

## Blocking Issues

## Conditional Issues

## Browser Health

## Next Step
```

## comparison-report.md

Required sections:

```markdown
# Visual Comparison Report

## Overall Match

## UI Type and Layout Paradigm

## Asset Strategy

## Region Comparison

## Component Completeness

## Color

## Typography

## Spacing

## Responsive

## Browser Health

## Final Decision
```

## region-diffs

Each region diff should include:

```markdown
# Region Diff: [name]

## Expected

## Actual

## Differences

## Severity

## Fix Tasks
```

## blocked-report.md

Required only when blocked.
