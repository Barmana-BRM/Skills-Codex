export const FORMATS = Object.freeze({
  portrait: Object.freeze({ width: 1080, height: 1920, label: '1080 × 1920' }),
  portrait34: Object.freeze({ width: 1080, height: 1440, label: '1080 × 1440' }),
  square: Object.freeze({ width: 1080, height: 1080, label: '1080 × 1080' }),
  landscape: Object.freeze({ width: 1920, height: 1080, label: '1920 × 1080' }),
});

export const DEFAULT_FORMAT_LAYOUTS = Object.freeze({
  portrait: Object.freeze({
    map: Object.freeze({ x: 5, y: 7, w: 90 }),
    data: Object.freeze({ x: 6.5, y: 63, w: 87 }),
  }),
  portrait34: Object.freeze({
    map: Object.freeze({ x: 6, y: 5, w: 88 }),
    data: Object.freeze({ x: 7, y: 67, w: 86 }),
  }),
  square: Object.freeze({
    map: Object.freeze({ x: 8, y: 4, w: 84 }),
    data: Object.freeze({ x: 8, y: 66, w: 84 }),
  }),
  landscape: Object.freeze({
    map: Object.freeze({ x: 46, y: 3, w: 50 }),
    data: Object.freeze({ x: 4, y: 62, w: 48 }),
  }),
});

export const VIDEO_FRAME_RATE = 30;
export const VIDEO_BITRATE = 12_000_000;
export const VIDEO_BITRATE_LABEL = `${VIDEO_BITRATE / 1_000_000} Mbps`;
export const VIDEO_CODEC_LABEL = 'H.264';

export function createFormatLayouts() {
  return Object.fromEntries(Object.entries(DEFAULT_FORMAT_LAYOUTS).map(([format, layouts]) => [
    format,
    {
      map: { ...layouts.map },
      data: { ...layouts.data },
    },
  ]));
}

export function exportOutputHint(formatKey) {
  const format = FORMATS[formatKey];
  if (!format) throw new Error(`Unknown export format: ${formatKey}`);
  return `当前输出：${format.label} PNG / MP4（${VIDEO_CODEC_LABEL} · ${VIDEO_BITRATE_LABEL} · ${VIDEO_FRAME_RATE} FPS · 路线原生分辨率）`;
}

export function idleRenderStatus() {
  return `MP4 以 ${VIDEO_BITRATE_LABEL}、固定 ${VIDEO_FRAME_RATE} FPS 逐帧渲染；路线按最终画面尺寸生成，导出前会询问保存位置。`;
}

export function completedExportSummary({ kind, formatKey, destinationLabel, durationSeconds }) {
  const format = FORMATS[formatKey];
  if (!format) throw new Error(`Unknown export format: ${formatKey}`);
  if (kind === 'PNG') return `最近导出：PNG · ${format.label} · ${destinationLabel}`;
  if (kind === 'MP4' && Number.isFinite(durationSeconds)) {
    return `最近导出：MP4 · ${format.label} · ${VIDEO_CODEC_LABEL} · ${VIDEO_BITRATE_LABEL} · ${VIDEO_FRAME_RATE} FPS · ${durationSeconds.toFixed(1)} 秒 · ${destinationLabel}`;
  }
  throw new Error(`Unsupported export summary: ${kind}`);
}

export function routeLayerBox(formatKey, layout) {
  const format = FORMATS[formatKey];
  if (!format) throw new Error(`Unknown export format: ${formatKey}`);
  const width = layout.w / 100;
  return {
    x: layout.x / 100,
    y: layout.y / 100,
    width,
    height: (format.width * width / 1.5) / format.height,
  };
}

export function findOutsideLayer(layers, tolerance = 0.002) {
  return layers.find((layer) => (
    layer.x < -tolerance
    || layer.y < -tolerance
    || layer.x + layer.width > 1 + tolerance
    || layer.y + layer.height > 1 + tolerance
  )) || null;
}

export function hasMp4Signature(buffer) {
  const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer || 0);
  return bytes.length >= 12
    && bytes[4] === 0x66
    && bytes[5] === 0x74
    && bytes[6] === 0x79
    && bytes[7] === 0x70;
}
