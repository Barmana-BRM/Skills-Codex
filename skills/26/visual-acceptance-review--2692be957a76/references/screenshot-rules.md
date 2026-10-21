# Screenshot Rules

## Required Viewports

| Viewport   | Width | Height | Filename              |
| ---------- | ----: | -----: | --------------------- |
| desktop-hd |  1920 |   1080 | actual-desktop-hd.png |
| desktop    |  1440 |    900 | actual-desktop.png    |
| tablet     |   768 |   1024 | actual-tablet.png     |
| mobile     |   375 |    812 | actual-mobile.png     |

## Screenshot Storage

Store under:

```text
07_validation/visual_acceptance/screenshots/
```

## Browser Health

Capture:

```text
console-errors.log
network-errors.log
```

## Desktop Comparison

Compare desktop actual screenshot against `reference.png`.

## Tablet / Mobile Comparison

Do not pixel-match tablet/mobile against desktop reference.

Compare tablet/mobile against:

```text
ui/05_design_system/responsive-spec.md
```

## If Screenshot Script Exists

Use project script.

Examples:

```text
pnpm screenshot
pnpm test:visual
pnpm verify:ui
```

Do not invent script names if they do not exist.

## If Script-backed Pixel Diff Exists

Use it and mark findings:

```text
source: script-backed
detectedBy: script-backed
```

If no script-backed diff exists, use qualitative visual review and mark estimated confidence.
