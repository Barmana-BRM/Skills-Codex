import { analyzeActivity, formatClock, formatPace, sportMeta } from './data.js';
import { RouteScene } from './route-scene.js';
import h264EncoderUrl from 'h264-mp4-encoder/embuild/dist/h264-mp4-encoder.web.js?url';
import { toCanvas as renderDomToCanvas } from 'html-to-image';
import {
  FORMATS,
  VIDEO_BITRATE,
  VIDEO_FRAME_RATE,
  completedExportSummary,
  createFormatLayouts,
  exportOutputHint,
  findOutsideLayer,
  hasMp4Signature,
  idleRenderStatus,
  routeLayerBox,
} from './export-config.js';

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
const number = (value, fallback = 0) => value != null && value !== '' && Number.isFinite(Number(value)) ? Number(value) : fallback;

function setIcon(element, icon) {
  if (!element) return;
  element.className = [...element.classList].filter((name) => !name.startsWith('ph-')).join(' ');
  element.classList.add('ph', icon);
}

let wasmH264Loader;

function loadWasmH264Encoder() {
  if (window.HME?.createH264MP4Encoder) return Promise.resolve(window.HME);
  if (wasmH264Loader) return wasmH264Loader;
  wasmH264Loader = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = h264EncoderUrl;
    script.async = true;
    script.addEventListener('load', () => {
      if (window.HME?.createH264MP4Encoder) resolve(window.HME);
      else reject(new Error('WASM H.264 encoder loaded without a browser API.'));
    }, { once: true });
    script.addEventListener('error', () => reject(new Error('WASM H.264 encoder failed to load.')), { once: true });
    document.head.append(script);
  });
  return wasmH264Loader;
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
}

async function requestSaveTarget(filename, description, mimeType, extension) {
  if (!window.isSecureContext || typeof window.showSaveFilePicker !== 'function') {
    return { mode: 'download' };
  }
  try {
    const handle = await window.showSaveFilePicker({
      suggestedName: filename,
      types: [{
        description,
        accept: { [mimeType]: [extension] },
      }],
    });
    return { mode: 'picker', handle };
  } catch (error) {
    if (error?.name === 'AbortError') return { mode: 'cancelled' };
    console.warn('系统保存窗口不可用，改用浏览器下载目录。', error);
    return { mode: 'download' };
  }
}

async function saveBlob(blob, filename, target) {
  if (target.mode === 'picker') {
    const writable = await target.handle.createWritable();
    await writable.write(blob);
    await writable.close();
    return 'chosen-location';
  }
  downloadBlob(blob, filename);
  return 'downloads-folder';
}

export class ExportComposer {
  constructor(root, notify) {
    this.root = root;
    this.notify = notify;
    this.stage = root.querySelector('#export-stage');
    this.backgroundImage = root.querySelector('#export-background-image');
    this.backgroundTransitionImage = root.querySelector('#export-background-transition-image');
    this.backgroundVideo = root.querySelector('#export-background-video');
    this.mapOverlay = root.querySelector('#export-map-overlay');
    this.dataOverlay = root.querySelector('#export-data-overlay');
    this.location = root.querySelector('#export-location');
    this.watermark = root.querySelector('#export-watermark');
    this.watermarkText = this.watermark.querySelector('span');
    this.backgroundCreditText = root.querySelector('#background-credit-text');
    this.backgroundCreditLink = root.querySelector('#background-credit-link');
    this.renderStatus = root.querySelector('#render-status');
    this.imageExportButton = root.querySelector('#export-image-button');
    this.videoExportButton = root.querySelector('#export-video-button');
    this.progressModal = document.querySelector('#export-progress-modal');
    this.progressDialog = this.progressModal.querySelector('.export-progress-dialog');
    this.progressKicker = document.querySelector('#export-progress-kicker');
    this.progressTitle = document.querySelector('#export-progress-title');
    this.progressPercent = document.querySelector('#export-progress-percent');
    this.progressTrack = document.querySelector('#export-progress-track');
    this.progressBar = document.querySelector('#export-progress-bar');
    this.progressDetail = document.querySelector('#export-progress-detail');
    this.cancelExportButton = document.querySelector('#export-cancel-button');
    this.routePhotoToggle = root.querySelector('#route-photo-toggle');
    this.routePhotoSummary = root.querySelector('#route-photo-summary');
    this.photoDurationControl = root.querySelector('#photo-duration-control');
    this.photoSecondsInput = root.querySelector('#photo-seconds-input');
    this.photoDurationTotal = root.querySelector('#photo-duration-total');
    this.format = 'portrait';
    this.backgroundType = 'image';
    this.rotationDuration = 10;
    this.photoSeconds = 2.5;
    this.previewDuration = this.rotationDuration;
    this.progress = 0;
    this.presentationProgress = 0;
    this.previewActive = false;
    this.previewFrame = null;
    this.previewStartTime = 0;
    this.presentationStartTime = 0;
    this.rendering = false;
    this.exportCancelRequested = false;
    this.exportCancelable = false;
    this.exportProgressValue = 0;
    this.exportPreviousFocus = null;
    this.appWasInert = false;
    this.appPreviousAriaHidden = null;
    this.lastExportSummary = '';
    this.renderLayers = null;
    this.customMediaUrl = null;
    this.routePhotos = [];
    this.coverPhoto = null;
    this.cardStyle = 'glass';
    this.formatLayouts = createFormatLayouts();
    this.layouts = this.formatLayouts[this.format];

    this.routeScene = new RouteScene(
      root.querySelector('#export-route-canvas'),
      null,
      {
        transparent: true,
        showGround: false,
        routeRadius: 0.95,
        routeGlowRadius: 2.1,
        photoMarkersOnlyOnCue: true,
      },
    );
    this.routeScene.playing = false;
    this.routeScene.spinning = false;
    this.routeScene.controls.enabled = false;
    this.routeScene.camera.position.set(8, 116, 250);
    this.routeScene.controls.target.set(0, 8, 0);
    this.routeScene.controls.update();

    this.bindControls();
    this.bindOverlay(this.mapOverlay, 'map', 28, 92);
    this.bindOverlay(this.dataOverlay, 'data', 32, 88);
    this.applyLayout('map');
    this.applyLayout('data');
    this.root.querySelector('#export-output-hint').textContent = exportOutputHint(this.format);
    this.renderStatus.textContent = idleRenderStatus();
  }

  bindControls() {
    this.root.querySelector('#background-media-input').addEventListener('change', (event) => {
      this.useUploadedMedia(event.target.files?.[0]);
      event.target.value = '';
    });

    this.routePhotoToggle.addEventListener('change', (event) => {
      if (event.target.checked) this.useRoutePhotoStory();
      else this.usePreset(this.root.querySelector('.background-preset'));
    });

    this.photoSecondsInput.addEventListener('change', (event) => {
      this.photoSeconds = clamp(Number(event.target.value) || 2.5, 2, 3);
      if (this.backgroundType === 'photo-story') {
        this.applyPhotoStoryDuration();
        this.updateAnimationFrame(0);
        if (!this.root.hidden) {
          this.pause();
          this.startPreview();
        }
      } else {
        this.updatePhotoDurationControl();
      }
    });

    for (const button of this.root.querySelectorAll('.background-preset')) {
      button.addEventListener('click', () => this.usePreset(button));
    }

    for (const button of this.root.querySelectorAll('.format-switcher button')) {
      button.addEventListener('click', () => this.setFormat(button.dataset.format));
    }

    for (const button of this.root.querySelectorAll('.card-style-options button')) {
      button.addEventListener('click', () => this.setCardStyle(button.dataset.cardStyle));
    }

    this.root.querySelector('#map-layer-toggle').addEventListener('change', (event) => {
      this.mapOverlay.hidden = !event.target.checked;
    });
    this.root.querySelector('#data-layer-toggle').addEventListener('change', (event) => {
      this.dataOverlay.hidden = !event.target.checked;
    });
    this.root.querySelector('#watermark-toggle').addEventListener('change', (event) => {
      this.watermark.hidden = !event.target.checked;
    });

    this.root.querySelector('#map-size-input').addEventListener('input', (event) => {
      this.layouts.map.w = Number(event.target.value);
      this.layouts.map.x = clamp(this.layouts.map.x, 0, 100 - this.layouts.map.w);
      this.applyLayout('map');
    });
    this.root.querySelector('#data-size-input').addEventListener('input', (event) => {
      this.layouts.data.w = Number(event.target.value);
      this.layouts.data.x = clamp(this.layouts.data.x, 0, 100 - this.layouts.data.w);
      this.applyLayout('data');
    });

    this.root.querySelector('#watermark-input').addEventListener('input', (event) => {
      this.watermarkText.textContent = event.target.value.trim() || 'RIDE RELIEF';
    });

    this.stage.addEventListener('pointerdown', (event) => {
      if (!event.target.closest('.composer-overlay')) this.selectOverlay(null);
    });

    this.imageExportButton.addEventListener('click', () => this.exportImage());
    this.videoExportButton.addEventListener('click', () => this.exportVideo());
    this.cancelExportButton.addEventListener('click', () => this.requestExportCancel());
    document.addEventListener('keydown', (event) => {
      if (this.progressModal.hidden) return;
      if (event.key === 'Escape') {
        event.preventDefault();
        this.requestExportCancel();
      } else if (event.key === 'Tab') {
        event.preventDefault();
        (this.cancelExportButton.disabled ? this.progressDialog : this.cancelExportButton).focus();
      }
    });
    document.addEventListener('focusin', (event) => {
      if (this.progressModal.hidden || this.progressModal.contains(event.target)) return;
      (this.cancelExportButton.disabled ? this.progressDialog : this.cancelExportButton).focus();
    });
  }

  bindOverlay(overlay, key, minWidth, maxWidth) {
    const handle = overlay.querySelector('.overlay-resize-handle');
    overlay.addEventListener('pointerdown', (event) => {
      if (event.target.closest('.overlay-resize-handle')) return;
      if (event.button !== 0) return;
      event.preventDefault();
      this.selectOverlay(overlay);
      const stageRect = this.stage.getBoundingClientRect();
      const start = {
        pointerX: event.clientX,
        pointerY: event.clientY,
        layoutX: this.layouts[key].x,
        layoutY: this.layouts[key].y,
      };
      let dragging = false;
      overlay.setPointerCapture(event.pointerId);
      const move = (moveEvent) => {
        const deltaX = moveEvent.clientX - start.pointerX;
        const deltaY = moveEvent.clientY - start.pointerY;
        if (!dragging && Math.hypot(deltaX, deltaY) < 6) return;
        if (!dragging) {
          dragging = true;
          overlay.classList.add('is-dragging');
        }
        const width = overlay.getBoundingClientRect().width / stageRect.width * 100;
        const height = overlay.getBoundingClientRect().height / stageRect.height * 100;
        this.layouts[key].x = clamp(start.layoutX + deltaX / stageRect.width * 100, 0, 100 - width);
        this.layouts[key].y = clamp(start.layoutY + deltaY / stageRect.height * 100, 0, 100 - height);
        this.applyLayout(key);
      };
      const end = () => {
        overlay.classList.remove('is-dragging');
        if (overlay.hasPointerCapture(event.pointerId)) overlay.releasePointerCapture(event.pointerId);
        overlay.removeEventListener('pointermove', move);
        overlay.removeEventListener('pointerup', end);
        overlay.removeEventListener('pointercancel', end);
      };
      overlay.addEventListener('pointermove', move);
      overlay.addEventListener('pointerup', end);
      overlay.addEventListener('pointercancel', end);
    });

    handle.addEventListener('pointerdown', (event) => {
      if (event.button !== 0) return;
      event.preventDefault();
      event.stopPropagation();
      this.selectOverlay(overlay);
      const stageRect = this.stage.getBoundingClientRect();
      const startX = event.clientX;
      const startWidth = this.layouts[key].w;
      let resizing = false;
      handle.setPointerCapture(event.pointerId);
      const move = (moveEvent) => {
        const deltaX = moveEvent.clientX - startX;
        if (!resizing && Math.abs(deltaX) < 5) return;
        resizing = true;
        const nextWidth = clamp(startWidth + deltaX / stageRect.width * 100, minWidth, maxWidth);
        this.layouts[key].w = nextWidth;
        this.layouts[key].x = clamp(this.layouts[key].x, 0, 100 - nextWidth);
        this.applyLayout(key);
        this.root.querySelector(`#${key === 'map' ? 'map' : 'data'}-size-input`).value = Math.round(nextWidth);
      };
      const end = () => {
        if (handle.hasPointerCapture(event.pointerId)) handle.releasePointerCapture(event.pointerId);
        handle.removeEventListener('pointermove', move);
        handle.removeEventListener('pointerup', end);
        handle.removeEventListener('pointercancel', end);
      };
      handle.addEventListener('pointermove', move);
      handle.addEventListener('pointerup', end);
      handle.addEventListener('pointercancel', end);
    });
  }

  selectOverlay(overlay) {
    this.root.querySelectorAll('.composer-overlay').forEach((item) => item.classList.toggle('is-selected', item === overlay));
  }

  applyLayout(key, constrain = true) {
    const overlay = key === 'map' ? this.mapOverlay : this.dataOverlay;
    const layout = this.layouts[key];
    overlay.style.left = `${layout.x}%`;
    overlay.style.top = `${layout.y}%`;
    overlay.style.width = `${layout.w}%`;
    if (key === 'map') requestAnimationFrame(() => this.routeScene.resize());
    if (!constrain) return;
    requestAnimationFrame(() => {
      const stageWidth = this.stage.clientWidth;
      const stageHeight = this.stage.clientHeight;
      if (!stageWidth || !stageHeight) return;
      const outerWidth = overlay.offsetWidth / stageWidth * 100;
      const outerHeight = overlay.offsetHeight / stageHeight * 100;
      const nextX = clamp(layout.x, 0, Math.max(0, 100 - outerWidth));
      const nextY = clamp(layout.y, 0, Math.max(0, 100 - outerHeight));
      if (nextX !== layout.x) {
        layout.x = nextX;
        overlay.style.left = `${nextX}%`;
      }
      if (nextY !== layout.y) {
        layout.y = nextY;
        overlay.style.top = `${nextY}%`;
      }
    });
  }

  setActivity(payload) {
    this.activity = payload;
    this.analysis = analyzeActivity(payload);
    this.setLocation(null);
    this.routeScene.setRoute(payload);
    this.routeScene.playing = false;
    this.routeScene.spinning = false;
    this.routeScene.camera.position.set(8, 116, 250);
    this.routeScene.controls.target.set(0, 8, 0);
    this.routeScene.controls.update();
    this.routeScene.setPresentationProgress(0);

    const hasCadence = this.analysis.metrics.cadenceCoverage > 1;
    const hasHeartRate = this.analysis.metrics.hasHeartRate;
    const hasPower = this.analysis.metrics.hasPower;
    const hasCalories = number(payload.session.totalCalories) > 0;
    const hasTemperature = this.analysis.metrics.averageTemperature != null;
    const type = sportMeta(this.analysis.metrics.sport);
    const hasPaceOrSpeed = this.analysis.metrics.hasTimeData && this.analysis.metrics.averageSpeed != null;
    const cadenceRelevant = (type.key === 'cycling' || type.key === 'running') && hasCadence;
    this.root.querySelector('#export-speed-field').hidden = !hasPaceOrSpeed;
    this.root.querySelector('#speed-source-chip').hidden = !hasPaceOrSpeed;
    this.root.querySelector('#export-cadence-field').hidden = !cadenceRelevant;
    this.root.querySelector('#cadence-source-chip').hidden = !cadenceRelevant;
    this.root.querySelector('#heart-source-chip').hidden = !hasHeartRate;
    this.root.querySelector('#power-source-chip').hidden = !hasPower;
    this.root.querySelector('#calories-source-chip').hidden = !hasCalories;
    this.root.querySelector('#temperature-source-chip').hidden = !hasTemperature;
    this.root.querySelector('#export-heart-field').hidden = !hasHeartRate;
    this.root.querySelector('#export-power-field').hidden = !hasPower;
    this.root.querySelector('#export-calories-field').hidden = !hasCalories;
    this.root.querySelector('#export-temperature-field').hidden = !hasTemperature;

    const summaryIcon = this.root.querySelector('#export-summary-icon');
    setIcon(summaryIcon, type.icon);
    this.root.querySelector('#export-summary-title').textContent = `${type.english} SUMMARY`;
    this.root.querySelector('#export-speed-label').textContent = type.key === 'cycling' ? '平均速度' : '平均配速';
    this.root.querySelector('#speed-source-label').textContent = type.key === 'cycling' ? '平均速度' : '平均配速';
    setIcon(this.root.querySelector('#export-speed-icon'), type.key === 'cycling' ? 'ph-speedometer' : 'ph-timer');
    this.root.querySelector('#export-max-label').textContent = type.key === 'cycling' ? '最高速度' : '最高海拔';
    this.root.querySelector('#max-source-label').textContent = type.key === 'cycling' ? '最高速度' : '最高海拔';
    setIcon(this.root.querySelector('#export-max-icon'), type.key === 'cycling' ? 'ph-gauge' : 'ph-mountains');
    this.root.querySelector('#export-cadence-label').textContent = `平均${type.cadence}`;
    this.root.querySelector('#cadence-source-label').textContent = `平均${type.cadence}`;
    setIcon(this.root.querySelector('#export-cadence-icon'), type.icon);
    this.root.querySelector('#export-data-mode-copy').textContent = `卡片使用整段${type.zh}汇总`;
    this.root.querySelector('#export-data-summary-copy').textContent = this.analysis.metrics.hasTimeData
      ? `地图约 10 秒完成一圈旋转；卡片固定展示整段${type.zh}的可用汇总指标。`
      : `地图约 10 秒完成一圈旋转；原文件没有时间轴，卡片只展示距离、爬升、海拔等可靠指标。`;

    const sourceName = payload.source?.slice(0, 48) || 'RIDE_RELIEF.fit';
    this.root.querySelector('#watermark-input').value = sourceName;
    this.watermarkText.textContent = sourceName;
    this.renderSummary();
    this.updateAnimationFrame(0);
  }

  setLocation(location) {
    const label = location?.exportLabel || location?.name;
    this.location.hidden = !label;
    this.location.querySelector('span').textContent = label || '';
  }

  effectiveRotationDuration() {
    return this.backgroundType === 'photo-story' && this.routePhotos.length > 1
      ? this.previewDuration
      : this.rotationDuration;
  }

  updatePhotoDurationControl() {
    const multiple = this.routePhotos.length > 1;
    this.photoDurationControl.hidden = !multiple;
    this.photoSecondsInput.value = String(this.photoSeconds);
    const total = multiple ? this.routePhotos.length * this.photoSeconds : this.rotationDuration;
    this.photoDurationTotal.textContent = multiple
      ? `${this.routePhotos.length} 张 · 总时长 ${total.toFixed(total % 1 ? 1 : 0)} 秒`
      : '单张照片沿用地图演示时长';
  }

  applyPhotoStoryDuration() {
    this.previewDuration = this.routePhotos.length > 1
      ? this.routePhotos.length * this.photoSeconds
      : this.rotationDuration;
    this.updatePhotoDurationControl();
    this.updateDurationLabels();
  }

  setPhotos(photos, { activate = false } = {}) {
    this.routePhotos = [...photos];
    this.coverPhoto = this.routePhotos.find((photo) => photo.isCover) ?? this.routePhotos[0] ?? null;
    this.routeScene.clearPhotos();
    this.routePhotos.forEach((photo) => this.routeScene.addPhoto(photo));
    this.routePhotoToggle.disabled = !this.routePhotos.length;
    this.routePhotoSummary.textContent = this.routePhotos.length
      ? `${this.routePhotos.length} 张 · 封面：${this.coverPhoto.label}`
      : '添加沿途照片后可启用';

    if (!this.routePhotos.length) {
      this.routePhotoToggle.checked = false;
      this.updatePhotoDurationControl();
      if (this.backgroundType === 'photo-story') this.usePreset(this.root.querySelector('.background-preset'));
      return;
    }
    this.updatePhotoDurationControl();
    if (activate || this.backgroundType === 'photo-story') this.useRoutePhotoStory({ notify: false });
  }

  useRoutePhotoStory({ notify = true } = {}) {
    if (!this.routePhotos.length || !this.coverPhoto) {
      this.routePhotoToggle.checked = false;
      this.notify?.('请先在导出创作中添加沿途照片', 'error');
      return;
    }
    const resumePreview = !this.root.hidden;
    this.pause();
    this.releaseCustomMedia();
    this.backgroundType = 'photo-story';
    this.backgroundVideo.pause();
    this.backgroundVideo.hidden = true;
    this.backgroundImage.hidden = false;
    this.backgroundTransitionImage.hidden = true;
    this.backgroundTransitionImage.style.opacity = '0';
    this.routePhotoToggle.checked = true;
    this.root.querySelectorAll('.background-preset').forEach((preset) => {
      preset.classList.remove('is-active');
      preset.setAttribute('aria-pressed', 'false');
    });
    this.applyPhotoStoryDuration();
    this.setBackgroundCredit(`沿途照片：${this.routePhotos.length} 张 · 封面 ${this.coverPhoto.label}`);
    this.updatePhotoStoryPreview(0);
    this.updateAnimationFrame(0);
    if (resumePreview) this.startPreview();
    if (notify) this.notify?.('已启用沿途照片转场', 'success');
  }

  photoStoryFrameAt(progress) {
    const story = this.orderedRoutePhotos();
    if (!story.length) return null;
    if (story.length === 1) return { from: story[0], to: null, blend: 0, cue: null, cueStrength: 0 };
    const timeline = clamp(progress, 0, 0.999999) * story.length;
    const segment = Math.floor(timeline);
    const local = timeline - segment;
    const from = story[segment];
    const to = story[(segment + 1) % story.length];
    const transitionFraction = clamp(0.55 / this.photoSeconds, 0.16, 0.3);
    const transitionStart = 1 - transitionFraction;
    if (local < transitionStart) return { from, to: null, blend: 0, cue: null, cueStrength: 0 };
    const amount = clamp((local - transitionStart) / transitionFraction, 0, 1);
    const blend = amount * amount * (3 - 2 * amount);
    return {
      from,
      to,
      blend,
      cue: to,
      cueStrength: Math.sin(Math.PI * amount),
    };
  }

  orderedRoutePhotos() {
    const cover = this.coverPhoto ?? this.routePhotos[0];
    if (!cover) return [];
    return [cover, ...this.routePhotos
      .filter((photo) => photo !== cover)
      .sort((left, right) => {
        const leftOffset = (left.progress - cover.progress + 1) % 1;
        const rightOffset = (right.progress - cover.progress + 1) % 1;
        return leftOffset - rightOffset;
      })];
  }

  routeProgressForPhotoStory(progress) {
    const story = this.orderedRoutePhotos();
    if (story.length < 2) return progress;
    const timeline = clamp(progress, 0, 0.999999) * story.length;
    const segment = Math.floor(timeline);
    const local = timeline - segment;
    const start = story[segment].progress;
    let end = story[(segment + 1) % story.length].progress;
    while (end <= start) end += 1;
    const eased = local * local * (3 - 2 * local);
    return (start + (end - start) * eased) % 1;
  }

  updatePhotoStoryPreview(progress) {
    if (this.backgroundType !== 'photo-story') return;
    const frame = this.photoStoryFrameAt(progress);
    if (!frame) return;
    if (this.backgroundImage.getAttribute('src') !== frame.from.url) this.backgroundImage.src = frame.from.url;
    this.backgroundImage.alt = frame.from.label;
    this.backgroundImage.style.transform = `scale(${(1.015 + progress * 0.012).toFixed(4)})`;
    if (frame.to) {
      if (this.backgroundTransitionImage.getAttribute('src') !== frame.to.url) this.backgroundTransitionImage.src = frame.to.url;
      this.backgroundTransitionImage.alt = frame.to.label;
      this.backgroundTransitionImage.hidden = false;
      this.backgroundTransitionImage.style.opacity = String(frame.blend);
      this.backgroundTransitionImage.style.transform = `scale(${(1.035 - frame.blend * 0.02).toFixed(4)})`;
    } else {
      this.backgroundTransitionImage.hidden = true;
      this.backgroundTransitionImage.style.opacity = '0';
    }
    this.routeScene.setPhotoCue(frame.cue, frame.cueStrength);
  }

  show() {
    requestAnimationFrame(() => {
      this.routeScene.resize();
      this.updateAnimationFrame(this.progress);
      this.startPreview();
    });
  }

  renderSummary() {
    if (!this.activity || !this.analysis) return;
    const last = this.activity.records.at(-1);
    const session = this.activity.session;
    const metrics = this.analysis.metrics;
    const totalDistance = number(session.totalDistance, number(last?.distance));
    const totalDuration = metrics.timerTime;
    const type = sportMeta(metrics.sport);

    const timeElement = this.root.querySelector('#export-live-time');
    timeElement.hidden = totalDuration == null;
    timeElement.textContent = totalDuration == null ? '' : formatClock(totalDuration);
    this.root.querySelector('#export-live-distance').textContent = (totalDistance / 1000).toFixed(2);
    this.root.querySelector('#export-live-speed').textContent = type.key === 'cycling'
      ? metrics.averageSpeed?.toFixed(1) ?? '—'
      : formatPace(metrics.averagePaceSeconds);
    this.root.querySelector('#export-speed-unit').textContent = type.key === 'cycling' ? 'km/h' : '/km';
    this.root.querySelector('#export-live-ascent').textContent = Math.round(number(session.totalAscent));
    this.root.querySelector('#export-live-max-speed').textContent = type.key === 'cycling'
      ? metrics.maxSpeed?.toFixed(1) ?? '—'
      : Math.round(metrics.maxAltitude ?? 0);
    this.root.querySelector('#export-max-unit').textContent = type.key === 'cycling' ? 'km/h' : 'm';
    this.root.querySelector('#export-live-calories').textContent = Math.round(number(session.totalCalories));
    this.root.querySelector('#export-live-temperature').textContent = metrics.averageTemperature == null
      ? '—'
      : Math.round(metrics.averageTemperature);
    this.root.querySelector('#export-live-cadence').textContent = metrics.effectiveCadence == null
      ? '—'
      : Math.round(metrics.effectiveCadence);
    this.root.querySelector('#export-cadence-unit').textContent = type.key === 'running' ? 'spm' : 'rpm';
    this.root.querySelector('#export-live-heart').textContent = metrics.averageHeartRate == null
      ? '—'
      : Math.round(metrics.averageHeartRate);
    this.root.querySelector('#export-live-power').textContent = metrics.averagePower == null
      ? '—'
      : Math.round(metrics.averagePower);
  }

  setFormat(format) {
    if (!FORMATS[format]) return;
    this.format = format;
    this.layouts = this.formatLayouts[format];
    this.stage.className = `export-stage format-${format}`;
    this.root.querySelectorAll('.format-switcher button').forEach((button) => {
      const active = button.dataset.format === format;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    this.root.querySelector('#map-size-input').value = Math.round(this.layouts.map.w);
    this.root.querySelector('#data-size-input').value = Math.round(this.layouts.data.w);
    this.applyLayout('map', false);
    this.applyLayout('data', false);
    this.selectOverlay(null);
    this.root.querySelector('#export-output-hint').textContent = exportOutputHint(format);
    setTimeout(() => {
      this.applyLayout('map');
      this.applyLayout('data');
      this.routeScene.resize();
    }, 260);
  }

  setCardStyle(style) {
    this.cardStyle = style;
    this.dataOverlay.classList.remove('style-glass', 'style-solid', 'style-minimal');
    this.dataOverlay.classList.add(`style-${style}`);
    this.root.querySelectorAll('.card-style-options button').forEach((button) => {
      const active = button.dataset.cardStyle === style;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', String(active));
    });
  }

  setBackgroundCredit(label, sourceUrl = '') {
    this.backgroundCreditText.textContent = label;
    this.backgroundCreditLink.hidden = !sourceUrl;
    if (sourceUrl) this.backgroundCreditLink.href = sourceUrl;
    else this.backgroundCreditLink.removeAttribute('href');
  }

  resetPhotoStoryLayer() {
    this.routePhotoToggle.checked = false;
    this.routeScene.setPhotoCue(null, 0);
    this.backgroundImage.style.transform = '';
    this.backgroundTransitionImage.hidden = true;
    this.backgroundTransitionImage.style.opacity = '0';
    this.backgroundTransitionImage.style.transform = '';
  }

  usePreset(button) {
    if (!button) return;
    const resumePreview = !this.root.hidden;
    this.pause();
    this.releaseCustomMedia();
    this.backgroundType = 'image';
    this.backgroundVideo.pause();
    this.backgroundVideo.hidden = true;
    this.backgroundImage.hidden = false;
    this.resetPhotoStoryLayer();
    this.backgroundImage.src = button.dataset.background;
    this.backgroundImage.alt = button.querySelector('img')?.alt || '选中的抽象背景';
    this.setBackgroundCredit(`背景：${button.dataset.credit} · Unsplash`, button.dataset.source);
    this.root.querySelectorAll('.background-preset').forEach((preset) => {
      const active = preset === button;
      preset.classList.toggle('is-active', active);
      preset.setAttribute('aria-pressed', String(active));
    });
    this.previewDuration = this.rotationDuration;
    this.updateDurationLabels();
    this.updateAnimationFrame(0);
    if (resumePreview) this.startPreview();
  }

  useUploadedMedia(file) {
    if (!file) return;
    const resumePreview = !this.root.hidden;
    this.pause();
    this.releaseCustomMedia();
    this.resetPhotoStoryLayer();
    this.customMediaUrl = URL.createObjectURL(file);
    this.root.querySelectorAll('.background-preset').forEach((preset) => {
      preset.classList.remove('is-active');
      preset.setAttribute('aria-pressed', 'false');
    });
    this.setBackgroundCredit(`本地素材：${file.name}`);

    if (file.type.startsWith('video/')) {
      this.backgroundType = 'video';
      this.backgroundImage.hidden = true;
      this.backgroundVideo.hidden = false;
      this.backgroundVideo.src = this.customMediaUrl;
      this.backgroundVideo.load();
      this.backgroundVideo.addEventListener('loadedmetadata', () => {
        this.previewDuration = Math.max(0.1, this.backgroundVideo.duration || 12);
        this.updateDurationLabels();
        this.updateAnimationFrame(0);
        if (resumePreview) this.startPreview();
      }, { once: true });
      this.notify?.('视频已载入，地图会按视频时长循环', 'success');
    } else if (file.type.startsWith('image/')) {
      this.backgroundType = 'image';
      this.backgroundVideo.pause();
      this.backgroundVideo.hidden = true;
      this.backgroundImage.hidden = false;
      this.backgroundImage.src = this.customMediaUrl;
      this.previewDuration = this.rotationDuration;
      this.updateDurationLabels();
      this.updateAnimationFrame(0);
      if (resumePreview) this.startPreview();
      this.notify?.('背景图片已载入', 'success');
    } else {
      this.releaseCustomMedia();
      this.notify?.('请选择图片或视频文件', 'error');
    }
  }

  releaseCustomMedia() {
    if (this.customMediaUrl) URL.revokeObjectURL(this.customMediaUrl);
    this.customMediaUrl = null;
  }

  updateDurationLabels() {
    const rotationDuration = this.effectiveRotationDuration();
    if (this.backgroundType === 'video') {
      this.root.querySelector('#export-sync-status').textContent = `地图约 ${rotationDuration} 秒一圈 · 路线点循环移动 · 视频 ${formatClock(this.previewDuration)}`;
    } else if (this.backgroundType === 'photo-story') {
      const perPhoto = this.routePhotos.length > 1 ? `每张约 ${this.photoSeconds} 秒` : `单张 ${this.previewDuration} 秒`;
      this.root.querySelector('#export-sync-status').textContent = `${this.routePhotos.length} 张沿途照片 · ${perPhoto} · 地图 ${rotationDuration} 秒一圈`;
    } else {
      this.root.querySelector('#export-sync-status').textContent = `地图约 ${rotationDuration} 秒一圈 · 路线点循环移动`;
    }
    if (this.activity && this.analysis) {
      const type = sportMeta(this.analysis.metrics.sport);
      this.root.querySelector('#export-data-summary-copy').textContent = this.backgroundType === 'photo-story' && this.routePhotos.length > 1
        ? `${this.routePhotos.length} 张照片按每张约 ${this.photoSeconds} 秒编排；地图在整段故事内转一圈，经过照片位置时标记会高亮。卡片固定展示整段${type.zh}汇总。`
        : `地图约 ${rotationDuration} 秒完成一圈旋转；卡片固定展示整段${type.zh}的可用汇总指标。`;
    }
  }

  recordAtTime(targetSeconds) {
    const records = this.activity.records;
    let low = 0;
    let high = records.length - 1;
    while (low < high) {
      const middle = Math.floor((low + high) / 2);
      if (number(records[middle].elapsedTime) < targetSeconds) low = middle + 1;
      else high = middle;
    }
    const previous = Math.max(0, low - 1);
    const index = Math.abs(number(records[previous].elapsedTime) - targetSeconds)
      <= Math.abs(number(records[low].elapsedTime) - targetSeconds)
      ? previous
      : low;
    return { record: records[index], index };
  }

  updateAnimationFrame(progress, presentationProgress = progress, renderTimestampSeconds = null) {
    if (!this.activity) return;
    this.progress = clamp(progress, 0, 1);
    this.presentationProgress = ((presentationProgress % 1) + 1) % 1;
    const fitDuration = number(
      this.activity.records.at(-1)?.elapsedTime,
      number(this.activity.session.totalTimerTime),
    );
    const routeTimelineProgress = this.backgroundType === 'photo-story'
      ? this.routeProgressForPhotoStory(this.progress)
      : this.progress;
    const fitTime = routeTimelineProgress * fitDuration;
    const recordIndex = fitDuration > 0
      ? this.recordAtTime(fitTime).index
      : Math.round(routeTimelineProgress * Math.max(0, this.activity.records.length - 1));
    const routeProgress = Math.min(recordIndex / Math.max(1, this.activity.records.length - 1), 0.999999);
    this.routeScene.setProgress(routeProgress);
    this.routeScene.setPresentationProgress(this.presentationProgress);
    this.updatePhotoStoryPreview(this.progress);
    if (Number.isFinite(renderTimestampSeconds)) {
      this.routeScene.renderFrame(renderTimestampSeconds * 1000);
    }
  }

  startPreview() {
    if (this.previewActive || !this.activity) return;
    this.previewActive = true;
    const duration = Math.max(0.1, this.previewDuration);
    this.previewStartTime = performance.now() - this.progress * duration * 1000;
    this.presentationStartTime = performance.now() - this.presentationProgress * this.effectiveRotationDuration() * 1000;
    if (this.backgroundType === 'video') {
      this.backgroundVideo.loop = true;
      if (Number.isFinite(this.backgroundVideo.duration)) {
        this.backgroundVideo.currentTime = this.progress * this.backgroundVideo.duration;
      }
      this.backgroundVideo.play().catch(() => {});
    }
    this.previewFrame = requestAnimationFrame((time) => this.previewTick(time));
  }

  previewTick(time) {
    if (!this.previewActive) return;
    const duration = Math.max(0.1, this.previewDuration);
    const elapsed = Math.max(0, (time - this.previewStartTime) / 1000);
    const presentationElapsed = Math.max(0, (time - this.presentationStartTime) / 1000);
    const rotationDuration = this.effectiveRotationDuration();
    this.updateAnimationFrame(
      (elapsed % duration) / duration,
      (presentationElapsed % rotationDuration) / rotationDuration,
    );
    this.previewFrame = requestAnimationFrame((nextTime) => this.previewTick(nextTime));
  }

  pause() {
    this.previewActive = false;
    if (this.previewFrame != null) cancelAnimationFrame(this.previewFrame);
    this.previewFrame = null;
    this.backgroundVideo.pause();
  }

  async ensureBackgroundReady() {
    if (this.backgroundType === 'photo-story') {
      await Promise.all(this.routePhotos.map(async (photo) => {
        if (!photo.image.complete && typeof photo.image.decode === 'function') await photo.image.decode();
      }));
      return;
    }
    if (this.backgroundType === 'image') {
      if (!this.backgroundImage.complete) await this.backgroundImage.decode();
      return;
    }
    if (this.backgroundVideo.readyState < 2) {
      await new Promise((resolve) => this.backgroundVideo.addEventListener('loadeddata', resolve, { once: true }));
    }
  }

  async seekBackgroundFrame(timestamp) {
    const video = this.backgroundVideo;
    const maxTime = Math.max(0, number(video.duration) - 0.001);
    const targetTime = clamp(timestamp, 0, maxTime);
    if (Math.abs(video.currentTime - targetTime) < 0.002 && video.readyState >= 2) return;
    await new Promise((resolve, reject) => {
      const timeout = window.setTimeout(() => {
        cleanup();
        reject(new Error('Timed out while seeking the background video.'));
      }, 2500);
      const cleanup = () => {
        window.clearTimeout(timeout);
        video.removeEventListener('seeked', onSeeked);
        video.removeEventListener('error', onError);
      };
      const onSeeked = () => {
        cleanup();
        resolve();
      };
      const onError = () => {
        cleanup();
        reject(video.error || new Error('Background video seek failed.'));
      };
      video.addEventListener('seeked', onSeeked, { once: true });
      video.addEventListener('error', onError, { once: true });
      video.currentTime = targetTime;
    });
    await new Promise((resolve) => requestAnimationFrame(resolve));
  }

  createRenderCanvas() {
    const format = FORMATS[this.format];
    const canvas = document.createElement('canvas');
    canvas.width = format.width;
    canvas.height = format.height;
    return canvas;
  }

  beginRouteRender() {
    if (this.mapOverlay.hidden) return;
    const format = FORMATS[this.format];
    const box = routeLayerBox(this.format, this.layouts.map);
    this.routeScene.beginExportRender(format.width * box.width, format.height * box.height);
  }

  endRouteRender() {
    this.routeScene.endExportRender();
  }

  validateRenderBounds() {
    const layers = [];
    if (!this.mapOverlay.hidden) {
      layers.push({ name: '路线', ...routeLayerBox(this.format, this.layouts.map) });
    }
    if (!this.dataOverlay.hidden && this.renderLayers?.data) {
      layers.push({ name: '数据卡片', ...this.renderLayers.data });
    }
    const outside = findOutsideLayer(layers);
    if (outside) throw new Error(`${outside.name}超出最终画布，请在预览中向内移动或缩小后重试。`);
  }

  async prepareRenderLayers() {
    const layers = {};
    if (this.dataOverlay.hidden) return layers;
    if (document.fonts?.ready) await document.fonts.ready;
    await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    const stageWidth = this.stage.clientWidth;
    const stageHeight = this.stage.clientHeight;
    const cardRect = this.dataOverlay.getBoundingClientRect();
    if (!stageWidth || !stageHeight || !cardRect.width || !cardRect.height) {
      throw new Error('The preview card does not have measurable dimensions.');
    }
    const format = FORMATS[this.format];
    const normalized = {
      x: this.dataOverlay.offsetLeft / stageWidth,
      y: this.dataOverlay.offsetTop / stageHeight,
      width: this.dataOverlay.offsetWidth / stageWidth,
      height: this.dataOverlay.offsetHeight / stageHeight,
    };
    const targetPixelWidth = normalized.width * format.width;
    const pixelRatio = clamp(targetPixelWidth / cardRect.width, 2, 4);
    const cardCanvas = await renderDomToCanvas(this.dataOverlay, {
      cacheBust: true,
      pixelRatio,
      filter: (node) => !node.classList?.contains('overlay-resize-handle'),
      style: {
        position: 'relative',
        inset: 'auto',
        left: '0',
        top: '0',
        width: `${cardRect.width}px`,
        height: `${cardRect.height}px`,
        boxSizing: 'border-box',
        margin: '0',
        outline: 'none',
        cursor: 'default',
        transform: 'none',
      },
    });
    layers.data = { canvas: cardCanvas, ...normalized };
    return layers;
  }

  drawCover(context, media, width, height, zoom = 1) {
    const sourceWidth = media.videoWidth || media.naturalWidth || width;
    const sourceHeight = media.videoHeight || media.naturalHeight || height;
    const scale = Math.max(width / sourceWidth, height / sourceHeight) * zoom;
    const drawWidth = sourceWidth * scale;
    const drawHeight = sourceHeight * scale;
    context.drawImage(media, (width - drawWidth) / 2, (height - drawHeight) / 2, drawWidth, drawHeight);
  }

  drawPhotoStory(context, width, height) {
    const frame = this.photoStoryFrameAt(this.progress);
    if (!frame) return;
    context.save();
    this.drawCover(context, frame.from.image, width, height, 1.015 + this.progress * 0.012);
    if (frame.to) {
      context.globalAlpha = frame.blend;
      this.drawCover(context, frame.to.image, width, height, 1.035 - frame.blend * 0.02);
    }
    context.restore();
  }

  drawComposition(context, width, height) {
    const media = this.backgroundType === 'video' ? this.backgroundVideo : this.backgroundImage;
    context.clearRect(0, 0, width, height);
    if (this.backgroundType === 'photo-story') this.drawPhotoStory(context, width, height);
    else this.drawCover(context, media, width, height);
    const shade = context.createLinearGradient(0, 0, 0, height);
    shade.addColorStop(0, 'rgba(2,4,3,.22)');
    shade.addColorStop(0.46, 'rgba(2,4,3,.02)');
    shade.addColorStop(1, 'rgba(2,4,3,.52)');
    context.fillStyle = shade;
    context.fillRect(0, 0, width, height);

    if (!this.mapOverlay.hidden) this.drawMapLayer(context, width, height);
    if (!this.dataOverlay.hidden) this.drawDataLayer(context, width, height);
    if (!this.watermark.hidden) this.drawWatermark(context, width, height);
  }

  drawMapLayer(context, width, height) {
    const layout = this.layouts.map;
    const x = width * layout.x / 100;
    const y = height * layout.y / 100;
    const layerWidth = width * layout.w / 100;
    const layerHeight = layerWidth / 1.5;
    context.save();
    context.drawImage(this.routeScene.canvas, x, y, layerWidth, layerHeight);
    context.restore();
  }

  drawDataLayer(context, width, height) {
    const layer = this.renderLayers?.data;
    if (!layer) throw new Error('The export card snapshot is not ready.');
    context.drawImage(
      layer.canvas,
      width * layer.x,
      height * layer.y,
      width * layer.width,
      height * layer.height,
    );
  }

  drawWatermark(context, width, height) {
    context.save();
    context.textAlign = 'right';
    context.fillStyle = 'rgba(241,243,233,.68)';
    context.font = `700 ${Math.max(12, width * 0.012)}px Arial, sans-serif`;
    context.shadowColor = 'rgba(0,0,0,.75)';
    context.shadowBlur = width * 0.012;
    context.fillText(this.watermarkText.textContent, width * 0.955, height * 0.97);
    context.restore();
  }

  showExportProgress({ kicker, title, detail, progress = 0, cancelable = true }) {
    this.exportCancelRequested = false;
    this.exportPreviousFocus = document.activeElement;
    const app = document.querySelector('#app');
    this.appWasInert = Boolean(app?.hasAttribute('inert'));
    this.appPreviousAriaHidden = app?.getAttribute('aria-hidden') ?? null;
    if (app) {
      app.setAttribute('inert', '');
      app.setAttribute('aria-hidden', 'true');
    }
    document.body.classList.add('is-export-modal-open');
    this.progressModal.hidden = false;
    this.updateExportProgress({ kicker, title, detail, progress, cancelable });
    requestAnimationFrame(() => {
      if (!this.progressModal.hidden && !this.cancelExportButton.disabled) this.cancelExportButton.focus();
    });
  }

  updateExportProgress({ kicker, title, detail, progress, cancelable = this.exportCancelable }) {
    if (kicker != null) this.progressKicker.textContent = kicker;
    if (title != null) this.progressTitle.textContent = title;
    if (detail != null) this.progressDetail.textContent = detail;
    const determinate = Number.isFinite(progress);
    if (determinate) {
      this.exportProgressValue = clamp(Number(progress), 0, 100);
      this.progressTrack.classList.remove('is-indeterminate');
      this.progressTrack.setAttribute('aria-valuenow', String(Math.round(this.exportProgressValue)));
      this.progressBar.style.width = `${this.exportProgressValue}%`;
      this.progressPercent.textContent = `${Math.round(this.exportProgressValue)}%`;
    } else {
      this.exportProgressValue = null;
      this.progressTrack.classList.add('is-indeterminate');
      this.progressTrack.removeAttribute('aria-valuenow');
      this.progressBar.style.width = '';
      this.progressPercent.textContent = '—';
    }
    this.exportCancelable = Boolean(cancelable) && !this.exportCancelRequested;
    this.cancelExportButton.disabled = !this.exportCancelable;
    this.cancelExportButton.querySelector('span').textContent = this.exportCancelRequested ? '正在取消…' : '取消导出';
    if (!this.progressModal.hidden && this.cancelExportButton.disabled && document.activeElement === this.cancelExportButton) {
      this.progressDialog.focus();
    }
  }

  requestExportCancel() {
    if (!this.rendering || !this.exportCancelable || this.exportCancelRequested) return;
    this.exportCancelRequested = true;
    this.updateExportProgress({
      title: '正在取消导出',
      detail: '正在停止编码并清理临时资源，不会生成文件…',
      progress: this.exportProgressValue,
      cancelable: false,
    });
  }

  throwIfExportCancelled() {
    if (this.exportCancelRequested) throw new DOMException('Export cancelled by user.', 'AbortError');
  }

  isExportCancellation(error) {
    return this.exportCancelRequested && error?.name === 'AbortError';
  }

  hideExportProgress() {
    this.progressModal.hidden = true;
    document.body.classList.remove('is-export-modal-open');
    const app = document.querySelector('#app');
    if (app) {
      if (this.appWasInert) app.setAttribute('inert', '');
      else app.removeAttribute('inert');
      if (this.appPreviousAriaHidden == null) app.removeAttribute('aria-hidden');
      else app.setAttribute('aria-hidden', this.appPreviousAriaHidden);
    }
    const previousFocus = this.exportPreviousFocus;
    this.exportPreviousFocus = null;
    this.exportCancelable = false;
    this.exportCancelRequested = false;
    this.cancelExportButton.disabled = false;
    this.cancelExportButton.querySelector('span').textContent = '取消导出';
    if (previousFocus?.isConnected) previousFocus.focus({ preventScroll: true });
  }

  async exportImage() {
    if (!this.activity || this.rendering) return;
    const filename = `ride-relief-${this.format}.png`;
    let saveTarget;
    try {
      saveTarget = await requestSaveTarget(filename, 'PNG 图片', 'image/png', '.png');
    } catch (error) {
      console.error(error);
      this.notify?.('无法打开保存窗口，请稍后重试', 'error');
      return;
    }
    if (saveTarget.mode === 'cancelled') {
      this.notify?.('已取消保存', 'info');
      return;
    }
    this.pause();
    this.setRendering(true, '正在生成高分辨率图片…');
    this.showExportProgress({
      kicker: 'EXPORTING PNG',
      title: '正在准备高清图片',
      detail: '正在准备背景素材和路线图层…',
      progress: 0,
    });
    try {
      await this.ensureBackgroundReady();
      this.throwIfExportCancelled();
      this.updateExportProgress({ title: '正在准备画面', detail: '背景素材已就绪，正在同步预览状态…', progress: 18 });
      await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      this.throwIfExportCancelled();
      this.updateExportProgress({ title: '正在生成数据图层', detail: '正在按最终分辨率生成数据卡片…', progress: 34 });
      this.renderLayers = await this.prepareRenderLayers();
      this.throwIfExportCancelled();
      this.updateExportProgress({ title: '正在检查画面边界', detail: '正在确认路线和数据卡片完整位于画布内…', progress: 56 });
      this.validateRenderBounds();
      const canvas = this.createRenderCanvas();
      this.beginRouteRender();
      this.routeScene.renderFrame(this.presentationProgress * this.effectiveRotationDuration() * 1000);
      this.drawComposition(canvas.getContext('2d'), canvas.width, canvas.height);
      this.throwIfExportCancelled();
      this.updateExportProgress({ title: '正在编码 PNG', detail: '正在生成高分辨率图片文件…', progress: 76 });
      const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
      this.throwIfExportCancelled();
      if (!blob?.size) throw new Error('PNG renderer produced an empty file.');
      this.updateExportProgress({ title: '正在保存图片', detail: '图片已生成，正在写入你选择的位置…', progress: 94, cancelable: false });
      const destination = await saveBlob(blob, filename, saveTarget);
      this.updateExportProgress({ title: '图片导出完成', detail: '高清 PNG 已成功写入。', progress: 100, cancelable: false });
      const destinationLabel = destination === 'chosen-location' ? '你选择的位置' : '浏览器默认下载目录';
      this.lastExportSummary = completedExportSummary({
        kind: 'PNG',
        formatKey: this.format,
        destinationLabel,
      });
      this.notify?.(
        destination === 'chosen-location' ? '图片已保存到你选择的位置' : '图片已保存到浏览器默认下载目录',
        'success',
      );
    } catch (error) {
      if (this.isExportCancellation(error)) {
        this.notify?.('已取消图片导出，没有生成文件', 'info');
      } else {
        console.error(error);
        this.notify?.(
          error?.message?.includes('超出最终画布') ? error.message : '图片导出失败，请尝试其他素材格式',
          'error',
        );
      }
    } finally {
      this.endRouteRender();
      this.renderLayers = null;
      this.setRendering(false);
      this.hideExportProgress();
      if (!this.root.hidden) this.startPreview();
    }
  }

  async exportVideo() {
    if (!this.activity || this.rendering) return;
    const filename = `ride-relief-${this.format}.mp4`;
    const frameRate = VIDEO_FRAME_RATE;
    const frameDuration = 1 / frameRate;
    const qualityBitrate = VIDEO_BITRATE;
    const dimensions = FORMATS[this.format];
    let media;
    let encoderMode = 'wasm';
    let hardwareAcceleration = 'no-preference';
    let saveTarget;
    let output;
    let wasmEncoder;
    let videoSource;

    this.setRendering(true, '正在检查 H.264 MP4 编码支持…');
    try {
      try {
        media = await import('mediabunny');
        const quality = new media.Quality({ bitrate: qualityBitrate, bitrateMode: 'variable' });
        for (const preference of ['prefer-hardware', 'no-preference']) {
          const supported = await media.canEncodeVideo('avc', {
            width: dimensions.width,
            height: dimensions.height,
            quality,
            hardwareAcceleration: preference,
          });
          if (supported) {
            encoderMode = 'webcodecs';
            hardwareAcceleration = preference;
            break;
          }
        }
      } catch (error) {
        console.info('浏览器硬件 H.264 编码不可用，将使用本地 WASM 编码。', error);
      }
      if (encoderMode === 'wasm' && typeof WebAssembly === 'undefined') {
        throw new Error('This browser provides neither WebCodecs nor WebAssembly.');
      }
      this.renderStatus.textContent = encoderMode === 'webcodecs'
        ? '硬件 H.264 编码已就绪，请选择 MP4 保存位置…'
        : '兼容 MP4 编码已就绪，请选择保存位置…';
      saveTarget = await requestSaveTarget(filename, 'MP4 视频', 'video/mp4', '.mp4');
    } catch (error) {
      console.error(error);
      this.notify?.('无法初始化 MP4 编码或打开保存窗口，请稍后重试', 'error');
      this.setRendering(false);
      return;
    }
    if (saveTarget.mode === 'cancelled') {
      this.notify?.('已取消保存', 'info');
      this.setRendering(false);
      return;
    }
    this.pause();
    this.renderStatus.textContent = '准备 H.264 MP4 渲染…';
    this.showExportProgress({
      kicker: 'EXPORTING MP4',
      title: '正在准备视频导出',
      detail: '正在准备背景、数据卡片和路线图层…',
      progress: 0,
    });
    try {
      await this.ensureBackgroundReady();
      this.throwIfExportCancelled();
      this.updateExportProgress({ title: '正在生成数据图层', detail: '正在按最终分辨率生成数据卡片…', progress: 5 });
      this.renderLayers = await this.prepareRenderLayers();
      this.throwIfExportCancelled();
      this.updateExportProgress({ title: '正在检查画面边界', detail: '正在确认路线和数据卡片完整位于画布内…', progress: 9 });
      this.validateRenderBounds();
      const canvas = this.createRenderCanvas();
      const context = canvas.getContext('2d');
      this.beginRouteRender();
      let target;
      if (encoderMode === 'webcodecs') {
        target = new media.BufferTarget();
        output = new media.Output({
          format: new media.Mp4OutputFormat({ fastStart: 'in-memory' }),
          target,
        });
        const quality = new media.Quality({ bitrate: qualityBitrate, bitrateMode: 'variable' });
        videoSource = new media.CanvasSource(canvas, {
          codec: 'avc',
          quality,
          keyFrameInterval: 2,
          latencyMode: 'quality',
          hardwareAcceleration,
          contentHint: 'motion',
        });
        output.addVideoTrack(videoSource, { frameRate });
        await output.start();
        this.throwIfExportCancelled();
      } else {
        this.renderStatus.textContent = '正在载入兼容 MP4 编码器…';
        this.updateExportProgress({ title: '正在载入视频编码器', detail: '首次使用兼容编码器可能需要稍等片刻…', progress: null });
        const h264 = await loadWasmH264Encoder();
        this.throwIfExportCancelled();
        wasmEncoder = await h264.createH264MP4Encoder();
        this.throwIfExportCancelled();
        Object.assign(wasmEncoder, {
          width: canvas.width,
          height: canvas.height,
          frameRate,
          kbps: qualityBitrate / 1000,
          speed: 10,
          groupOfPictures: frameRate * 2,
          temporalDenoise: false,
        });
        wasmEncoder.initialize();
      }
      this.updateExportProgress({ title: '正在编码 MP4', detail: '编码器已就绪，开始逐帧渲染…', progress: 12 });

      if (this.backgroundType === 'video') {
        this.backgroundVideo.loop = false;
        this.backgroundVideo.pause();
        await this.seekBackgroundFrame(0);
        this.throwIfExportCancelled();
      }
      const duration = Math.max(0.1, this.previewDuration);
      const rotationDuration = this.effectiveRotationDuration();
      const totalFrames = Math.max(1, Math.ceil(duration * frameRate));
      let lastReportedProgress = -1;

      for (let frameIndex = 0; frameIndex < totalFrames; frameIndex += 1) {
        this.throwIfExportCancelled();
        const timestamp = frameIndex * frameDuration;
        if (this.backgroundType === 'video') {
          await this.seekBackgroundFrame(timestamp);
          this.throwIfExportCancelled();
        }
        const progress = clamp(timestamp / duration, 0, 1);
        const presentationProgress = (timestamp % rotationDuration) / rotationDuration;
        this.updateAnimationFrame(progress, presentationProgress, timestamp);
        this.drawComposition(context, canvas.width, canvas.height);
        if (videoSource) {
          await videoSource.add(timestamp, frameDuration, {
            keyFrame: frameIndex % (frameRate * 2) === 0,
          });
          this.throwIfExportCancelled();
        } else {
          wasmEncoder.addFrameRgba(context.getImageData(0, 0, canvas.width, canvas.height).data);
          if (frameIndex % 2 === 0) await new Promise((resolve) => requestAnimationFrame(resolve));
          this.throwIfExportCancelled();
        }
        const modeLabel = encoderMode === 'webcodecs' ? 'H.264 硬件编码' : 'H.264 兼容编码';
        const frameProgress = (frameIndex + 1) / totalFrames;
        const renderProgress = 12 + frameProgress * 80;
        const reportedProgress = Math.floor(renderProgress);
        if (reportedProgress !== lastReportedProgress || frameIndex === totalFrames - 1) {
          lastReportedProgress = reportedProgress;
          this.renderStatus.textContent = `正在编码 MP4 ${Math.round(frameProgress * 100)}% · ${modeLabel}`;
          this.updateExportProgress({
            title: '正在编码 MP4',
            detail: `${frameIndex + 1} / ${totalFrames} 帧 · ${modeLabel}`,
            progress: renderProgress,
          });
        }
      }

      this.throwIfExportCancelled();
      this.updateExportProgress({ title: '正在封装 MP4', detail: '视频帧已完成，正在生成可播放的 MP4 文件…', progress: 94, cancelable: false });
      this.backgroundVideo.pause();
      let mp4Buffer;
      if (videoSource) {
        const activeVideoSource = videoSource;
        videoSource = null;
        activeVideoSource.close();
        await output.finalize();
        if (!target.buffer) throw new Error('MP4 encoder did not produce an output buffer.');
        mp4Buffer = target.buffer;
      } else {
        wasmEncoder.finalize();
        mp4Buffer = wasmEncoder.FS.readFile(wasmEncoder.outputFilename).slice();
        wasmEncoder.delete();
        wasmEncoder = null;
      }
      if (!hasMp4Signature(mp4Buffer)) throw new Error('MP4 encoder produced an invalid file signature.');
      this.updateExportProgress({ title: '正在写入视频', detail: 'MP4 已生成，正在写入你选择的位置…', progress: 98, cancelable: false });
      const destination = await saveBlob(new Blob([mp4Buffer], { type: 'video/mp4' }), filename, saveTarget);
      this.updateExportProgress({ title: '视频导出完成', detail: 'H.264 MP4 已成功写入。', progress: 100, cancelable: false });
      const destinationLabel = destination === 'chosen-location' ? '你选择的位置' : '浏览器默认下载目录';
      this.lastExportSummary = completedExportSummary({
        kind: 'MP4',
        formatKey: this.format,
        destinationLabel,
        durationSeconds: duration,
      });
      this.notify?.(
        destination === 'chosen-location' ? 'MP4 已保存到你选择的位置' : 'MP4 已保存到浏览器默认下载目录',
        'success',
      );
      this.updateAnimationFrame(0);
    } catch (error) {
      const cancelled = this.isExportCancellation(error);
      if (!cancelled) console.error(error);
      if (videoSource) {
        try { videoSource.close(); } catch {}
        videoSource = null;
      }
      if (output && output.state !== 'finalized' && output.state !== 'canceled') {
        await output.cancel().catch(() => {});
      }
      if (wasmEncoder) {
        try { wasmEncoder.delete(); } catch {}
        wasmEncoder = null;
      }
      if (cancelled) {
        this.notify?.('已取消 MP4 导出，没有生成文件', 'info');
      } else {
        this.notify?.(
          error?.message?.includes('超出最终画布') ? error.message : 'MP4 渲染失败，请确认素材可播放并留出足够内存',
          'error',
        );
      }
    } finally {
      this.endRouteRender();
      this.renderLayers = null;
      this.backgroundVideo.loop = true;
      this.setRendering(false);
      this.hideExportProgress();
      if (!this.root.hidden) this.startPreview();
    }
  }

  setRendering(rendering, message) {
    this.rendering = rendering;
    this.imageExportButton.disabled = rendering;
    this.videoExportButton.disabled = rendering;
    this.renderStatus.classList.toggle('is-rendering', rendering);
    this.renderStatus.textContent = rendering
      ? message
      : this.lastExportSummary || idleRenderStatus();
  }
}
