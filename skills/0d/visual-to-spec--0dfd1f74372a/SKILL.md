---
name: visual-to-spec
description: |
  Use when a user provides a reference UI screenshot and asks to extract visual
  specs, generate design tokens, create a component tree, or produce a frontend
  implementation contract, including dashboards, landing pages, mobile screens,
  image-led UIs, panorama scenes, 3D exhibit UIs, and screenshot-to-spec tasks.
argument-hint: "[reference-image]"
---
Version: 2.0.0

# visual-to-spec

Convert a finalized UI screenshot into a complete frontend implementation contract.

## Trigger Conditions

- User provides a UI screenshot and asks to extract visual specs
- User asks to generate design tokens from a screenshot
- User asks to build a component tree or frontend implementation contract from a screenshot
- User asks to analyze screenshot layout, color, typography, spacing, overlay controls, or panorama/3D scene UI
- Keywords: "extract spec from screenshot", "image to design spec", "screenshot to spec"

## Required Inputs

| Item | Description |
|------|-------------|
| reference.png | Finalized UI screenshot (the only required input) |
| Project token standards | Optional, adapt to existing standards if available |

## Outputs

All files written to `03_visual_spec/` directory:

| File | Content |
|------|---------|
| visual-analysis.md | UI type, visible element evidence, composition, color, typography, spacing analysis |
| layout-spec.md | Layout positioning and sizing spec, branching by UI type |
| component-tree.md | Hierarchical component tree with per-component style summaries |
| tokens.json | DTCG-inspired design tokens with source/confidence annotations |
| implementation-risks.md | Implementation risk assessment |
| human-review-needed.md | Low-confidence items and manual review checklist |
| DESIGN.md | Summary document referencing all above files |

See `references/output-files.md` for detailed output formats.

## Source of Truth

**reference.png is the sole visual source of truth.**

- Do not redesign.
- Do not treat UI elements invisible in the screenshot as screenshot facts.
- Do not introduce colors, fonts, spacing, panels, charts, or navigation structures absent from the image.
- Do not default to a dashboard / SaaS / three-column layout; UI type determination must come first.
- `reference-visible` components must have bbox and visual evidence in the screenshot; components without bbox must not be labeled `reference-visible`.
- Inferred implementation wrapper components (e.g., AppShell, MainContent, SceneImageLayer, OverlayLayer) are permitted but must be labeled `source: inferred-implementation`.
- For image-led, panorama-scene, 3D exhibit, and product-render screenshots, output an asset strategy: which visual content must be raster/image assets, and which can be implemented as HTML/CSS/SVG.

All values must carry source and confidence annotations.
See `references/source-strictness-rules.md` for complete rules.

## Phase Overview (9 phases, sequential)

| # | Phase | Key Output |
|---|-------|------------|
| 1 | Global composition analysis + UI type determination + visible element evidence | visual-analysis.md §1 |
| 2 | Color extraction | visual-analysis.md §2 + tokens.json (color) |
| 3 | Typography extraction | visual-analysis.md §3 + tokens.json (typography) |
| 4 | Spacing and grid system | visual-analysis.md §4 + tokens.json (spacing) |
| 5 | Layout specification | layout-spec.md |
| 6 | Component tree construction | component-tree.md |
| 7 | Token merge and validation | tokens.json (final) |
| 8 | Implementation risk assessment | implementation-risks.md |
| 9 | Human review checklist | human-review-needed.md |

See `references/extraction-workflow.md` for detailed workflow.

## Hard Rules

1. Every extracted value must include `source`, `confidence`, `confidenceLabel`, and `strictness`.
2. `reference-visible` must include bbox or reference bbox within the same component detail; visibility claims without bbox are invalid.
3. Phase 1 must output `uiType`, one of: `application-dashboard`, `panorama-scene`, `image-led-landing`, `mobile-app`, `poster-like-ui`, `unknown`.
4. If `uiType` is `panorama-scene` or `image-led-landing`, phases 5/6 must use the image layer + overlay layer layout model.
5. Components not present in the screenshot must be listed in Rejected Assumptions, not placed in the component tree.
6. Values with confidence < 0.6 must appear in `human-review-needed.md`; low-confidence layout type must go into human review even if confidence >= 0.6.
7. Every color in the component tree must exist in tokens.json.
8. Every component dimension must match layout-spec.md.
9. Sum of sibling component widths must not exceed parent container width; overlay components must verify bbox does not overflow.
10. Typography scale must decrease monotonically: h1 > h2 > h3 > body.
11. No orphan tokens (defined but unused).
12. No missing tokens (used in component tree but undefined).

## Capability Boundaries

See `references/script-backed-boundary.md` for detailed boundary definition.

| Category | Examples |
|----------|----------|
| LLM can do | Visual recognition, UI type determination, color estimation, layout judgment, component classification, proportion estimation |
| Script-assisted | Precise color values, WCAG contrast, delta-E, exact pixel measurement, bbox measurement, visual regression comparison |
| Human confirmation | Low-confidence colors, ambiguous component boundaries, uncertain font identification, whether the main visual needs real assets |

When scripts are unavailable, LLM does best-effort estimation and annotates confidence and notes.

## Supporting Files Index

### references/
- `extraction-workflow.md` — 9-phase detailed workflow, UI type branching, asset strategy rules
- `token-schema.md` — Token JSON schema definition and field descriptions
- `output-files.md` — Structure templates for each output file
- `source-strictness-rules.md` — Complete rules for source/confidence/strictness/bbox labels
- `script-backed-boundary.md` — Boundary definitions for LLM / script / human operations

### examples/
- `tokens.example.json` — Complete tokens.json example
- `component-tree.example.md` — Component tree example, including panorama-scene vs dashboard branching
- `layout-spec.example.md` — Layout spec example, including overlay coordinate model
- `visual-analysis.example.md` — Visual analysis example, including UI type, visible elements, rejected assumptions
- `human-review-needed.example.md` — Human review checklist example
