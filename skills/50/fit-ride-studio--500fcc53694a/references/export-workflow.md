# Ride Relief export workflow

## Entry conditions

Open the composer only after the user requests a shareable image, animation, demonstration, or video. Analysis alone does not authorize an export.

For a batch, resolve one FIT or KML activity for the visual story. Good candidates are latest, longest, or highest-ascent, but the user's explicit choice wins.

## Browser sequence

1. Verify `http://127.0.0.1:5174/` is reachable. Start `npm run dev` from the Ride Relief root only when needed.
2. Reuse the staged report URL returned by `scripts/prepare-report.mjs`. If no staged URL exists, prepare the chosen track and analysis JSON first.
3. Open the URL with any available browser capability. It auto-loads the track; do not depend on automating the file input. If browser tools are unavailable on the same machine, give the URL to the user. If the Agent is remote and the user cannot reach its loopback address, stop the UI workflow and deliver the text/JSON result instead.
4. Open **导出创作**.
5. Add route photos in **导出创作** when provided. Let GPS/time matching place them automatically, or bind them on the 2D route when the user specifies positions; select one cover image.
6. Enable **沿途照片故事** when multiple bound photos should transition along route progress. Use 2.5 seconds per photo by default (the user may choose 2 or 3 seconds), order photos cyclically from the chosen cover along the route, and verify that each transition coincides with a highlighted route marker. Otherwise load one user photo or video as the background, or keep a built-in background and disclose that choice.
7. Set aspect ratio, map/card sizes, card style, layer visibility, and watermark.
8. When visual/screenshot capability exists, inspect the preview. The overlay bounding boxes must remain inside the stage for the selected ratio; sensor-dependent rows must not clip the card; route-photo transitions must start from the selected cover. Without visual capability, tell the user what to inspect and wait for confirmation before an expensive render. Treat each ratio as its own composition rather than cropping one layout into every format.
9. Export PNG for a still or H.264 MP4 for motion. Keep the output canvas at the selected 1080-class dimensions, render the 3D route at its final overlay pixel size instead of scaling the preview canvas, and use 12 Mbps / 30 FPS for MP4.
10. Before rendering starts, warn that Chromium may open a native save picker that the user must operate personally; browser automation usually cannot control it. If the picker API is unavailable, explain that the file will use the browser downloads folder.
11. After the save target is confirmed, show a modal export task with the current phase, percentage, progress bar, and frame count when applicable. Block composer interaction while it is open. Let the user cancel during preparation and frame encoding; cancellation must stop work, release encoder/render resources, and never report success. Disable cancellation only while the finished file is being finalized or written, to avoid a partial output.
12. Let the user choose the final location in the browser/system save picker. If the picker API is unavailable, confirm the browser downloads fallback.

## Defaults

- Ratio: 9:16 for social sharing.
- Motion: 10-second map rotation with the route point looping continuously for one background. For multiple route photos, total duration = photo count × per-photo seconds and the map completes one rotation across the full story.
- Data card: whole-activity totals, not time-synchronized live values. Geometry-only KML shows only reliable spatial/elevation fields.
- Watermark: track basename, enabled.
- Output: MP4 (H.264, 12 Mbps, 30 FPS) for “演示/动画/视频”; PNG for “图片/封面/静帧”. Render the route layer at its final composition dimensions so the map stays sharp in the exported file.
- Background: bound route-photo story first when requested, otherwise user media, then a built-in abstract image.

## Export quality gate

- Preview first; perform the expensive MP4 render only after the user asks for the video deliverable.
- With visual capability, measure the route and data-card bounds against the selected final canvas before encoding. Stop with a specific correction message if either layer crosses an edge. Otherwise require user preview confirmation.
- With visual capability, check representative states: opening frame, midpoint, final frame, and every photo transition. At a transition, only the active photo marker should appear on the route.
- Keep resolution, codec, bitrate, frame rate, and route-layer render size in one implementation source of truth; keep the visible export hint synchronized with it.
- After changing export formats, layout defaults, or encoding settings in the Ride Relief app, run `npm run test:export` before browser verification.
- When the saved file is available for inspection, verify dimensions, H.264 codec, 30 FPS, duration, and the first/final frame before reporting completion.

## Privacy and completion

- Before public sharing, flag closed routes or nearby start/end points and offer to hide the first/last 300–500 m.
- A request to export authorizes rendering the chosen deliverable, but not arbitrary changes to unrelated files.
- Do not report success while rendering is still in progress. Confirm the save picker result or browser download fallback.
- Treat a user-cancelled render as a normal outcome: close the progress modal, restore composer interaction, and report that no file was exported rather than showing an encoding error.
