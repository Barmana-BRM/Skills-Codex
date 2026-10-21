# Fix Task Schema

`fix-tasks.json` must be an array.

## Schema

```json
{
  "id": "VAR-001",
  "source": "reference-visible",
  "detectedBy": ["visual-acceptance-review"],
  "strictness": "required",
  "viewport": "desktop",
  "region": "SceneImageLayer",
  "component": "SceneImageLayer",
  "issueType": "asset_strategy_violation",
  "issue": "Main panorama image is missing and replaced by SVG visualization.",
  "expected": "Use approved raster scene asset as the main SceneImageLayer.",
  "actual": "Rendered SVG map/gradient as main visual.",
  "sourceOfTruth": "ui/03_visual_spec/implementation-risks.md",
  "fileHint": "src/App.tsx",
  "fixType": "restore_asset_strategy",
  "priority": "high",
  "confidenceTier": "tier-2",
  "confidence": 0.92,
  "blocking": true
}
```

## Required Fields

- id
- source
- detectedBy
- strictness
- viewport
- region
- component
- issueType
- issue
- expected
- actual
- sourceOfTruth
- fixType
- priority
- confidenceTier
- confidence
- blocking

## issueType Values

- overall_mismatch
- ui_type_drift
- layout_paradigm_drift
- asset_strategy_violation
- missing_component
- prohibited_component
- forbidden_layout
- color_mismatch
- typography_mismatch
- spacing_mismatch
- responsive_mismatch
- browser_error
- network_error
- needs_human_review

## fixType Values

- restore_ui_type
- restore_layout_paradigm
- restore_asset_strategy
- add_missing_component
- remove_prohibited_component
- remove_forbidden_layout
- token_reference
- adjust_typography
- adjust_spacing
- fix_responsive
- fix_browser_error
- fix_network_error
- needs_human_review

## priority

Use:

- high
- medium
- low

Blocking issues should be high.
