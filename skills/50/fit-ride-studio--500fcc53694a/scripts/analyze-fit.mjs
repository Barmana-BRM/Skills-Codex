#!/usr/bin/env node

import { access, readFile, readdir, stat } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const VERSION = 1;
const finite = (value) => value != null && value !== '' && Number.isFinite(Number(value));
const numeric = (value, fallback = null) => finite(value) ? Number(value) : fallback;
const positive = (value) => finite(value) && Number(value) > 0;
const round = (value, digits = 1) => value == null ? null : Number(Number(value).toFixed(digits));
const percent = (count, total) => total > 0 ? count / total * 100 : 0;
const mean = (values) => values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null;
const weightedMean = (pairs) => {
  const valid = pairs.filter(({ value, weight }) => finite(value) && Number(weight) > 0);
  const weight = valid.reduce((sum, item) => sum + Number(item.weight), 0);
  return weight ? valid.reduce((sum, item) => sum + Number(item.value) * Number(item.weight), 0) / weight : null;
};
let analyzeActivity;
let parseActivityFile;

function formatClock(seconds) {
  const safe = Math.max(0, Math.round(Number(seconds) || 0));
  const hours = Math.floor(safe / 3600);
  const minutes = Math.floor((safe % 3600) / 60);
  const remainder = safe % 60;
  if (hours) return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(remainder).padStart(2, '0')}`;
  return `${String(minutes).padStart(2, '0')}:${String(remainder).padStart(2, '0')}`;
}

function usage() {
  return `Usage: node analyze-fit.mjs [--app-root <ride-relief-dir>] [--format json|markdown] [--keep-duplicates] <file.fit|file.kml|directory> [...more]\n\nThe default format is markdown. Directories expand top-level FIT and KML files.\nLikely duplicates are excluded unless --keep-duplicates is set.`;
}

function parseArguments(argv) {
  let format = 'markdown';
  let keepDuplicates = false;
  let appRoot = null;
  const inputs = [];
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === '--help' || argument === '-h') return { help: true, format, keepDuplicates, inputs };
    if (argument === '--keep-duplicates') {
      keepDuplicates = true;
      continue;
    }
    if (argument === '--app-root') {
      appRoot = argv[index + 1];
      index += 1;
      continue;
    }
    if (argument.startsWith('--app-root=')) {
      appRoot = argument.slice('--app-root='.length);
      continue;
    }
    if (argument === '--format') {
      format = argv[index + 1];
      index += 1;
      continue;
    }
    if (argument.startsWith('--format=')) {
      format = argument.slice('--format='.length);
      continue;
    }
    if (argument.startsWith('-')) throw new Error(`Unknown option: ${argument}`);
    inputs.push(argument);
  }
  if (!['json', 'markdown'].includes(format)) throw new Error('--format must be json or markdown');
  return { help: false, format, keepDuplicates, appRoot, inputs };
}

async function isRideReliefRoot(candidate) {
  if (!candidate) return false;
  try {
    const packageJson = JSON.parse(await readFile(path.join(candidate, 'package.json'), 'utf8'));
    await access(path.join(candidate, 'src', 'data.js'));
    return packageJson.name === 'ride-relief';
  } catch {
    return false;
  }
}

async function findAppRoot(explicitRoot) {
  const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
  const candidates = [
    explicitRoot && path.resolve(explicitRoot),
    process.env.RIDE_RELIEF_ROOT && path.resolve(process.env.RIDE_RELIEF_ROOT),
    path.resolve(scriptDirectory, '../../..'),
  ].filter(Boolean);
  let cursor = path.resolve(process.cwd());
  while (true) {
    candidates.push(cursor);
    const parent = path.dirname(cursor);
    if (parent === cursor) break;
    cursor = parent;
  }
  for (const candidate of [...new Set(candidates)]) {
    if (await isRideReliefRoot(candidate)) return candidate;
  }
  throw new Error('Ride Relief app root not found. Run from the project or pass --app-root <directory>.');
}

async function loadApplicationAnalyzer(appRoot) {
  const moduleUrl = pathToFileURL(path.join(appRoot, 'src', 'data.js')).href;
  const application = await import(moduleUrl);
  analyzeActivity = application.analyzeActivity;
  parseActivityFile = application.parseActivityFile;
  if (typeof analyzeActivity !== 'function' || typeof parseActivityFile !== 'function') {
    throw new Error('Ride Relief src/data.js does not expose the expected analyzer functions.');
  }
}

async function expandInputs(inputs) {
  const files = [];
  for (const input of inputs) {
    const resolved = path.resolve(input);
    const details = await stat(resolved);
    if (details.isDirectory()) {
      const entries = await readdir(resolved, { withFileTypes: true });
      files.push(...entries
        .filter((entry) => entry.isFile() && /\.(fit|kml)$/i.test(entry.name))
        .map((entry) => path.join(resolved, entry.name))
        .sort((a, b) => a.localeCompare(b)));
    } else if (details.isFile() && /\.(fit|kml)$/i.test(resolved)) {
      files.push(resolved);
    } else {
      throw new Error(`Not a FIT/KML file or directory: ${input}`);
    }
  }
  return files;
}

function validValues(records, selector, allowZero = false) {
  return records
    .map(selector)
    .filter((value) => value != null && value !== '')
    .map(Number)
    .filter((value) => Number.isFinite(value) && (allowZero || value > 0));
}

async function parseRide(filePath) {
  const bytes = await readFile(filePath);
  const file = {
    name: path.basename(filePath),
    type: filePath.toLowerCase().endsWith('.kml') ? 'application/vnd.google-earth.kml+xml' : 'application/octet-stream',
    arrayBuffer: async () => bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
  };
  const payload = await parseActivityFile(file);
  const analysis = analyzeActivity(payload);
  const { session, records } = payload;
  const last = records.at(-1);
  const cadenceValues = validValues(records, (record) => record.cadence);
  const heartRateValues = validValues(records, (record) => record.heartRate ?? record.heart_rate);
  const powerValues = validValues(records, (record) => record.power);
  const temperatureValues = validValues(records, (record) => record.temperature, true);
  const gradeValues = validValues(records, (record) => record.grade, true);
  const movingSeconds = numeric(session.totalTimerTime, numeric(last?.elapsedTime, null));
  const elapsedSeconds = numeric(session.totalElapsedTime, movingSeconds);
  const distanceMeters = numeric(session.totalDistance, numeric(last?.distance, 0));
  const avgSpeedKmh = positive(session.avgSpeed)
    ? Number(session.avgSpeed)
    : movingSeconds > 0 ? distanceMeters / movingSeconds * 3.6 : null;
  const maxSpeedKmh = positive(session.maxSpeed)
    ? Number(session.maxSpeed)
    : analysis.metrics.maxSpeed;
  const calories = positive(session.totalCalories) ? Number(session.totalCalories) : null;
  const totalAscentMeters = numeric(session.totalAscent, 0);
  const totalDescentMeters = numeric(session.totalDescent, null);

  return {
    source: path.basename(filePath),
    startTime: session.startTime || records[0]?.timestamp || null,
    sport: session.sport || 'cycling',
    summary: {
      distanceMeters,
      movingSeconds,
      elapsedSeconds,
      hasTimeData: analysis.metrics.hasTimeData,
      pauseSeconds: elapsedSeconds == null || movingSeconds == null ? null : Math.max(0, elapsedSeconds - movingSeconds),
      movingRatioPercent: round(analysis.metrics.movingRatio, 1),
      avgSpeedKmh: round(avgSpeedKmh, 2),
      avgPaceSecondsPerKm: round(analysis.metrics.averagePaceSeconds, 1),
      maxSpeedKmh: round(maxSpeedKmh, 2),
      totalAscentMeters: round(totalAscentMeters, 0),
      totalDescentMeters: round(totalDescentMeters, 0),
      minAltitudeMeters: round(analysis.metrics.minAltitude, 0),
      maxAltitudeMeters: round(analysis.metrics.maxAltitude, 0),
      calories: round(calories, 0),
      effectiveCadenceRpm: round(analysis.metrics.effectiveCadence, 1),
      maxCadenceRpm: round(analysis.metrics.maxCadence, 0),
      avgHeartRateBpm: round(analysis.metrics.averageHeartRate, 0),
      maxHeartRateBpm: round(analysis.metrics.maxHeartRate, 0),
      avgPowerWatts: round(analysis.metrics.averagePower, 0),
      maxPowerWatts: round(analysis.metrics.maxPower, 0),
      avgTemperatureCelsius: round(analysis.metrics.averageTemperature, 1),
      maxGradePercent: round(analysis.metrics.maxGrade, 1),
      representativeGradePercent: round(analysis.metrics.representativeGrade, 1),
      gradeAnalyzedDistanceMeters: round(analysis.metrics.gradeAnalyzedDistance, 0),
      ascentDensityMetersPerKm: round(analysis.metrics.ascentDensity, 1),
      routeGapMeters: round(analysis.metrics.routeGap, 0),
      isLoop: Boolean(analysis.metrics.isLoop),
      profileTitle: analysis.profile.title,
      profileDescription: analysis.profile.description,
    },
    dataQuality: {
      gpsRecordCount: records.length,
      cadenceSamples: cadenceValues.length,
      cadenceCoveragePercent: round(percent(cadenceValues.length, records.length), 1),
      heartRateSamples: heartRateValues.length,
      heartRateCoveragePercent: round(percent(heartRateValues.length, records.length), 1),
      powerSamples: powerValues.length,
      powerCoveragePercent: round(percent(powerValues.length, records.length), 1),
      temperatureSamples: temperatureValues.length,
      temperatureCoveragePercent: round(percent(temperatureValues.length, records.length), 1),
      gradeSamples: gradeValues.length,
      gradeCoveragePercent: round(percent(gradeValues.length, records.length), 1),
    },
    distributions: {
      speedPercent: analysis.metrics.pace
        ? Object.fromEntries(Object.entries(analysis.metrics.pace).map(([key, value]) => [key, round(value, 1)]))
        : null,
      cadencePercent: cadenceValues.length
        ? Object.fromEntries(Object.entries(analysis.metrics.cadence).map(([key, value]) => [key, round(value, 1)]))
        : null,
      gradePercent: analysis.metrics.grade
        ? Object.fromEntries(Object.entries(analysis.metrics.grade).map(([key, value]) => [key, round(value, 1)]))
        : null,
    },
    climbs: analysis.metrics.climbs.map((climb) => ({
      startDistanceMeters: round(climb.startDistanceMeters, 0),
      distanceMeters: round(climb.distanceMeters, 0),
      elevationGainMeters: round(climb.elevationGainMeters, 0),
      averageGradePercent: round(climb.averageGradePercent, 1),
      maxGradePercent: round(climb.maxGradePercent, 1),
    })),
    recommendations: analysis.recommendations,
  };
}

function duplicateKey(ride) {
  const timestamp = ride.startTime ? new Date(ride.startTime).getTime() : null;
  if (!Number.isFinite(timestamp) || ride.summary.movingSeconds == null) return `source:${ride.source}`;
  const start = Number.isFinite(timestamp) ? Math.round(timestamp / 1000) : 'unknown';
  return [ride.sport, start, Math.round(ride.summary.distanceMeters), Math.round(ride.summary.movingSeconds)].join(':');
}

function compactRide(ride) {
  return {
    source: ride.source,
    sport: ride.sport,
    startTime: ride.startTime,
    distanceMeters: ride.summary.distanceMeters,
    movingSeconds: ride.summary.movingSeconds,
    avgSpeedKmh: ride.summary.avgSpeedKmh,
    maxSpeedKmh: ride.summary.maxSpeedKmh,
    totalAscentMeters: ride.summary.totalAscentMeters,
    calories: ride.summary.calories,
    effectiveCadenceRpm: ride.summary.effectiveCadenceRpm,
    avgHeartRateBpm: ride.summary.avgHeartRateBpm,
    avgPowerWatts: ride.summary.avgPowerWatts,
    cadenceCoveragePercent: ride.dataQuality.cadenceCoveragePercent,
    heartRateCoveragePercent: ride.dataQuality.heartRateCoveragePercent,
    powerCoveragePercent: ride.dataQuality.powerCoveragePercent,
    gradeCoveragePercent: ride.dataQuality.gradeCoveragePercent,
    representativeGradePercent: ride.summary.representativeGradePercent,
    keyClimbCount: ride.climbs.length,
  };
}

function delta(latest, earliest, key, digits = 1) {
  const latestValue = numeric(latest.summary[key]);
  const earliestValue = numeric(earliest.summary[key]);
  return latestValue == null || earliestValue == null ? null : round(latestValue - earliestValue, digits);
}

function buildAggregate(rides, duplicates, failed) {
  const sorted = [...rides].sort((a, b) => {
    const left = a.startTime ? new Date(a.startTime).getTime() : 0;
    const right = b.startTime ? new Date(b.startTime).getTime() : 0;
    return left - right;
  });
  const totalDistanceMeters = rides.reduce((sum, ride) => sum + ride.summary.distanceMeters, 0);
  const timedRides = rides.filter((ride) => ride.summary.movingSeconds != null);
  const totalMovingSeconds = timedRides.reduce((sum, ride) => sum + ride.summary.movingSeconds, 0);
  const totalElapsedSeconds = timedRides.reduce((sum, ride) => sum + (ride.summary.elapsedSeconds ?? ride.summary.movingSeconds), 0);
  const timedDistanceMeters = timedRides.reduce((sum, ride) => sum + ride.summary.distanceMeters, 0);
  const totalAscentMeters = rides.reduce((sum, ride) => sum + (ride.summary.totalAscentMeters || 0), 0);
  const knownCalories = rides.filter((ride) => ride.summary.calories != null);
  const totalRecords = rides.reduce((sum, ride) => sum + ride.dataQuality.gpsRecordCount, 0);
  const sampleTotal = (key) => rides.reduce((sum, ride) => sum + ride.dataQuality[key], 0);
  const longest = rides.reduce((best, ride) => ride.summary.distanceMeters > best.summary.distanceMeters ? ride : best);
  const fastest = rides.reduce((best, ride) => (ride.summary.avgSpeedKmh || 0) > (best.summary.avgSpeedKmh || 0) ? ride : best);
  const climbing = rides.reduce((best, ride) => (ride.summary.totalAscentMeters || 0) > (best.summary.totalAscentMeters || 0) ? ride : best);
  const earliest = sorted[0];
  const latest = sorted.at(-1);
  const ridesWith = (key) => rides.filter((ride) => ride.dataQuality[key] > 0).length;
  const maxGradeValues = rides.map((ride) => ride.summary.maxGradePercent).filter(finite);
  const representativeGradeValues = rides.map((ride) => ride.summary.representativeGradePercent).filter(finite);
  const sportCounts = Object.fromEntries([...new Set(rides.map((ride) => ride.sport))].map((sport) => [sport, rides.filter((ride) => ride.sport === sport).length]));
  const aggregate = {
    schemaVersion: VERSION,
    mode: 'aggregate',
    summary: {
      rideCount: rides.length,
      sportCounts,
      timeDataRideCount: timedRides.length,
      dateFrom: earliest?.startTime || null,
      dateTo: latest?.startTime || null,
      totalDistanceMeters,
      totalMovingSeconds: timedRides.length ? totalMovingSeconds : null,
      totalElapsedSeconds: timedRides.length ? totalElapsedSeconds : null,
      totalPauseSeconds: timedRides.length ? Math.max(0, totalElapsedSeconds - totalMovingSeconds) : null,
      avgSpeedKmh: totalMovingSeconds > 0 ? round(timedDistanceMeters / totalMovingSeconds * 3.6, 2) : null,
      maxSpeedKmh: round(Math.max(...rides.map((ride) => ride.summary.maxSpeedKmh || 0)), 2),
      totalAscentMeters: round(totalAscentMeters, 0),
      totalCaloriesKnown: round(knownCalories.reduce((sum, ride) => sum + ride.summary.calories, 0), 0),
      caloriesRideCoveragePercent: round(percent(knownCalories.length, rides.length), 1),
      effectiveCadenceRpm: round(weightedMean(rides.map((ride) => ({ value: ride.summary.effectiveCadenceRpm, weight: ride.dataQuality.cadenceSamples }))), 1),
      avgHeartRateBpm: round(weightedMean(rides.map((ride) => ({ value: ride.summary.avgHeartRateBpm, weight: ride.dataQuality.heartRateSamples }))), 0),
      avgPowerWatts: round(weightedMean(rides.map((ride) => ({ value: ride.summary.avgPowerWatts, weight: ride.dataQuality.powerSamples }))), 0),
      avgTemperatureCelsius: round(weightedMean(rides.map((ride) => ({ value: ride.summary.avgTemperatureCelsius, weight: ride.dataQuality.temperatureSamples }))), 1),
      cadenceCoveragePercent: round(percent(sampleTotal('cadenceSamples'), totalRecords), 1),
      heartRateCoveragePercent: round(percent(sampleTotal('heartRateSamples'), totalRecords), 1),
      powerCoveragePercent: round(percent(sampleTotal('powerSamples'), totalRecords), 1),
      temperatureCoveragePercent: round(percent(sampleTotal('temperatureSamples'), totalRecords), 1),
      gradeCoveragePercent: round(percent(sampleTotal('gradeSamples'), totalRecords), 1),
      maxGradePercent: maxGradeValues.length ? round(Math.max(...maxGradeValues), 1) : null,
      representativeGradePercent: representativeGradeValues.length ? round(Math.max(...representativeGradeValues), 1) : null,
      ridesWithCadence: ridesWith('cadenceSamples'),
      ridesWithHeartRate: ridesWith('heartRateSamples'),
      ridesWithPower: ridesWith('powerSamples'),
      ridesWithGrade: ridesWith('gradeSamples'),
    },
    rides: sorted.map(compactRide),
    bests: {
      longest: compactRide(longest),
      fastestAverage: compactRide(fastest),
      highestAscent: compactRide(climbing),
    },
    trend: rides.length > 1 ? {
      earliestSource: earliest.source,
      latestSource: latest.source,
      distanceMetersDelta: delta(latest, earliest, 'distanceMeters', 0),
      avgSpeedKmhDelta: delta(latest, earliest, 'avgSpeedKmh', 2),
      totalAscentMetersDelta: delta(latest, earliest, 'totalAscentMeters', 0),
      effectiveCadenceRpmDelta: delta(latest, earliest, 'effectiveCadenceRpm', 1),
    } : null,
    insights: [],
    duplicates,
    failed,
  };

  const summary = aggregate.summary;
  aggregate.insights.push({
    category: '总量',
    title: `${rides.length} 次活动，共 ${(totalDistanceMeters / 1000).toFixed(1)} km`,
    body: timedRides.length
      ? `其中 ${timedRides.length}/${rides.length} 次包含有效时间，累计移动 ${formatClock(totalMovingSeconds)}；全部活动累计爬升 ${Math.round(totalAscentMeters)} m。综合均速只使用具有时间轴的活动。`
      : `这些轨迹都没有有效时间轴；仍可汇总距离与爬升，但不会生成时长、配速或均速结论。全部活动累计爬升 ${Math.round(totalAscentMeters)} m。`,
  });
  const cadenceRelevantCount = rides.filter((ride) => ride.sport === 'cycling' || ride.sport === 'running').length;
  if (summary.ridesWithCadence) {
    aggregate.insights.push({
      category: '踏频',
      title: `${summary.ridesWithCadence}/${rides.length} 次包含踏频`,
      body: `有效踏频加权均值 ${Math.round(summary.effectiveCadenceRpm)} rpm，记录覆盖 ${Math.round(summary.cadenceCoveragePercent)}%。只在有效踩踏样本间比较，滑行与停车不作为低踏频。`,
    });
  } else if (cadenceRelevantCount) {
    aggregate.insights.push({
      category: '数据',
      title: '骑行或跑步记录没有可用踏频 / 步频',
      body: '路线、速度和爬升分析仍可正常使用；只有在技术节奏确实是目标时，才需要补充相应传感器。',
    });
  }
  if (cadenceRelevantCount && !summary.ridesWithHeartRate && !summary.ridesWithPower) {
    aggregate.insights.push({
      category: '数据',
      title: '缺少跨骑行的强度依据',
      body: '没有心率与功率时，不宜推断训练负荷或恢复状态。若要长期训练分析，稳定记录心率通常是更容易开始的一步。',
    });
  } else if (summary.ridesWithHeartRate < rides.length || summary.ridesWithPower < rides.length) {
    aggregate.insights.push({
      category: '一致性',
      title: '传感器覆盖在不同骑行间不一致',
      body: `心率覆盖 ${summary.ridesWithHeartRate}/${rides.length} 次，功率覆盖 ${summary.ridesWithPower}/${rides.length} 次。比较趋势时优先使用传感器条件相同的骑行。`,
    });
  }
  if (summary.ridesWithGrade) {
    aggregate.insights.push({
      category: '坡度',
      title: `${summary.ridesWithGrade}/${rides.length} 次包含可用坡度`,
      body: `单次骑行的代表性陡坡最高为 ${fmt(summary.representativeGradePercent, '%', 1)}。坡度区间按有效距离加权，避免慢速路段因采样更密而被夸大。`,
    });
  }
  const privacySensitive = rides.filter((ride) => ride.summary.isLoop && (ride.summary.routeGapMeters ?? Infinity) < 200);
  if (privacySensitive.length) {
    aggregate.insights.push({
      category: '隐私',
      title: `${privacySensitive.length} 次活动的起终点非常接近`,
      body: '公开分享路线前，建议隐藏或裁掉首尾 300–500 米，避免暴露住址或常用出发点。',
    });
  }
  if (duplicates.length || failed.length) {
    aggregate.insights.push({
      category: '质量',
      title: '已隔离重复或无法解析的文件',
      body: `重复 ${duplicates.length} 份、解析失败 ${failed.length} 份，均未进入综合统计。`,
    });
  }
  return aggregate;
}

function fmt(value, suffix = '', digits = 1) {
  return value == null ? '未记录' : `${Number(value).toFixed(digits)}${suffix}`;
}

function fmtDate(value) {
  if (!value) return '日期未知';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '日期未知' : new Intl.DateTimeFormat('zh-CN', {
    timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit',
  }).format(date);
}

function sportLabel(value) {
  return value === 'running' ? '跑步' : value === 'hiking' ? '徒步' : value === 'cycling' ? '骑行' : '户外活动';
}

function formatDuration(value) {
  return value == null ? '未记录' : formatClock(value);
}

function formatPace(value) {
  if (value == null) return '未记录';
  const seconds = Math.round(value);
  return `${Math.floor(seconds / 60)}'${String(seconds % 60).padStart(2, '0')}\"/km`;
}

function escapeCell(value) {
  return String(value ?? '—').replaceAll('|', '\\|').replaceAll('\n', ' ');
}

function renderSingle(report) {
  const { ride } = report;
  const summary = ride.summary;
  const quality = ride.dataQuality;
  const activityLabel = sportLabel(ride.sport);
  const cadenceLabel = ride.sport === 'cycling' ? '有效踏频' : '有效步频';
  const speedLabel = ride.sport === 'cycling'
    ? `${fmt(summary.avgSpeedKmh, '', 1)} / ${fmt(summary.maxSpeedKmh, ' km/h', 1)}`
    : `${formatPace(summary.avgPaceSecondsPerKm)} / 最高海拔 ${fmt(summary.maxAltitudeMeters, ' m', 0)}`;
  const lines = [
    `# 单次${activityLabel}轨迹分析：${ride.source}`,
    '',
    `**${summary.profileTitle}。** ${summary.profileDescription}`,
    '',
    '| 指标 | 结果 |',
    '| --- | ---: |',
    `| 日期 | ${fmtDate(ride.startTime)} |`,
    `| 距离 | ${fmt(summary.distanceMeters / 1000, ' km', 2)} |`,
    `| 移动时间 | ${formatDuration(summary.movingSeconds)} |`,
    `| ${ride.sport === 'cycling' ? '平均 / 最高速度' : '平均配速 / 最高海拔'} | ${speedLabel} |`,
    `| 累计爬升 | ${fmt(summary.totalAscentMeters, ' m', 0)} |`,
    `| 停留 / 移动占比 | ${formatDuration(summary.pauseSeconds)} / ${fmt(summary.movingRatioPercent, '%', 0)} |`,
    `| ${cadenceLabel} | ${fmt(summary.effectiveCadenceRpm, ride.sport === 'running' ? ' spm' : ' rpm', 0)} |`,
    `| 平均心率 | ${fmt(summary.avgHeartRateBpm, ' bpm', 0)} |`,
    `| 平均功率 | ${fmt(summary.avgPowerWatts, ' W', 0)} |`,
    `| 平均环境温度 | ${fmt(summary.avgTemperatureCelsius, ' °C', 0)} |`,
    `| 最高记录 / 代表性陡坡 | ${fmt(summary.maxGradePercent, '%', 1)} / ${fmt(summary.representativeGradePercent, '%（P99）', 1)} |`,
    `| 热量 | ${fmt(summary.calories, ' kcal', 0)} |`,
    '',
    '## 数据完整性',
    '',
    '| 数据 | 覆盖率 |',
    '| --- | ---: |',
    `| 时间轴 | ${summary.hasTimeData ? '已记录' : '未记录'} |`,
    `| ${ride.sport === 'cycling' ? '踏频' : '步频'} | ${fmt(quality.cadenceCoveragePercent, '%', 0)} |`,
    `| 心率 | ${fmt(quality.heartRateCoveragePercent, '%', 0)} |`,
    `| 功率 | ${fmt(quality.powerCoveragePercent, '%', 0)} |`,
    `| 坡度 | ${fmt(quality.gradeCoveragePercent, '%', 0)} |`,
    '',
    '## 坡度与主要爬坡',
    '',
  ];
  if (ride.distributions.gradePercent) {
    const grade = ride.distributions.gradePercent;
    lines.push(`按有效距离统计：下坡（<−3%）${fmt(grade.descent, '%', 1)}，平缓（−3–3%）${fmt(grade.flat, '%', 1)}，爬坡（3–6%）${fmt(grade.climb, '%', 1)}，陡坡（>6%）${fmt(grade.steep, '%', 1)}。`, '');
  } else {
    lines.push('坡度覆盖不足，未生成区间分布。', '');
  }
  if (ride.climbs.length) {
    lines.push('| 起点里程 | 长度 | 爬升 | 平均坡度 | 代表峰值 |', '| ---: | ---: | ---: | ---: | ---: |');
    for (const climb of ride.climbs) {
      lines.push(`| ${fmt(climb.startDistanceMeters / 1000, ' km', 1)} | ${fmt(climb.distanceMeters / 1000, ' km', 2)} | ${fmt(climb.elevationGainMeters, ' m', 0)} | ${fmt(climb.averageGradePercent, '%', 1)} | ${fmt(climb.maxGradePercent, '%', 1)} |`);
    }
    lines.push('');
  } else {
    lines.push('未识别出长度至少 200 m、平均坡度至少 2.5% 的连续爬坡。', '');
  }
  lines.push(
    '## 建议',
    '',
  );
  if (!ride.recommendations.length) lines.push('- 当前数据没有触发额外建议。');
  for (const item of ride.recommendations) {
    lines.push(`- **${item.category} · ${item.title}**：${item.body}`);
    for (const action of item.actions ?? []) lines.push(`  - ${action}`);
  }
  if (report.duplicates.length) {
    lines.push('', `重复文件（未计入）：${report.duplicates.map((item) => item.source).join('、')}`);
  }
  if (report.failed.length) {
    lines.push('', `解析失败（未计入）：${report.failed.map((item) => `${item.source}：${item.error}`).join('；')}`);
  }
  return lines.join('\n');
}

function renderAggregate(report) {
  const summary = report.summary;
  const lines = [
    `# ${summary.rideCount} 次运动轨迹综合分析`,
    '',
    `时间范围：${fmtDate(summary.dateFrom)} 至 ${fmtDate(summary.dateTo)}`,
    '',
    '| 综合指标 | 结果 |',
    '| --- | ---: |',
    `| 总里程 | ${fmt(summary.totalDistanceMeters / 1000, ' km', 1)} |`,
    `| 有时间轴的活动 | ${summary.timeDataRideCount} / ${summary.rideCount} |`,
    `| 总移动时间 | ${formatDuration(summary.totalMovingSeconds)} |`,
    `| 综合均速 | ${fmt(summary.avgSpeedKmh, ' km/h', 1)} |`,
    `| 最高速度 | ${fmt(summary.maxSpeedKmh, ' km/h', 1)} |`,
    `| 累计爬升 | ${fmt(summary.totalAscentMeters, ' m', 0)} |`,
    `| 最高代表性陡坡 | ${fmt(summary.representativeGradePercent, '%（P99）', 1)} |`,
    `| 有效踏频 | ${fmt(summary.effectiveCadenceRpm, ' rpm', 0)} |`,
    `| 平均心率 | ${fmt(summary.avgHeartRateBpm, ' bpm', 0)} |`,
    `| 平均功率 | ${fmt(summary.avgPowerWatts, ' W', 0)} |`,
    '',
    '## 每次活动',
    '',
    '| 日期 | 类型 | 文件 | 距离 | 移动时间 | 均速 | 爬升 | 踏频/步频 | 心率 | 功率 |',
    '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |',
  ];
  for (const ride of report.rides) {
    lines.push(`| ${fmtDate(ride.startTime)} | ${sportLabel(ride.sport)} | ${escapeCell(ride.source)} | ${fmt(ride.distanceMeters / 1000, ' km', 1)} | ${formatDuration(ride.movingSeconds)} | ${fmt(ride.avgSpeedKmh, ' km/h', 1)} | ${fmt(ride.totalAscentMeters, ' m', 0)} | ${fmt(ride.effectiveCadenceRpm, ride.sport === 'running' ? ' spm' : ' rpm', 0)} | ${fmt(ride.avgHeartRateBpm, ' bpm', 0)} | ${fmt(ride.avgPowerWatts, ' W', 0)} |`);
  }
  lines.push(
    '',
    '## 表现亮点',
    '',
    `- 最长：${report.bests.longest.source}（${fmt(report.bests.longest.distanceMeters / 1000, ' km', 1)}）`,
    `- 最快均速：${report.bests.fastestAverage.avgSpeedKmh == null ? '没有可比较的时间数据' : `${report.bests.fastestAverage.source}（${fmt(report.bests.fastestAverage.avgSpeedKmh, ' km/h', 1)}）`}`,
    `- 爬升最多：${report.bests.highestAscent.source}（${fmt(report.bests.highestAscent.totalAscentMeters, ' m', 0)}）`,
  );
  if (report.trend) {
    lines.push(
      '',
      '## 首次与最近一次对比',
      '',
      `由 ${report.trend.earliestSource} 到 ${report.trend.latestSource}：`,
      '',
      `- 距离变化：${fmt(report.trend.distanceMetersDelta == null ? null : report.trend.distanceMetersDelta / 1000, ' km', 1)}`,
      `- 均速变化：${fmt(report.trend.avgSpeedKmhDelta, ' km/h', 1)}`,
      `- 爬升变化：${fmt(report.trend.totalAscentMetersDelta, ' m', 0)}`,
      `- 有效踏频变化：${fmt(report.trend.effectiveCadenceRpmDelta, ' rpm', 0)}`,
      '',
      '以上只是两次活动的描述性差异，路线、天气、停留和设备条件不同，不能单独证明体能变化。',
    );
  }
  lines.push(
    '',
    '## 数据一致性',
    '',
    `- 踏频：${summary.ridesWithCadence}/${summary.rideCount} 次，记录覆盖 ${fmt(summary.cadenceCoveragePercent, '%', 0)}`,
    `- 心率：${summary.ridesWithHeartRate}/${summary.rideCount} 次，记录覆盖 ${fmt(summary.heartRateCoveragePercent, '%', 0)}`,
    `- 功率：${summary.ridesWithPower}/${summary.rideCount} 次，记录覆盖 ${fmt(summary.powerCoveragePercent, '%', 0)}`,
    `- 坡度：${summary.ridesWithGrade}/${summary.rideCount} 次，记录覆盖 ${fmt(summary.gradeCoveragePercent, '%', 0)}`,
    '',
    '## 综合建议',
    '',
  );
  for (const item of report.insights) lines.push(`- **${item.category} · ${item.title}**：${item.body}`);
  if (report.duplicates.length) {
    lines.push('', `重复文件（未计入）：${report.duplicates.map((item) => item.source).join('、')}`);
  }
  if (report.failed.length) {
    lines.push('', `解析失败（未计入）：${report.failed.map((item) => `${item.source}：${item.error}`).join('；')}`);
  }
  return lines.join('\n');
}

async function main() {
  let options;
  try {
    options = parseArguments(process.argv.slice(2));
    if (options.help) {
      console.log(usage());
      return;
    }
    if (!options.inputs.length) throw new Error('Provide at least one FIT/KML file or directory.');
    const appRoot = await findAppRoot(options.appRoot);
    await loadApplicationAnalyzer(appRoot);
    const paths = await expandInputs(options.inputs);
    if (!paths.length) throw new Error('No FIT or KML files found in the provided inputs.');

    const parsed = [];
    const failed = [];
    for (const filePath of paths) {
      try {
        parsed.push(await parseRide(filePath));
      } catch (error) {
        failed.push({ source: path.basename(filePath), error: error?.message || String(error) });
      }
    }
    if (!parsed.length) throw new Error(`No activity file could be parsed. ${failed.map((item) => `${item.source}: ${item.error}`).join('; ')}`);

    const unique = [];
    const duplicates = [];
    const seen = new Map();
    for (const ride of parsed) {
      const key = duplicateKey(ride);
      if (!options.keepDuplicates && seen.has(key)) duplicates.push({ source: ride.source, duplicateOf: seen.get(key) });
      else {
        seen.set(key, ride.source);
        unique.push(ride);
      }
    }

    const report = unique.length === 1
      ? { schemaVersion: VERSION, mode: 'single', ride: unique[0], duplicates, failed }
      : buildAggregate(unique, duplicates, failed);
    console.log(options.format === 'json'
      ? JSON.stringify(report, null, 2)
      : report.mode === 'single' ? renderSingle(report) : renderAggregate(report));
  } catch (error) {
    console.error(`Activity analysis failed: ${error?.message || error}`);
    process.exitCode = 1;
  }
}

await main();
