# UI Type and Asset Validation

## UI Type Preservation

Read:

```text
ui/03_visual_spec/visual-analysis.md
```

If UI type is:

- panorama-scene
- scene-led-interface
- image-led-interface
- photorealistic-interface

then actual rendering must preserve scene-first structure.

## Forbidden Drift

Fail if actual rendering introduces:

- Sidebar
- RightPanel
- DataGrid
- MapVisualization
- DashboardCard
- ChartPanel
- AdminNav
- SaaS StatusBar
- fixed three-column grid shell

unless explicitly reference-visible and human-approved.

## Layout Paradigm Preservation

Read:

```text
ui/03_visual_spec/layout-spec.md
```

Fail if actual layout uses a different paradigm.

## Asset Strategy Preservation

Read:

```text
ui/03_visual_spec/implementation-risks.md
```

For photorealistic / panorama / scene-led UI:

Fail if:

- main scene image missing
- approved raster asset missing
- scene redrawn with CSS/SVG/chart/map
- gradient replaces scene
- scene objects become DOM components
- overlay and scene are not separable

## Overlay Validation

For scene-led UI:

- scene layer should remain primary
- overlay controls should sit above scene
- hotspots should align with visual anchors
- thumbnails / view controls should remain accessible
