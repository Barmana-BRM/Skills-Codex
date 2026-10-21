#!/usr/bin/env node

import assert from 'node:assert/strict';
import {
  DEFAULT_FORMAT_LAYOUTS,
  FORMATS,
  VIDEO_BITRATE,
  VIDEO_FRAME_RATE,
  completedExportSummary,
  createFormatLayouts,
  exportOutputHint,
  findOutsideLayer,
  hasMp4Signature,
  routeLayerBox,
} from '../src/export-config.js';

const formatKeys = Object.keys(FORMATS);
assert.deepEqual(formatKeys, ['portrait', 'portrait34', 'square', 'landscape']);

for (const formatKey of formatKeys) {
  const format = FORMATS[formatKey];
  assert.equal(Math.min(format.width, format.height), 1080, `${formatKey} must be 1080-class`);
  assert.match(exportOutputHint(formatKey), /12 Mbps.*30 FPS.*路线原生分辨率/);

  const mapBox = routeLayerBox(formatKey, DEFAULT_FORMAT_LAYOUTS[formatKey].map);
  assert.equal(findOutsideLayer([{ name: 'map', ...mapBox }]), null, `${formatKey} map must fit`);

  const dataLayout = DEFAULT_FORMAT_LAYOUTS[formatKey].data;
  assert.ok(dataLayout.x >= 0 && dataLayout.x + dataLayout.w <= 100, `${formatKey} data width must fit`);
  assert.ok(dataLayout.y >= 0 && dataLayout.y < 100, `${formatKey} data top must fit`);
}

assert.equal(VIDEO_FRAME_RATE, 30);
assert.equal(VIDEO_BITRATE, 12_000_000);
assert.match(completedExportSummary({
  kind: 'MP4',
  formatKey: 'portrait',
  durationSeconds: 10,
  destinationLabel: '你选择的位置',
}), /MP4 · 1080 × 1920 · H\.264 · 12 Mbps · 30 FPS · 10\.0 秒 · 你选择的位置/);
assert.equal(new Set(Object.values(DEFAULT_FORMAT_LAYOUTS).map((layout) => JSON.stringify(layout))).size, 4);

const mutableLayouts = createFormatLayouts();
mutableLayouts.portrait.map.w = 42;
assert.equal(DEFAULT_FORMAT_LAYOUTS.portrait.map.w, 90, 'runtime layout edits must not mutate defaults');

assert.equal(findOutsideLayer([{ name: 'bad', x: 0.8, y: 0.1, width: 0.3, height: 0.2 }])?.name, 'bad');
assert.equal(hasMp4Signature(Uint8Array.from([0, 0, 0, 24, 0x66, 0x74, 0x79, 0x70, 0, 0, 0, 0])), true);
assert.equal(hasMp4Signature(Uint8Array.from([0, 0, 0, 0])), false);

console.log(`Export config check passed: ${formatKeys.length} formats · 1080-class · H.264 ${VIDEO_BITRATE / 1_000_000} Mbps · ${VIDEO_FRAME_RATE} FPS`);
