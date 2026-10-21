import '@phosphor-icons/web/regular';
import {
  analyzeActivity,
  formatActivityDate,
  formatClock,
  formatPace,
  fetchActivityFile,
  loadBundledSample,
  parseActivityFile,
  sportMeta,
} from './data.js';
import { ExportComposer } from './export-composer.js';
import { preparePhotos, releasePhotos } from './photos.js';
import { RouteScene } from './route-scene.js';
import './styles.css';

const elements = Object.fromEntries([
  'fit-input', 'photo-input', 'export-button', 'share-stage', 'route-canvas', 'stage-loader',
  'analysis-view', 'export-view', 'analysis-mode-button', 'export-mode-button',
  'activity-kicker', 'activity-title', 'activity-coordinate', 'activity-source',
  'activity-summary-icon', 'activity-summary-title', 'activity-profile-heading', 'activity-profile-label',
  'metric-distance', 'metric-duration', 'metric-speed', 'metric-ascent', 'metric-calories', 'metric-max-speed', 'metric-cadence',
  'metric-duration-card', 'metric-speed-card', 'metric-speed-icon', 'metric-speed-label', 'metric-calories-card',
  'metric-max-card', 'metric-max-icon', 'metric-max-label', 'metric-cadence-card', 'metric-cadence-icon', 'metric-cadence-label',
  'analysis-data-quality', 'analysis-profile-title', 'analysis-profile-copy',
  'location-context-card', 'location-confidence', 'location-name', 'location-region',
  'location-summary', 'location-facts', 'location-sources',
  'skill-analysis-source', 'deep-analysis-list', 'deep-analysis-note',
  'pace-easy-bar', 'pace-steady-bar', 'pace-fast-bar', 'pace-easy-value', 'pace-steady-value', 'pace-fast-value',
  'pace-distribution', 'pace-heading', 'pace-data-status', 'pace-easy-label', 'pace-steady-label', 'pace-fast-label',
  'analysis-moving-ratio', 'analysis-pause-time', 'analysis-altitude-range', 'analysis-temperature',
  'analysis-moving-card', 'analysis-pause-card', 'trend-heading', 'trend-speed-legend',
  'analysis-ascent-density', 'analysis-route-gap', 'analysis-chart', 'recommendation-count', 'recommendation-list',
  'cadence-analysis-card', 'cadence-data-status', 'analysis-cadence-average', 'analysis-cadence-max',
  'analysis-cadence-coverage', 'cadence-low-bar', 'cadence-cruise-bar', 'cadence-high-bar',
  'cadence-low-value', 'cadence-cruise-value', 'cadence-high-value', 'cadence-insight',
  'cadence-heading-icon', 'cadence-heading', 'cadence-max-label', 'cadence-coverage-label',
  'grade-analysis-card', 'grade-data-status', 'analysis-grade-max', 'analysis-grade-representative',
  'analysis-grade-coverage', 'grade-descent-bar', 'grade-flat-bar', 'grade-climb-bar', 'grade-steep-bar',
  'grade-descent-value', 'grade-flat-value', 'grade-climb-value', 'grade-steep-value',
  'analysis-climb-list', 'grade-insight',
  'sensor-card', 'heart-rate-metric', 'power-metric', 'analysis-heart-rate', 'analysis-power',
  'live-distance', 'live-secondary', 'live-secondary-unit', 'photo-story', 'photo-current', 'photo-total', 'photo-title',
  'photo-meta', 'photo-preview', 'photo-count', 'photo-drop', 'photo-list', 'spin-button', 'reset-button',
  'photo-route-editor', 'photo-route-map', 'photo-route-path', 'photo-route-markers',
  'photo-route-selection', 'photo-route-status', 'photo-auto-match', 'photo-set-cover',
  'play-button', 'progress-input', 'timeline-time', 'timeline-duration', 'toast',
].map((id) => [id.replaceAll('-', '_'), document.getElementById(id)]));

let activity = null;
let photos = [];
let currentPhoto = null;
let selectedPhoto = null;
let photoRoutePoints = [];
let progressIsDragging = false;
let toastTimer = null;
let currentAnalysis = null;
let skillAnalysisRequest = 0;
let chartResizeFrame = null;
let analysisPlayingBeforeExport = true;
let currentMode = 'analysis';
const pageParameters = new URLSearchParams(window.location.search);

function sameOriginResource(value, fallback = null) {
  if (!value) return fallback;
  try {
    const url = new URL(value, window.location.href);
    if (url.origin !== window.location.origin) return fallback;
    return `${url.pathname}${url.search}`;
  } catch {
    return fallback;
  }
}

const analysisResource = sameOriginResource(pageParameters.get('analysis'), '/skill-analysis.json');
const trackResource = sameOriginResource(pageParameters.get('track'));

function showToast(message, type = 'info') {
  clearTimeout(toastTimer);
  elements.toast.textContent = message;
  elements.toast.dataset.type = type;
  elements.toast.classList.add('is-visible');
  toastTimer = setTimeout(() => elements.toast.classList.remove('is-visible'), 3200);
}

function sessionNumber(value, fallback = 0) {
  return Number.isFinite(Number(value)) ? Number(value) : fallback;
}

function metricMarkup(value, unit, digits = 0) {
  if (!Number.isFinite(Number(value))) return '—';
  return `${Number(value).toFixed(digits)}${unit ? ` <small>${unit}</small>` : ''}`;
}

function setIcon(element, icon) {
  if (!element) return;
  element.className = [...element.classList].filter((name) => !name.startsWith('ph-')).join(' ');
  element.classList.add('ph', icon);
}

function buildActivityTitle(startTime, distanceMeters, sport) {
  const date = new Date(startTime);
  const hour = Number.isNaN(date.getTime()) ? 12 : Number(new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    hourCycle: 'h23',
    timeZone: 'Asia/Shanghai',
  }).format(date));
  const timeLabel = hour < 10 ? '晨间' : hour < 14 ? '午间' : hour < 18 ? '午后' : '夜间';
  const kilometers = Math.max(0, Number(distanceMeters) || 0) / 1000;
  const type = sportMeta(sport);
  const distanceLabel = type.key === 'cycling'
    ? kilometers >= 50 ? '长途' : kilometers >= 30 ? '耐力' : kilometers >= 15 ? '巡游' : '短途'
    : type.key === 'running'
      ? kilometers >= 21 ? '长距离' : kilometers >= 10 ? '耐力跑' : '轻松跑'
      : type.key === 'hiking'
        ? kilometers >= 15 ? '长线徒步' : kilometers >= 7 ? '山野徒步' : '轻徒步'
        : '户外路线';
  return `${timeLabel}${distanceLabel} · ${kilometers.toFixed(kilometers < 10 ? 1 : 0)} 公里`;
}

function drawAnalysisChart(records) {
  const canvas = elements.analysis_chart;
  if (!canvas || !records?.length) return;
  const width = Math.max(240, Math.round(canvas.clientWidth));
  const height = 126;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = Math.round(width * dpr);
  canvas.height = Math.round(height * dpr);
  const context = canvas.getContext('2d');
  context.setTransform(dpr, 0, 0, dpr, 0, 0);
  context.clearRect(0, 0, width, height);

  const maxPoints = 140;
  const stride = Math.max(1, Math.ceil(records.length / maxPoints));
  const sampled = records.filter((_, index) => index % stride === 0 || index === records.length - 1);
  const altitudes = sampled.map((record) => Number(record.altitude) || 0);
  const hasSpeedData = sampled.some((record) => record.speed != null && Number(record.speed) > 0);
  const speeds = sampled.map((record) => record.speed == null ? 0 : Number(record.speed) || 0);
  const minAltitude = Math.min(...altitudes);
  const maxAltitude = Math.max(...altitudes);
  const maxSpeed = Math.max(...speeds, 1);
  const padding = { top: 8, right: 3, bottom: 8, left: 3 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;
  const xFor = (index) => padding.left + index / Math.max(1, sampled.length - 1) * plotWidth;
  const altitudeY = (value) => padding.top + (1 - (value - minAltitude) / Math.max(1, maxAltitude - minAltitude)) * plotHeight;
  const speedY = (value) => padding.top + (1 - value / maxSpeed) * plotHeight;
  const accent = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#d6ff64';

  context.strokeStyle = 'rgba(235, 240, 225, 0.08)';
  context.lineWidth = 1;
  for (let row = 1; row < 4; row += 1) {
    const y = padding.top + plotHeight * row / 4;
    context.beginPath();
    context.moveTo(0, y);
    context.lineTo(width, y);
    context.stroke();
  }

  context.beginPath();
  altitudes.forEach((value, index) => {
    const x = xFor(index);
    const y = altitudeY(value);
    if (index === 0) context.moveTo(x, y);
    else context.lineTo(x, y);
  });
  context.lineTo(width - padding.right, height - padding.bottom);
  context.lineTo(padding.left, height - padding.bottom);
  context.closePath();
  context.globalAlpha = 0.12;
  context.fillStyle = accent;
  context.fill();
  context.globalAlpha = 1;

  context.beginPath();
  altitudes.forEach((value, index) => {
    const x = xFor(index);
    const y = altitudeY(value);
    if (index === 0) context.moveTo(x, y);
    else context.lineTo(x, y);
  });
  context.strokeStyle = accent;
  context.lineWidth = 1.5;
  context.stroke();

  if (hasSpeedData) {
    context.beginPath();
    speeds.forEach((value, index) => {
      const x = xFor(index);
      const y = speedY(value);
      if (index === 0) context.moveTo(x, y);
      else context.lineTo(x, y);
    });
    context.strokeStyle = 'rgba(241, 243, 233, 0.72)';
    context.lineWidth = 1;
    context.stroke();
  }
}

function renderRecommendations(recommendations) {
  elements.recommendation_list.replaceChildren();
  recommendations.forEach((recommendation, index) => {
    const card = document.createElement('article');
    card.className = 'recommendation-card';
    card.setAttribute('role', 'listitem');

    const number = document.createElement('span');
    number.className = 'recommendation-number';
    const categoryIcons = {
      节奏: 'ph-timer',
      踏频: 'ph-person-simple-bike',
      步频: 'ph-person-simple-run',
      路线: 'ph-mountains',
      隐私: 'ph-shield-check',
      数据: 'ph-pulse',
      补给: 'ph-drop',
    };
    const icon = document.createElement('i');
    icon.className = `ph ${categoryIcons[recommendation.category] ?? 'ph-lightbulb'}`;
    icon.setAttribute('aria-hidden', 'true');
    number.append(icon);

    const content = document.createElement('div');
    const meta = document.createElement('span');
    meta.className = 'recommendation-meta';
    meta.textContent = `${recommendation.category} · ${recommendation.evidence ?? recommendation.value}`;
    const title = document.createElement('h3');
    title.textContent = recommendation.title;
    const body = document.createElement('p');
    body.textContent = recommendation.body;
    content.append(meta, title, body);
    if (recommendation.actions?.length) {
      const actions = document.createElement('ul');
      actions.className = 'recommendation-actions';
      recommendation.actions.forEach((action) => {
        const item = document.createElement('li');
        item.textContent = action;
        actions.append(item);
      });
      content.append(actions);
    }
    card.append(number, content);
    elements.recommendation_list.append(card);
  });
  elements.recommendation_count.textContent = `${recommendations.length} 条`;
}

function buildLocalDeepAnalysis(analysis) {
  const { metrics, profile } = analysis;
  const type = sportMeta(metrics.sport);
  const sections = [];
  const primaryClimb = metrics.climbs[0];
  sections.push({
    category: '路线负荷',
    evidence: `${metrics.ascentDensity.toFixed(1)} m/km · ${metrics.climbs.length} 段主要爬坡`,
    title: profile.title,
    body: primaryClimb
      ? `累计爬升并不是平均分散在全程：最主要的一段约 ${(primaryClimb.distanceMeters / 1000).toFixed(2)} km，获得 ${Math.round(primaryClimb.elevationGainMeters)} m 高度。分析重点应放在爬升集中位置，而不只是总公里数。`
      : `每公里爬升约 ${metrics.ascentDensity.toFixed(1)} m，没有识别出满足长度、坡度和爬升门槛的连续爬坡段，路线负荷主要来自零散起伏。`,
    findings: [
      `代表性陡坡为 ${metrics.representativeGrade == null ? '未记录' : `${metrics.representativeGrade.toFixed(1)}%（P99）`}`,
      `海拔活动范围 ${metrics.altitudeRange == null ? '未记录' : `${Math.round(metrics.altitudeRange)} m`}`,
    ],
  });

  if (metrics.hasTimeData && metrics.pace) {
    const dominantPace = Object.entries(metrics.pace).sort((left, right) => right[1] - left[1])[0]?.[0];
    const paceIndex = dominantPace === 'fast' ? 2 : dominantPace === 'steady' ? 1 : 0;
    sections.push({
      category: '节奏结构',
      evidence: `${Math.round(metrics.movingRatio)}% 移动占比 · ${type.paceLabels[paceIndex]}段占比最高`,
      title: metrics.movingRatio < 85 ? '停留对整体连续性影响明显' : `整段${type.zh}的连续性较好`,
      body: `${type.paceLabels.join(' / ')}段分别占 ${Math.round(metrics.pace.easy)}% / ${Math.round(metrics.pace.steady)}% / ${Math.round(metrics.pace.fast)}%。这些比例只描述本次轨迹的相对速度结构，不等同于个人训练分区。`,
      findings: [
        `暂停时间 ${formatClock(metrics.pauseSeconds)}`,
        metrics.averagePaceSeconds ? `平均配速 ${formatPace(metrics.averagePaceSeconds)} /km` : `平均速度 ${metrics.averageSpeed.toFixed(1)} km/h`,
      ],
    });
  } else {
    sections.push({
      category: '时间与配速',
      evidence: `${String(activity?.format ?? '轨迹').toUpperCase()} 未提供逐点时间`,
      title: '路线形态可信，时长与配速不可恢复',
      body: '这份文件可以支持距离、海拔、坡度与路线动画，但无法从空间点间距反推出实际行进速度；页面会把相关指标明确标为未记录。',
      findings: ['不会把 00:00 当作真实时长', '照片仍可通过 GPS 或手动点选绑定路线'],
    });
  }

  if (metrics.sport === 'cycling' || metrics.sport === 'running') {
    const unit = metrics.sport === 'running' ? 'spm' : 'rpm';
    sections.push({
      category: `${type.cadence}与数据`,
      evidence: metrics.effectiveCadence == null
        ? `${type.cadence}未记录`
        : `${Math.round(metrics.effectiveCadence)} ${unit} · ${Math.round(metrics.cadenceCoverage)}% 覆盖`,
      title: metrics.effectiveCadence == null ? `当前无法解释${type.cadence}结构` : `有效${type.cadence}需要结合覆盖率一起看`,
      body: metrics.effectiveCadence == null
        ? `没有${type.cadence}数据时，不应从速度变化反推技术效率；路线、海拔和节奏分析仍可独立使用。`
        : `有效平均排除了零值，但仍有约 ${Math.max(0, 100 - metrics.cadenceCoverage).toFixed(0)}% 的轨迹没有有效记录，可能来自停留或传感器丢失。`,
      findings: metrics.effectiveCadence == null ? [
        '心率与功率同样只在设备真实记录时展示',
      ] : [
        `低 / 中 / 高区间：${Math.round(metrics.cadence.low)}% / ${Math.round(metrics.cadence.cruise)}% / ${Math.round(metrics.cadence.high)}%`,
        `最高${type.cadence} ${Math.round(metrics.maxCadence)} ${unit}`,
      ],
    });
  }

  if (metrics.averageTemperature != null || metrics.hasHeartRate || metrics.hasPower) {
    const sensorNames = [metrics.hasHeartRate && '心率', metrics.hasPower && '功率'].filter(Boolean);
    sections.push({
      category: '环境与传感器',
      evidence: sensorNames.length ? `${sensorNames.join('、')}已记录` : '仅记录环境温度',
      title: sensorNames.length ? '可用实测字段能够支持更细的强度复盘' : '气温信息可辅助解释体感，但不是身体温度',
      body: metrics.averageTemperature == null
        ? '本次没有环境温度记录；强度结论仍应以实际心率、功率覆盖和个人阈值为前提。'
        : `设备记录平均环境温度 ${Math.round(metrics.averageTemperature)}°C。它适合用于解释补水和环境压力，不应被当作体温或单独用于判断恢复状态。`,
      findings: [
        metrics.hasHeartRate ? `平均 / 最大心率 ${Math.round(metrics.averageHeartRate)} / ${Math.round(metrics.maxHeartRate)} bpm` : '心率未记录',
        metrics.hasPower ? `平均 / 最大功率 ${Math.round(metrics.averagePower)} / ${Math.round(metrics.maxPower)} W` : '功率未记录',
      ],
    });
  }
  return sections;
}

function renderDeepAnalysis(sections, { source = '轨迹本地分析', note } = {}) {
  elements.deep_analysis_list.replaceChildren();
  sections.forEach((section) => {
    const card = document.createElement('article');
    card.className = 'deep-analysis-card';
    card.setAttribute('role', 'listitem');
    const meta = document.createElement('span');
    meta.textContent = `${section.category ?? '观察'} · ${section.evidence ?? '基于当前轨迹'}`;
    const title = document.createElement('h3');
    title.textContent = section.title;
    const body = document.createElement('p');
    body.textContent = section.body;
    card.append(meta, title, body);
    if (section.findings?.length) {
      const findings = document.createElement('ul');
      section.findings.forEach((finding) => {
        const item = document.createElement('li');
        item.textContent = finding;
        findings.append(item);
      });
      card.append(findings);
    }
    elements.deep_analysis_list.append(card);
  });
  elements.skill_analysis_source.textContent = source;
  elements.deep_analysis_note.textContent = note
    ?? '固定指标由轨迹文件计算；扩展内容可由分析 Skill 按本次活动动态生成。';
}

function renderLocationContext(location) {
  elements.location_context_card.hidden = !location;
  elements.location_facts.replaceChildren();
  elements.location_sources.replaceChildren();
  exportComposer.setLocation(location);
  if (!location) return;

  elements.location_confidence.textContent = location.confidenceLabel || '公开地点信息';
  elements.location_name.textContent = location.name || '路线地点';
  elements.location_region.textContent = location.region || '区域待确认';
  elements.location_summary.textContent = location.summary || '';
  for (const fact of location.facts ?? []) {
    const item = document.createElement('li');
    item.textContent = fact;
    elements.location_facts.append(item);
  }
  for (const source of location.sources ?? []) {
    if (!source?.url) continue;
    const link = document.createElement('a');
    link.href = source.url;
    link.target = '_blank';
    link.rel = 'noreferrer';
    link.textContent = source.title || '公开来源';
    const icon = document.createElement('i');
    icon.className = 'ph ph-arrow-up-right';
    icon.setAttribute('aria-hidden', 'true');
    link.append(icon);
    elements.location_sources.append(link);
  }
  const publicLabel = location.exportLabel || location.name;
  if (publicLabel) elements.activity_coordinate.textContent = publicLabel;
}

async function hydrateSkillAnalysis(payload, fallbackRecommendations) {
  const request = ++skillAnalysisRequest;
  try {
    const analysisUrl = new URL(analysisResource, window.location.origin);
    analysisUrl.searchParams.set('t', Date.now());
    const response = await fetch(analysisUrl, { cache: 'no-store' });
    if (!response.ok) return;
    const document = await response.json();
    if (request !== skillAnalysisRequest) return;
    const reports = Array.isArray(document.reports) ? document.reports : [document];
    const source = String(payload.source ?? '').split(/[\\/]/).at(-1);
    const report = reports.find((candidate) => candidate?.source === source);
    if (!report) return;
    renderLocationContext(report.location ?? null);
    if (report.deepAnalysis?.length) {
      renderDeepAnalysis(report.deepAnalysis, {
        source: report.provider ?? 'Fit Ride Studio Skill',
        note: report.note,
      });
    }
    renderRecommendations(report.recommendations?.length ? report.recommendations : fallbackRecommendations);
  } catch (error) {
    console.info('没有可用的 Skill 扩展分析，继续显示本地轨迹分析。', error);
  }
}

function renderGradeAnalysis(metrics) {
  const hasGrade = metrics.grade && metrics.gradeCoverage > 10;
  elements.grade_analysis_card.classList.toggle('is-empty', !hasGrade);
  elements.grade_data_status.textContent = hasGrade
    ? `${Math.round(metrics.gradeCoverage)}% 记录覆盖 · 按距离`
    : '轨迹未记录';
  elements.analysis_climb_list.replaceChildren();
  if (!hasGrade) {
    elements.grade_insight.textContent = '这份轨迹没有足够的坡度记录；仅凭累计爬升无法可靠还原坡度区间和主要爬坡段。';
    return;
  }

  elements.analysis_grade_max.innerHTML = metricMarkup(metrics.maxGrade, '%', 1);
  elements.analysis_grade_representative.innerHTML = metricMarkup(metrics.representativeGrade, '% · P99', 1);
  elements.analysis_grade_coverage.textContent = `${Math.round(metrics.gradeCoverage)}%`;
  const gradeEntries = [
    ['descent', elements.grade_descent_bar, elements.grade_descent_value],
    ['flat', elements.grade_flat_bar, elements.grade_flat_value],
    ['climb', elements.grade_climb_bar, elements.grade_climb_value],
    ['steep', elements.grade_steep_bar, elements.grade_steep_value],
  ];
  for (const [key, bar, label] of gradeEntries) {
    const value = metrics.grade[key];
    bar.style.width = `${value}%`;
    label.textContent = `${value.toFixed(1)}%`;
  }

  metrics.climbs.forEach((climb, index) => {
    const item = document.createElement('article');
    item.className = 'climb-item';
    const rank = document.createElement('span');
    rank.className = 'climb-rank';
    rank.textContent = `#${index + 1}`;
    const copy = document.createElement('div');
    const position = document.createElement('span');
    position.textContent = `约 ${Number(climb.startDistanceMeters / 1000).toFixed(1)} km 处开始`;
    const headline = document.createElement('strong');
    headline.textContent = `${Number(climb.distanceMeters / 1000).toFixed(2)} km · 爬升 ${Math.round(climb.elevationGainMeters)} m`;
    const detail = document.createElement('small');
    detail.textContent = `平均 ${climb.averageGradePercent.toFixed(1)}% · 代表峰值 ${climb.maxGradePercent.toFixed(1)}%`;
    copy.append(position, headline, detail);
    item.append(rank, copy);
    elements.analysis_climb_list.append(item);
  });

  const analyzedKilometers = metrics.gradeAnalyzedDistance / 1000;
  elements.grade_insight.textContent = metrics.climbs.length
    ? `坡度分布按 ${analyzedKilometers.toFixed(1)} km 有效距离加权；代表性陡坡取平滑坡度的 P99，最高记录保留设备原值。`
    : `坡度分布按 ${analyzedKilometers.toFixed(1)} km 有效距离加权；没有识别出长度至少 200 m、平均坡度至少 2.5% 的连续爬坡。`;
}

function updateAnalysis(payload) {
  currentAnalysis = analyzeActivity(payload);
  const { metrics, profile, recommendations } = currentAnalysis;
  const type = sportMeta(metrics.sport);
  const sourceCount = [
    payload.records.length > 1,
    metrics.altitudeRange != null,
    metrics.gradeCoverage > 10,
    metrics.hasTimeData,
    metrics.averageTemperature != null,
    metrics.cadenceCoverage > 10,
    metrics.hasHeartRate || metrics.hasPower,
  ].filter(Boolean).length;

  elements.analysis_data_quality.textContent = `${sourceCount} / 7 数据维度`;
  elements.analysis_profile_title.textContent = profile.title;
  elements.analysis_profile_copy.textContent = profile.description;
  elements.analysis_moving_ratio.textContent = metrics.movingRatio == null ? '未记录' : `${Math.round(metrics.movingRatio)}%`;
  elements.analysis_pause_time.textContent = metrics.pauseSeconds == null ? '未记录' : formatClock(metrics.pauseSeconds);
  elements.analysis_altitude_range.innerHTML = metrics.minAltitude == null
    ? '—'
    : `${Math.round(metrics.minAltitude)}–${Math.round(metrics.maxAltitude)} <small>m</small>`;
  elements.analysis_temperature.innerHTML = metricMarkup(metrics.averageTemperature, '°C', 0);
  elements.analysis_ascent_density.innerHTML = metricMarkup(metrics.ascentDensity, 'm/km', 1);
  elements.analysis_route_gap.innerHTML = metricMarkup(metrics.routeGap, 'm', 0);

  elements.pace_heading.textContent = metrics.sport === 'cycling' ? '速度结构' : '行进节奏';
  elements.pace_data_status.textContent = metrics.pace ? '按轨迹记录占比' : '时间未记录';
  [elements.pace_easy_label, elements.pace_steady_label, elements.pace_fast_label].forEach((label, index) => {
    label.textContent = type.paceLabels[index];
  });
  elements.pace_distribution.classList.toggle('is-empty', !metrics.pace);
  const paceEntries = [
    ['easy', elements.pace_easy_bar, elements.pace_easy_value],
    ['steady', elements.pace_steady_bar, elements.pace_steady_value],
    ['fast', elements.pace_fast_bar, elements.pace_fast_value],
  ];
  for (const [key, bar, label] of paceEntries) {
    const value = metrics.pace?.[key] ?? 0;
    bar.style.width = `${value}%`;
    label.textContent = metrics.pace ? `${Math.round(value)}%` : '—';
  }

  const hasCadence = metrics.effectiveCadence != null && metrics.cadenceCoverage > 1;
  const cadenceRelevant = metrics.sport === 'cycling' || metrics.sport === 'running' || hasCadence;
  const cadenceUnit = metrics.sport === 'running' ? 'spm' : 'rpm';
  elements.cadence_analysis_card.hidden = !cadenceRelevant;
  elements.cadence_analysis_card.classList.toggle('is-empty', !hasCadence);
  elements.cadence_heading.textContent = `${type.cadence}分析`;
  elements.cadence_max_label.textContent = `最高${type.cadence}`;
  elements.cadence_coverage_label.textContent = `${type.cadence}覆盖`;
  setIcon(elements.cadence_heading_icon, type.icon);
  elements.cadence_data_status.textContent = hasCadence
    ? `${Math.round(metrics.cadenceCoverage)}% 轨迹覆盖`
    : '轨迹未记录';
  if (hasCadence) {
    elements.analysis_cadence_average.innerHTML = metricMarkup(metrics.effectiveCadence, cadenceUnit, 0);
    elements.analysis_cadence_max.innerHTML = metricMarkup(metrics.maxCadence, cadenceUnit, 0);
    elements.analysis_cadence_coverage.textContent = `${Math.round(metrics.cadenceCoverage)}%`;
    const cadenceEntries = [
      ['low', elements.cadence_low_bar, elements.cadence_low_value],
      ['cruise', elements.cadence_cruise_bar, elements.cadence_cruise_value],
      ['high', elements.cadence_high_bar, elements.cadence_high_value],
    ];
    for (const [key, bar, label] of cadenceEntries) {
      const value = metrics.cadence[key];
      bar.style.width = `${value}%`;
      label.textContent = `${Math.round(value)}%`;
    }
    const dominantCadence = Object.entries(metrics.cadence).sort((a, b) => b[1] - a[1])[0]?.[0];
    const cadenceInterpretation = dominantCadence === 'cruise'
      ? '70–90 rpm 巡航区间占主导，踩踏节奏较适合持续骑行。'
      : dominantCadence === 'low'
        ? '低于 70 rpm 的踩踏较多；若主要出现在平路，可尝试更轻齿比。'
        : '高于 90 rpm 的踩踏较多，可结合体感观察高转速下的稳定性。';
    elements.cadence_insight.textContent = metrics.sport === 'running'
      ? `区间只用于描述本次记录；请先确认设备记录的是单脚还是双脚步频。零值已从平均值中排除。`
      : `${cadenceInterpretation} 零踏频已从平均值和区间统计中排除。`;
  } else {
    elements.cadence_insight.textContent = `这份轨迹没有可用${type.cadence}；路线、坡度与海拔分析不受影响。`;
  }

  renderGradeAnalysis(metrics);

  elements.sensor_card.hidden = !(metrics.hasHeartRate || metrics.hasPower);
  elements.heart_rate_metric.hidden = !metrics.hasHeartRate;
  elements.power_metric.hidden = !metrics.hasPower;
  if (metrics.hasHeartRate) {
    elements.analysis_heart_rate.innerHTML = `${Math.round(metrics.averageHeartRate)} / ${Math.round(metrics.maxHeartRate)} <small>bpm</small>`;
  }
  if (metrics.hasPower) {
    elements.analysis_power.innerHTML = `${Math.round(metrics.averagePower)} / ${Math.round(metrics.maxPower)} <small>W</small>`;
  }

  renderDeepAnalysis(buildLocalDeepAnalysis(currentAnalysis), { source: `${String(payload.format ?? 'FIT').toUpperCase()} 本地分析` });
  renderRecommendations(recommendations);
  hydrateSkillAnalysis(payload, recommendations);
  elements.analysis_chart.setAttribute(
    'aria-label',
    metrics.hasSpeedData
      ? `海拔从 ${Math.round(metrics.minAltitude ?? 0)} 到 ${Math.round(metrics.maxAltitude ?? 0)} 米，最高速度 ${metrics.maxSpeed?.toFixed(1)} 公里每小时的趋势图`
      : `海拔从 ${Math.round(metrics.minAltitude ?? 0)} 到 ${Math.round(metrics.maxAltitude ?? 0)} 米的趋势图；轨迹没有时间与速度数据`,
  );
  elements.trend_heading.textContent = metrics.hasSpeedData ? '海拔 / 速度趋势' : '海拔趋势';
  elements.trend_speed_legend.hidden = !metrics.hasSpeedData;
  requestAnimationFrame(() => drawAnalysisChart(payload.records));
}

function updateSummary(payload) {
  const { session, records } = payload;
  const first = records[0];
  const last = records.at(-1);
  const totalDistance = sessionNumber(session.totalDistance, last.distance);
  const analysis = analyzeActivity(payload);
  const { metrics } = analysis;
  const type = sportMeta(metrics.sport);
  const timerTime = metrics.timerTime;
  const ascent = sessionNumber(session.totalAscent);
  const calories = Number(session.totalCalories);
  setIcon(elements.activity_summary_icon, type.icon);
  elements.activity_summary_title.textContent = `这次${type.zh}`;
  elements.activity_profile_heading.textContent = `${type.zh}画像`;
  elements.activity_profile_label.textContent = `${type.english} PROFILE`;
  elements.metric_distance.textContent = (totalDistance / 1000).toFixed(2);
  elements.metric_duration.textContent = timerTime == null ? '未记录' : formatClock(timerTime);
  if (type.key === 'cycling') {
    elements.metric_speed_label.textContent = '平均速度';
    setIcon(elements.metric_speed_icon, 'ph-gauge');
    elements.metric_speed.innerHTML = metricMarkup(metrics.averageSpeed, 'km/h', 1);
  } else {
    elements.metric_speed_label.textContent = '平均配速';
    setIcon(elements.metric_speed_icon, 'ph-timer');
    elements.metric_speed.innerHTML = metrics.averagePaceSeconds == null ? '未记录' : `${formatPace(metrics.averagePaceSeconds)} <small>/km</small>`;
  }
  elements.metric_ascent.innerHTML = `${Math.round(ascent)} <small>m</small>`;
  elements.metric_calories_card.hidden = !(Number.isFinite(calories) && calories > 0);
  elements.metric_calories.innerHTML = metricMarkup(calories, 'kcal', 0);
  if (type.key === 'cycling') {
    elements.metric_max_label.textContent = '最高速度';
    setIcon(elements.metric_max_icon, 'ph-speedometer');
    elements.metric_max_speed.innerHTML = metricMarkup(metrics.maxSpeed, 'km/h', 1);
  } else {
    elements.metric_max_label.textContent = '最高海拔';
    setIcon(elements.metric_max_icon, 'ph-mountains');
    elements.metric_max_speed.innerHTML = metricMarkup(metrics.maxAltitude, 'm', 0);
  }
  const cadenceRelevant = type.key === 'cycling' || type.key === 'running' || metrics.effectiveCadence != null;
  elements.metric_cadence_card.hidden = !cadenceRelevant;
  elements.metric_cadence_label.textContent = `有效${type.cadence}`;
  setIcon(elements.metric_cadence_icon, type.icon);
  elements.metric_cadence.innerHTML = metricMarkup(metrics.effectiveCadence, type.key === 'running' ? 'spm' : 'rpm', 0);
  elements.timeline_duration.textContent = timerTime == null ? '空间轨迹' : formatClock(timerTime);
  elements.activity_title.textContent = payload.title || buildActivityTitle(session.startTime, totalDistance, metrics.sport);
  elements.activity_kicker.textContent = `${type.english} · ${formatActivityDate(session.startTime)}`;
  elements.activity_source.textContent = payload.metadata?.provider
    ? `${payload.metadata.provider} · ${String(payload.format).toUpperCase()}`
    : payload.source.includes('MAGENE') ? 'MAGENE C606V2' : payload.source.slice(0, 24);
  elements.activity_coordinate.textContent = `${Math.abs(first.lat).toFixed(3)}° ${first.lat >= 0 ? 'N' : 'S'} · ${Math.abs(first.lon).toFixed(3)}° ${first.lon >= 0 ? 'E' : 'W'}`;
  updateAnalysis(payload);
}

function frameUpdate(progress, record, activePhoto) {
  if (!record || !activity) return;
  const totalSeconds = sessionNumber(activity.session.totalTimerTime, activity.records.at(-1)?.elapsedTime);
  elements.live_distance.textContent = (sessionNumber(record.distance) / 1000).toFixed(2);
  const type = sportMeta(activity.session.sport);
  if (type.key === 'hiking' && !currentAnalysis?.metrics.hasSpeedData) {
    elements.live_secondary.textContent = Math.round(sessionNumber(record.altitude));
    elements.live_secondary_unit.textContent = 'M ALT';
  } else if (type.key === 'running') {
    const currentPace = Number(record.speed) > 0 ? 3600 / Number(record.speed) : null;
    elements.live_secondary.textContent = formatPace(currentPace);
    elements.live_secondary_unit.textContent = '/KM';
  } else {
    elements.live_secondary.textContent = Number(record.speed) > 0 ? Number(record.speed).toFixed(1) : '—';
    elements.live_secondary_unit.textContent = 'KM/H';
  }
  elements.timeline_time.textContent = currentAnalysis?.metrics.hasTimeData ? formatClock(progress * totalSeconds) : `${Math.round(progress * 100)}%`;
  if (!progressIsDragging) elements.progress_input.value = Math.round(progress * 1000);
  elements.progress_input.style.setProperty('--progress', `${progress * 100}%`);

  if (activePhoto !== currentPhoto) {
    currentPhoto = activePhoto;
    if (!activePhoto) {
      elements.photo_story.hidden = true;
    } else {
      const index = photos.indexOf(activePhoto);
      elements.photo_current.textContent = String(index + 1).padStart(2, '0');
      elements.photo_total.textContent = String(photos.length).padStart(2, '0');
      elements.photo_preview.src = activePhoto.url;
      elements.photo_title.textContent = activePhoto.label;
      elements.photo_meta.textContent = `${activePhoto.method} · 约 ${(activePhoto.progress * sessionNumber(activity.session.totalDistance) / 1000).toFixed(1)} km`;
      elements.photo_story.hidden = false;
    }
  }
}

const routeScene = new RouteScene(elements.route_canvas, frameUpdate);
const exportComposer = new ExportComposer(elements.export_view, showToast);

async function setActivity(payload, successMessage) {
  activity = payload;
  renderLocationContext(null);
  routeScene.setRoute(payload);
  updateSummary(payload);
  exportComposer.setActivity(payload);
  exportComposer.setPhotos([]);
  releasePhotos(photos);
  photos = [];
  currentPhoto = null;
  selectedPhoto = null;
  buildPhotoRouteMap();
  elements.photo_list.replaceChildren();
  elements.photo_count.textContent = '0 张';
  elements.photo_route_editor.hidden = true;
  elements.photo_story.hidden = true;
  elements.stage_loader.classList.add('is-hidden');
  if (successMessage) showToast(successMessage, 'success');
}

async function handleActivityFile(file) {
  if (!file) return false;
  elements.stage_loader.classList.remove('is-hidden');
  elements.stage_loader.querySelector('span').textContent = `正在解析 ${file.name.toLowerCase().endsWith('.kml') ? 'KML' : 'FIT'} 轨迹`;
  try {
    const payload = await parseActivityFile(file);
    await setActivity(payload, `已读取 ${payload.records.length.toLocaleString()} 个 GPS 轨迹点`);
    return true;
  } catch (error) {
    console.error(error);
    elements.stage_loader.classList.add('is-hidden');
    showToast(error.message || '轨迹文件解析失败', 'error');
    return false;
  }
}

async function loadInitialActivity() {
  if (trackResource) {
    const file = await fetchActivityFile(trackResource, pageParameters.get('name') || '');
    if (!await handleActivityFile(file)) throw new Error('URL 中的轨迹无法解析');
    return;
  }
  await setActivity(await loadBundledSample());
}

function photoDistanceLabel(photo) {
  const totalDistance = sessionNumber(activity?.session.totalDistance, activity?.records.at(-1)?.distance);
  return `${(photo.progress * totalDistance / 1000).toFixed(1)} km`;
}

function buildPhotoRouteMap() {
  const records = activity?.records ?? [];
  if (!records.length) {
    photoRoutePoints = [];
    elements.photo_route_path.setAttribute('d', '');
    elements.photo_route_map.querySelector('.photo-route-shadow').setAttribute('d', '');
    return;
  }
  const maxPoints = 420;
  const stride = Math.max(1, Math.ceil(records.length / maxPoints));
  const indices = [];
  for (let index = 0; index < records.length; index += stride) indices.push(index);
  if (indices.at(-1) !== records.length - 1) indices.push(records.length - 1);
  const latitudeCenter = records.reduce((sum, record) => sum + record.lat, 0) / records.length;
  const longitudeScale = Math.max(0.12, Math.cos(latitudeCenter * Math.PI / 180));
  const rawPoints = indices.map((index) => ({
    x: records[index].lon * longitudeScale,
    y: -records[index].lat,
    progress: index / Math.max(1, records.length - 1),
  }));
  const minX = Math.min(...rawPoints.map((point) => point.x));
  const maxX = Math.max(...rawPoints.map((point) => point.x));
  const minY = Math.min(...rawPoints.map((point) => point.y));
  const maxY = Math.max(...rawPoints.map((point) => point.y));
  const width = 320;
  const height = 180;
  const padding = 14;
  const scale = Math.min(
    (width - padding * 2) / Math.max(maxX - minX, 1e-9),
    (height - padding * 2) / Math.max(maxY - minY, 1e-9),
  );
  const drawnWidth = (maxX - minX) * scale;
  const drawnHeight = (maxY - minY) * scale;
  const offsetX = (width - drawnWidth) / 2;
  const offsetY = (height - drawnHeight) / 2;
  photoRoutePoints = rawPoints.map((point) => ({
    x: offsetX + (point.x - minX) * scale,
    y: offsetY + (point.y - minY) * scale,
    progress: point.progress,
  }));
  const pathData = photoRoutePoints.map((point, index) => `${index ? 'L' : 'M'} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`).join(' ');
  elements.photo_route_path.setAttribute('d', pathData);
  elements.photo_route_map.querySelector('.photo-route-shadow').setAttribute('d', pathData);
}

function routePointAt(progress) {
  if (!photoRoutePoints.length) return null;
  return photoRoutePoints.reduce((nearest, point) => (
    Math.abs(point.progress - progress) < Math.abs(nearest.progress - progress) ? point : nearest
  ));
}

function renderPhotoRouteMarkers() {
  const namespace = 'http://www.w3.org/2000/svg';
  elements.photo_route_markers.replaceChildren();
  photos.forEach((photo, index) => {
    const point = routePointAt(photo.progress);
    if (!point) return;
    const marker = document.createElementNS(namespace, 'circle');
    marker.setAttribute('cx', point.x);
    marker.setAttribute('cy', point.y);
    marker.setAttribute('r', photo === selectedPhoto ? '6' : photo.isCover ? '5' : '4');
    marker.setAttribute('class', `photo-route-marker${photo.isCover ? ' is-cover' : ''}${photo === selectedPhoto ? ' is-selected' : ''}`);
    marker.setAttribute('aria-label', `${index + 1}. ${photo.label}`);
    const title = document.createElementNS(namespace, 'title');
    title.textContent = `${photo.isCover ? '封面 · ' : ''}${photo.label} · ${photoDistanceLabel(photo)}`;
    marker.append(title);
    elements.photo_route_markers.append(marker);
  });
}

function createPhotoListItem(photo, index) {
  const item = document.createElement('button');
  item.type = 'button';
  item.className = `photo-list-item${photo === selectedPhoto ? ' is-selected' : ''}`;
  item.setAttribute('aria-pressed', String(photo === selectedPhoto));
  const image = document.createElement('img');
  image.src = photo.url;
  image.alt = photo.label;
  const copy = document.createElement('span');
  const title = document.createElement('strong');
  title.textContent = `${String(index + 1).padStart(2, '0')} · ${photo.label}`;
  const meta = document.createElement('small');
  meta.textContent = `${photo.method} · ${photoDistanceLabel(photo)}`;
  copy.append(title, meta);
  item.append(image, copy);
  if (photo.isCover) {
    const badge = document.createElement('em');
    badge.className = 'photo-cover-badge';
    badge.textContent = '封面';
    item.append(badge);
  }
  item.addEventListener('click', () => selectPhoto(photo));
  return item;
}

function renderPhotoBindingUI() {
  elements.photo_route_editor.hidden = !photos.length;
  elements.photo_count.textContent = `${photos.length} 张`;
  elements.photo_list.replaceChildren(...photos.map(createPhotoListItem));
  if (!selectedPhoto) {
    elements.photo_route_selection.textContent = '请选择一张照片';
    elements.photo_route_status.textContent = '先选择下方照片，再点击路线上的位置；也可以使用 GPS 或拍摄时间自动匹配。';
    elements.photo_auto_match.disabled = true;
    elements.photo_set_cover.disabled = true;
  } else {
    elements.photo_route_selection.textContent = selectedPhoto.label;
    elements.photo_route_status.textContent = `${selectedPhoto.method} · 约 ${photoDistanceLabel(selectedPhoto)}；点击上方路线可重新绑定。`;
    elements.photo_auto_match.disabled = false;
    elements.photo_set_cover.disabled = false;
    elements.photo_set_cover.classList.toggle('is-active', selectedPhoto.isCover);
    elements.photo_set_cover.innerHTML = selectedPhoto.isCover
      ? '<i class="ph ph-check" aria-hidden="true"></i>当前封面'
      : '<i class="ph ph-image" aria-hidden="true"></i>设为封面';
  }
  renderPhotoRouteMarkers();
}

function syncPhotoBindings({ activateExport = false } = {}) {
  routeScene.clearPhotos();
  photos.forEach((photo) => routeScene.addPhoto(photo));
  currentPhoto = null;
  exportComposer.setPhotos(photos, { activate: activateExport });
  renderPhotoBindingUI();
}

function selectPhoto(photo) {
  selectedPhoto = photo;
  routeScene.setProgress(Math.max(0, photo.progress - 0.012));
  routeScene.playing = false;
  elements.play_button.classList.add('is-paused');
  elements.play_button.setAttribute('aria-label', '播放动画');
  renderPhotoBindingUI();
}

async function handlePhotos(fileList) {
  if (!fileList?.length) return;
  if (!activity) {
    showToast('请先打开一份 FIT 或 KML 轨迹', 'error');
    return;
  }
  elements.photo_drop.classList.add('is-loading');
  try {
    const availableSlots = Math.max(0, 12 - photos.length);
    if (!availableSlots) throw new Error('最多可添加 12 张沿途照片');
    const nextPhotos = await preparePhotos([...fileList].slice(0, availableSlots), routeScene);
    if (!nextPhotos.length) throw new Error('没有找到可读取的图片');
    photos = [...photos, ...nextPhotos];
    if (!photos.some((photo) => photo.isCover)) photos[0].isCover = true;
    selectedPhoto = nextPhotos[0];
    syncPhotoBindings({ activateExport: true });
    routeScene.setProgress(Math.max(0, selectedPhoto.progress - 0.02));
    showToast(`已添加 ${nextPhotos.length} 张照片，可在 2D 路线上调整位置`, 'success');
  } catch (error) {
    console.error(error);
    showToast(error.message || '照片读取失败', 'error');
  } finally {
    elements.photo_drop.classList.remove('is-loading');
    elements.photo_input.value = '';
  }
}

function setMode(mode) {
  if (mode === currentMode) return;
  const exportMode = mode === 'export';

  if (exportMode) {
    analysisPlayingBeforeExport = routeScene.playing;
    routeScene.playing = false;
    exportComposer.show();
  } else {
    exportComposer.pause();
    routeScene.playing = analysisPlayingBeforeExport;
    requestAnimationFrame(() => routeScene.resize());
  }

  currentMode = mode;
  document.getElementById('app').dataset.mode = mode;
  elements.analysis_view.hidden = exportMode;
  elements.export_view.hidden = !exportMode;
  elements.analysis_mode_button.classList.toggle('is-active', !exportMode);
  elements.export_mode_button.classList.toggle('is-active', exportMode);
  elements.analysis_mode_button.setAttribute('aria-pressed', String(!exportMode));
  elements.export_mode_button.setAttribute('aria-pressed', String(exportMode));
  elements.analysis_mode_button.setAttribute('aria-selected', String(!exportMode));
  elements.export_mode_button.setAttribute('aria-selected', String(exportMode));
  elements.export_button.innerHTML = exportMode
    ? '<i class="ph ph-chart-line-up" aria-hidden="true"></i>返回分析'
    : '<i class="ph ph-export" aria-hidden="true"></i>导出创作';
}

elements.fit_input.addEventListener('change', (event) => handleActivityFile(event.target.files?.[0]));
elements.photo_input.addEventListener('change', (event) => handlePhotos(event.target.files));
elements.photo_drop.addEventListener('click', () => elements.photo_input.click());
elements.photo_route_map.addEventListener('click', (event) => {
  if (!selectedPhoto || !photoRoutePoints.length) {
    showToast('请先选择一张照片', 'error');
    return;
  }
  const bounds = elements.photo_route_map.getBoundingClientRect();
  const pointer = {
    x: (event.clientX - bounds.left) / Math.max(1, bounds.width) * 320,
    y: (event.clientY - bounds.top) / Math.max(1, bounds.height) * 180,
  };
  const nearest = photoRoutePoints.reduce((best, point) => {
    const distance = (point.x - pointer.x) ** 2 + (point.y - pointer.y) ** 2;
    return distance < best.distance ? { point, distance } : best;
  }, { point: photoRoutePoints[0], distance: Infinity }).point;
  selectedPhoto.progress = nearest.progress;
  selectedPhoto.method = '手动选点';
  syncPhotoBindings();
  routeScene.setProgress(Math.max(0, selectedPhoto.progress - 0.012));
  showToast(`已把 ${selectedPhoto.label} 绑定到 ${photoDistanceLabel(selectedPhoto)}`, 'success');
});
elements.photo_auto_match.addEventListener('click', () => {
  if (!selectedPhoto) return;
  selectedPhoto.progress = selectedPhoto.automaticProgress;
  selectedPhoto.method = selectedPhoto.automaticMethod;
  syncPhotoBindings();
  routeScene.setProgress(Math.max(0, selectedPhoto.progress - 0.012));
  showToast(`已按${selectedPhoto.method}重新匹配`, 'success');
});
elements.photo_set_cover.addEventListener('click', () => {
  if (!selectedPhoto) return;
  photos.forEach((photo) => { photo.isCover = photo === selectedPhoto; });
  syncPhotoBindings();
  showToast(`已将 ${selectedPhoto.label} 设为封面`, 'success');
});
elements.analysis_mode_button.addEventListener('click', () => setMode('analysis'));
elements.export_mode_button.addEventListener('click', () => setMode('export'));
elements.export_button.addEventListener('click', () => setMode(currentMode === 'export' ? 'analysis' : 'export'));
document.querySelector('.brand').addEventListener('click', (event) => {
  event.preventDefault();
  setMode('analysis');
});

elements.play_button.addEventListener('click', () => {
  routeScene.playing = !routeScene.playing;
  elements.play_button.classList.toggle('is-paused', !routeScene.playing);
  elements.play_button.setAttribute('aria-label', routeScene.playing ? '暂停动画' : '播放动画');
});

elements.spin_button.addEventListener('click', () => {
  routeScene.spinning = !routeScene.spinning;
  elements.spin_button.classList.toggle('is-active', routeScene.spinning);
  elements.spin_button.setAttribute('aria-pressed', String(routeScene.spinning));
});

elements.reset_button.addEventListener('click', () => routeScene.resetCamera());

elements.progress_input.addEventListener('pointerdown', () => { progressIsDragging = true; });
elements.progress_input.addEventListener('input', (event) => {
  routeScene.setProgress(Number(event.target.value) / 1000);
  elements.progress_input.style.setProperty('--progress', `${Number(event.target.value) / 10}%`);
});
window.addEventListener('pointerup', () => { progressIsDragging = false; });

window.addEventListener('resize', () => {
  cancelAnimationFrame(chartResizeFrame);
  chartResizeFrame = requestAnimationFrame(() => {
    if (activity) drawAnalysisChart(activity.records);
  });
});

if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  routeScene.playing = false;
  routeScene.spinning = false;
  elements.play_button.classList.add('is-paused');
  elements.play_button.setAttribute('aria-label', '播放动画');
  elements.spin_button.classList.remove('is-active');
  elements.spin_button.setAttribute('aria-pressed', 'false');
}

for (const eventName of ['dragenter', 'dragover']) {
  window.addEventListener(eventName, (event) => {
    event.preventDefault();
    elements.share_stage.classList.add('is-dragging');
  });
}
for (const eventName of ['dragleave', 'drop']) {
  window.addEventListener(eventName, (event) => {
    event.preventDefault();
    elements.share_stage.classList.remove('is-dragging');
  });
}
window.addEventListener('drop', (event) => {
  const dropped = [...(event.dataTransfer?.files ?? [])];
  const track = dropped.find((file) => /\.(fit|kml)$/i.test(file.name));
  const images = dropped.filter((file) => file.type.startsWith('image/'));
  if (track) handleActivityFile(track);
  else if (images.length) handlePhotos(images);
});

loadInitialActivity()
  .catch((error) => {
    console.error(error);
    elements.stage_loader.querySelector('span').textContent = trackResource
      ? '自动轨迹加载失败，请检查临时链接或手动打开 FIT / KML'
      : '示例路线加载失败，请打开 FIT 或 KML 文件';
    showToast(trackResource ? '自动轨迹加载失败' : '示例路线加载失败', 'error');
  });
