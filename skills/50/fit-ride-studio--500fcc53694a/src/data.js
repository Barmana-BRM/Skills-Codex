import FitParser from 'fit-file-parser';

const finite = (value) => value != null && value !== '' && Number.isFinite(Number(value));

const SPORT_META = {
  cycling: { key: 'cycling', zh: '骑行', english: 'RIDE', icon: 'ph-bicycle', cadence: '踏频', paceLabels: ['轻松', '巡航', '快速'] },
  running: { key: 'running', zh: '跑步', english: 'RUN', icon: 'ph-person-simple-run', cadence: '步频', paceLabels: ['恢复', '稳定', '快速'] },
  hiking: { key: 'hiking', zh: '徒步', english: 'HIKE', icon: 'ph-person-simple-hike', cadence: '步频', paceLabels: ['慢行', '稳定', '快速'] },
  other: { key: 'other', zh: '户外活动', english: 'ROUTE', icon: 'ph-path', cadence: '步频', paceLabels: ['轻松', '稳定', '快速'] },
};

export function normalizeSport(value) {
  const normalized = String(value ?? '').trim().toLowerCase();
  if (/running|run|跑步|越野跑/.test(normalized)) return 'running';
  if (/hiking|walking|walk|trek|徒步|登山|健走/.test(normalized)) return 'hiking';
  if (/cycling|biking|bike|骑行|自行车/.test(normalized)) return 'cycling';
  return normalized && SPORT_META[normalized] ? normalized : 'other';
}

export function sportMeta(value) {
  return SPORT_META[normalizeSport(value)] ?? SPORT_META.other;
}

export function formatPace(secondsPerKilometer) {
  if (!finite(secondsPerKilometer) || Number(secondsPerKilometer) <= 0) return '—';
  const seconds = Math.round(Number(secondsPerKilometer));
  return `${Math.floor(seconds / 60)}'${String(seconds % 60).padStart(2, '0')}\"`;
}

function normalizeRecord(record) {
  return {
    lat: Number(record.position_lat),
    lon: Number(record.position_long),
    altitude: finite(record.altitude) ? Number(record.altitude) : 0,
    speed: finite(record.speed) ? Number(record.speed) : 0,
    cadence: finite(record.cadence) ? Number(record.cadence) : 0,
    heartRate: finite(record.heart_rate) ? Number(record.heart_rate) : null,
    power: finite(record.power) ? Number(record.power) : null,
    grade: finite(record.grade) ? Number(record.grade) : null,
    temperature: finite(record.temperature) ? Number(record.temperature) : null,
    distance: finite(record.distance) ? Number(record.distance) : 0,
    elapsedTime: finite(record.elapsed_time) ? Number(record.elapsed_time) : null,
    timestamp: record.timestamp ? new Date(record.timestamp).toISOString() : null,
  };
}

function deriveSession(records) {
  const first = records[0];
  const last = records.at(-1);
  const speeds = records.map((record) => record.speed).filter(finite);
  const altitudes = records.map((record) => record.altitude).filter(finite);
  let ascent = 0;
  for (let index = 1; index < altitudes.length; index += 1) {
    const gain = altitudes[index] - altitudes[index - 1];
    if (gain > 0) ascent += gain;
  }

  return {
    startTime: first?.timestamp,
    totalElapsedTime: last?.elapsedTime ?? 0,
    totalTimerTime: last?.elapsedTime ?? 0,
    totalDistance: last?.distance ?? 0,
    totalCalories: null,
    avgSpeed: speeds.length ? speeds.reduce((sum, value) => sum + value, 0) / speeds.length : 0,
    maxSpeed: speeds.length ? Math.max(...speeds) : 0,
    totalAscent: Math.round(ascent),
    avgCadence: 0,
    sport: 'cycling',
  };
}

export async function parseFitFile(file) {
  const parser = new FitParser({
    force: true,
    mode: 'list',
    lengthUnit: 'm',
    speedUnit: 'km/h',
    elapsedRecordField: true,
  });
  const parsed = await parser.parseAsync(await file.arrayBuffer());
  const records = (parsed.records ?? [])
    .filter((record) => finite(record.position_lat) && finite(record.position_long))
    .map(normalizeRecord);
  if (records.length < 2) throw new Error('这份 FIT 里没有足够的 GPS 轨迹点');

  const rawSession = parsed.sessions?.[0];
  const session = rawSession
    ? {
        startTime: rawSession.start_time,
        totalElapsedTime: rawSession.total_elapsed_time,
        totalTimerTime: rawSession.total_timer_time,
        totalDistance: rawSession.total_distance,
        totalCalories: rawSession.total_calories,
        avgSpeed: rawSession.avg_speed,
        maxSpeed: rawSession.max_speed,
        totalAscent: rawSession.total_ascent,
        totalDescent: rawSession.total_descent,
        avgCadence: rawSession.avg_cadence,
        maxCadence: rawSession.max_cadence,
        avgHeartRate: rawSession.avg_heart_rate,
        maxHeartRate: rawSession.max_heart_rate,
        avgPower: rawSession.avg_power,
        maxPower: rawSession.max_power,
        avgTemperature: rawSession.avg_temperature,
        sport: normalizeSport(rawSession.sport),
      }
    : deriveSession(records);

  return { source: file.name, format: 'fit', session, records };
}

function decodeXmlText(value = '') {
  return String(value)
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1')
    .replace(/<[^>]+>/g, '')
    .replaceAll('&lt;', '<')
    .replaceAll('&gt;', '>')
    .replaceAll('&amp;', '&')
    .replaceAll('&quot;', '"')
    .replaceAll('&apos;', "'")
    .trim();
}

function parseCoordinateText(text, separator = ',') {
  const tuples = separator === ',' ? String(text).trim().split(/\s+/) : [String(text).trim()];
  return tuples.map((tuple) => {
    const values = separator === ',' ? tuple.split(',').map(Number) : tuple.split(/\s+/).map(Number);
    return { lon: values[0], lat: values[1], altitude: finite(values[2]) ? values[2] : 0 };
  }).filter((point) => finite(point.lat) && finite(point.lon));
}

function spatialRecords(points, timestamps = []) {
  const validTimes = timestamps.length === points.length
    && timestamps.every((value) => Number.isFinite(new Date(value).getTime()));
  const startTimestamp = validTimes ? new Date(timestamps[0]).getTime() : null;
  let cumulativeDistance = 0;
  const records = points.map((point, index) => {
    if (index) cumulativeDistance += haversineMeters(points[index - 1], point) ?? 0;
    const timestampMs = validTimes ? new Date(timestamps[index]).getTime() : null;
    const elapsedTime = timestampMs == null ? null : Math.max(0, (timestampMs - startTimestamp) / 1000);
    return {
      ...point,
      speed: null,
      cadence: 0,
      heartRate: null,
      power: null,
      grade: null,
      temperature: null,
      distance: cumulativeDistance,
      elapsedTime,
      timestamp: timestampMs == null ? null : new Date(timestampMs).toISOString(),
    };
  });

  for (let index = 1; index < records.length; index += 1) {
    const elapsedDelta = records[index].elapsedTime == null || records[index - 1].elapsedTime == null
      ? null
      : records[index].elapsedTime - records[index - 1].elapsedTime;
    const distanceDelta = records[index].distance - records[index - 1].distance;
    if (elapsedDelta > 0 && distanceDelta >= 0) records[index].speed = distanceDelta / elapsedDelta * 3.6;
  }

  for (let index = 0; index < records.length; index += 1) {
    let left = index;
    let right = index;
    while (left > 0 && records[index].distance - records[left].distance < 35) left -= 1;
    while (right < records.length - 1 && records[right].distance - records[index].distance < 35) right += 1;
    const run = records[right].distance - records[left].distance;
    if (run >= 20) records[index].grade = Math.max(-45, Math.min(45, (records[right].altitude - records[left].altitude) / run * 100));
  }
  return records;
}

function kmlDataMap(xml) {
  const values = {};
  const pattern = /<Data\b[^>]*name=["']([^"']+)["'][^>]*>[\s\S]*?<value\b[^>]*>([\s\S]*?)<\/value>[\s\S]*?<\/Data>/gi;
  for (const match of xml.matchAll(pattern)) {
    if (!(match[1] in values)) values[match[1]] = decodeXmlText(match[2]);
  }
  return values;
}

export async function parseKmlFile(file) {
  const xml = new TextDecoder().decode(await file.arrayBuffer());
  if (!/<kml\b/i.test(xml)) throw new Error('这不是有效的 KML 文件');
  const candidates = [];
  for (const match of xml.matchAll(/<LineString\b[^>]*>[\s\S]*?<coordinates\b[^>]*>([\s\S]*?)<\/coordinates>[\s\S]*?<\/LineString>/gi)) {
    const points = parseCoordinateText(match[1]);
    if (points.length > 1) candidates.push({ points, timestamps: [] });
  }
  for (const match of xml.matchAll(/<(?:gx:)?Track\b[^>]*>([\s\S]*?)<\/(?:gx:)?Track>/gi)) {
    const body = match[1];
    const points = [...body.matchAll(/<(?:gx:)?coord\b[^>]*>([\s\S]*?)<\/(?:gx:)?coord>/gi)]
      .flatMap((item) => parseCoordinateText(item[1], ' '));
    const timestamps = [...body.matchAll(/<when\b[^>]*>([\s\S]*?)<\/when>/gi)].map((item) => decodeXmlText(item[1]));
    if (points.length > 1) candidates.push({ points, timestamps });
  }
  candidates.sort((left, right) => right.points.length - left.points.length);
  const candidate = candidates[0];
  if (!candidate) throw new Error('这份 KML 里没有足够的轨迹点');

  const metadata = kmlDataMap(xml);
  const records = spatialRecords(candidate.points, candidate.timestamps);
  const firstName = xml.match(/<Document\b[^>]*>[\s\S]*?<name\b[^>]*>([\s\S]*?)<\/name>/i)?.[1];
  const title = decodeXmlText(firstName) || file.name.replace(/\.kml$/i, '');
  const recordedDistance = Number(metadata.Distance ?? metadata.Mileage);
  const totalDistance = recordedDistance > 0 ? recordedDistance : records.at(-1).distance;
  const totalTimerTime = records.at(-1).elapsedTime > 0 ? records.at(-1).elapsedTime : null;
  const speeds = records.map((record) => record.speed).filter((value) => finite(value) && Number(value) > 0);
  const sport = normalizeSport(metadata.SportTypeName || metadata.TrackTags || title);

  return {
    source: file.name,
    title,
    format: 'kml',
    metadata: {
      provider: /Tbulu|2bulu/i.test(xml) ? '两步路' : 'KML',
      sportName: metadata.SportTypeName || null,
      startName: metadata.PosStartName || null,
      endName: metadata.PosEndName || null,
      hasTimeData: totalTimerTime != null,
    },
    session: {
      startTime: records[0].timestamp,
      totalElapsedTime: totalTimerTime,
      totalTimerTime,
      totalDistance,
      totalCalories: Number(metadata.Calorie) > 0 ? Number(metadata.Calorie) : null,
      avgSpeed: totalTimerTime ? totalDistance / totalTimerTime * 3.6 : null,
      maxSpeed: speeds.length ? Math.max(...speeds) : null,
      totalAscent: Number(metadata.ElevationGain) >= 0 ? Number(metadata.ElevationGain) : null,
      totalDescent: Number(metadata.ElevationLoss) >= 0 ? Number(metadata.ElevationLoss) : null,
      avgCadence: null,
      sport,
    },
    records,
  };
}

export async function parseActivityFile(file) {
  const name = String(file?.name ?? '').toLowerCase();
  if (name.endsWith('.kml') || file?.type === 'application/vnd.google-earth.kml+xml') return parseKmlFile(file);
  if (name.endsWith('.fit') || file?.type === 'application/octet-stream' || !file?.type) return parseFitFile(file);
  throw new Error('目前支持 FIT 与 KML 轨迹文件');
}

export async function fetchActivityFile(url, suggestedName = '') {
  const response = await fetch(url, { cache: 'no-store' });
  if (!response.ok) throw new Error(`轨迹加载失败（HTTP ${response.status}）`);
  const responseName = decodeURIComponent(new URL(response.url).pathname.split('/').at(-1) || 'activity.fit');
  const name = pathlessBasename(suggestedName || responseName);
  if (!/\.(fit|kml)$/i.test(name)) throw new Error('轨迹 URL 必须指向 FIT 或 KML 文件');
  const contentType = response.headers.get('content-type')?.split(';')[0]
    || (name.toLowerCase().endsWith('.kml') ? 'application/vnd.google-earth.kml+xml' : 'application/octet-stream');
  return new File([await response.arrayBuffer()], name, { type: contentType });
}

function pathlessBasename(value) {
  return String(value).replaceAll('\\', '/').split('/').at(-1) || 'activity.fit';
}

export async function loadBundledSample() {
  const response = await fetch('/sample-route.json');
  if (!response.ok) throw new Error('示例路线加载失败');
  return response.json();
}

export function formatClock(seconds) {
  const safe = Math.max(0, Math.round(Number(seconds) || 0));
  const hours = Math.floor(safe / 3600);
  const minutes = Math.floor((safe % 3600) / 60);
  const remainder = safe % 60;
  if (hours) return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(remainder).padStart(2, '0')}`;
  return `${String(minutes).padStart(2, '0')}:${String(remainder).padStart(2, '0')}`;
}

export function formatActivityDate(value) {
  if (!value) return 'DATE UNKNOWN';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'DATE UNKNOWN';
  const datePart = new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: '2-digit',
    timeZone: 'Asia/Shanghai',
  }).format(date).toUpperCase();
  const hour = Number(new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    hourCycle: 'h23',
    timeZone: 'Asia/Shanghai',
  }).format(date));
  const period = hour >= 18 ? 'NIGHT' : hour >= 16 ? 'EVENING' : hour < 10 ? 'MORNING' : 'DAY';
  return `${datePart} · ${period}`;
}

const average = (values) => values.length
  ? values.reduce((sum, value) => sum + value, 0) / values.length
  : null;

function haversineMeters(start, end) {
  if (!start || !end) return null;
  const radius = 6_371_000;
  const toRadians = (value) => value * Math.PI / 180;
  const latitudeDelta = toRadians(end.lat - start.lat);
  const longitudeDelta = toRadians(end.lon - start.lon);
  const startLatitude = toRadians(start.lat);
  const endLatitude = toRadians(end.lat);
  const a = Math.sin(latitudeDelta / 2) ** 2
    + Math.cos(startLatitude) * Math.cos(endLatitude) * Math.sin(longitudeDelta / 2) ** 2;
  return 2 * radius * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function paceDistribution(speeds, sport = 'cycling') {
  const validSpeeds = speeds.filter((speed) => Number.isFinite(speed) && speed > 0);
  if (!validSpeeds.length) return null;
  const [easyLimit, steadyLimit] = sport === 'running' ? [7.5, 11.5] : sport === 'hiking' ? [3, 5.5] : [15, 25];
  const total = validSpeeds.length;
  return {
    easy: validSpeeds.filter((speed) => speed < easyLimit).length / total * 100,
    steady: validSpeeds.filter((speed) => speed >= easyLimit && speed < steadyLimit).length / total * 100,
    fast: validSpeeds.filter((speed) => speed >= steadyLimit).length / total * 100,
  };
}

function cadenceDistribution(values) {
  const total = Math.max(1, values.length);
  return {
    low: values.filter((cadence) => cadence < 70).length / total * 100,
    cruise: values.filter((cadence) => cadence >= 70 && cadence <= 90).length / total * 100,
    high: values.filter((cadence) => cadence > 90).length / total * 100,
  };
}

function percentile(values, ratio) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const position = Math.max(0, Math.min(sorted.length - 1, (sorted.length - 1) * ratio));
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  const blend = position - lower;
  return sorted[lower] + (sorted[upper] - sorted[lower]) * blend;
}

function analyzeGrade(records) {
  const rawGrades = records.map((record) => record.grade == null ? null : Number(record.grade));
  const validGrades = rawGrades.filter(Number.isFinite);
  const coverage = records.length ? validGrades.length / records.length * 100 : 0;
  if (validGrades.length < 2 || coverage < 10) {
    return {
      coverage,
      maxGrade: null,
      representativeGrade: null,
      distribution: null,
      climbs: [],
      analyzedDistanceMeters: 0,
    };
  }

  // The device grade field is already filtered. A short centered pass removes isolated spikes
  // without flattening real ramps, then distance weighting prevents slow sections dominating.
  const radius = 4;
  const smoothed = rawGrades.map((_, index) => {
    let sum = 0;
    let count = 0;
    for (let cursor = Math.max(0, index - radius); cursor <= Math.min(records.length - 1, index + radius); cursor += 1) {
      if (!Number.isFinite(rawGrades[cursor])) continue;
      sum += rawGrades[cursor];
      count += 1;
    }
    return count ? sum / count : null;
  });

  const distanceByBand = { descent: 0, flat: 0, climb: 0, steep: 0 };
  let analyzedDistanceMeters = 0;
  for (let index = 1; index < records.length; index += 1) {
    const distance = Number(records[index].distance) - Number(records[index - 1].distance);
    const grade = smoothed[index];
    if (!Number.isFinite(distance) || distance <= 0 || distance > 120 || !Number.isFinite(grade)) continue;
    analyzedDistanceMeters += distance;
    if (grade < -3) distanceByBand.descent += distance;
    else if (grade < 3) distanceByBand.flat += distance;
    else if (grade < 6) distanceByBand.climb += distance;
    else distanceByBand.steep += distance;
  }
  const distribution = analyzedDistanceMeters > 0
    ? Object.fromEntries(Object.entries(distanceByBand).map(([key, distance]) => [key, distance / analyzedDistanceMeters * 100]))
    : null;

  const climbs = [];
  const finishClimb = (startIndex, endIndex) => {
    if (startIndex == null || endIndex == null || endIndex <= startIndex) return;
    const startDistance = Number(records[startIndex].distance);
    const endDistance = Number(records[endIndex].distance);
    const distanceMeters = endDistance - startDistance;
    if (!Number.isFinite(distanceMeters) || distanceMeters < 200) return;
    let weightedGrade = 0;
    let weightedDistance = 0;
    const segmentGrades = [];
    for (let index = startIndex + 1; index <= endIndex; index += 1) {
      const distance = Number(records[index].distance) - Number(records[index - 1].distance);
      const grade = smoothed[index];
      if (!Number.isFinite(distance) || distance <= 0 || distance > 120 || !Number.isFinite(grade)) continue;
      weightedGrade += grade * distance;
      weightedDistance += distance;
      segmentGrades.push(grade);
    }
    const averageGradePercent = weightedDistance ? weightedGrade / weightedDistance : null;
    const startAltitude = Number(records[startIndex].altitude);
    const endAltitude = Number(records[endIndex].altitude);
    const elevationGainMeters = Number.isFinite(startAltitude) && Number.isFinite(endAltitude)
      ? Math.max(0, endAltitude - startAltitude)
      : distanceMeters * Math.max(0, averageGradePercent ?? 0) / 100;
    if (averageGradePercent == null || averageGradePercent < 2.5 || elevationGainMeters < 8) return;
    climbs.push({
      startDistanceMeters: startDistance,
      distanceMeters,
      elevationGainMeters,
      averageGradePercent,
      maxGradePercent: percentile(segmentGrades, 0.95),
    });
  };

  let climbStart = null;
  let lastClimbingIndex = null;
  let subThresholdDistance = 0;
  for (let index = 1; index < records.length; index += 1) {
    const distance = Number(records[index].distance) - Number(records[index - 1].distance);
    if (!Number.isFinite(distance) || distance < 0 || distance > 120) continue;
    const grade = smoothed[index];
    if (Number.isFinite(grade) && grade >= 3) {
      if (climbStart == null) climbStart = index - 1;
      lastClimbingIndex = index;
      subThresholdDistance = 0;
    } else if (climbStart != null) {
      subThresholdDistance += distance;
      if (subThresholdDistance > 200) {
        finishClimb(climbStart, lastClimbingIndex);
        climbStart = null;
        lastClimbingIndex = null;
        subThresholdDistance = 0;
      }
    }
  }
  finishClimb(climbStart, lastClimbingIndex);

  climbs.sort((left, right) => right.elevationGainMeters - left.elevationGainMeters || right.distanceMeters - left.distanceMeters);
  return {
    coverage,
    maxGrade: Math.max(...validGrades),
    representativeGrade: percentile(smoothed.filter(Number.isFinite), 0.99),
    distribution,
    climbs: climbs.slice(0, 3),
    analyzedDistanceMeters,
  };
}

export function analyzeActivity(payload) {
  const { records, session } = payload;
  const sport = normalizeSport(session.sport);
  const sportInfo = sportMeta(sport);
  const first = records[0];
  const last = records.at(-1);
  const speeds = records
    .filter((record) => record.speed != null && record.speed !== '')
    .map((record) => Number(record.speed))
    .filter((value) => Number.isFinite(value) && value >= 0);
  const altitudes = records.map((record) => Number(record.altitude)).filter(Number.isFinite);
  const cadenceValues = records.map((record) => Number(record.cadence)).filter((value) => Number.isFinite(value) && value > 0);
  const temperatures = records
    .filter((record) => record.temperature != null)
    .map((record) => Number(record.temperature))
    .filter(Number.isFinite);
  const heartRateValues = records.map((record) => Number(record.heartRate ?? record.heart_rate)).filter((value) => Number.isFinite(value) && value > 0);
  const powerValues = records.map((record) => Number(record.power)).filter((value) => Number.isFinite(value) && value > 0);
  const gradeAnalysis = analyzeGrade(records);

  const totalDistance = Number(session.totalDistance ?? last?.distance ?? 0);
  const timerCandidate = session.totalTimerTime ?? last?.elapsedTime;
  const timerTime = finite(timerCandidate) && Number(timerCandidate) > 0 ? Number(timerCandidate) : null;
  const elapsedCandidate = session.totalElapsedTime ?? timerTime;
  const elapsedTime = finite(elapsedCandidate) && Number(elapsedCandidate) > 0 ? Number(elapsedCandidate) : timerTime;
  const hasTimeData = timerTime != null;
  const pauseSeconds = hasTimeData && elapsedTime != null ? Math.max(0, elapsedTime - timerTime) : null;
  const movingRatio = hasTimeData && elapsedTime > 0 ? timerTime / elapsedTime * 100 : null;
  const recordedMaxSpeed = Number(session.maxSpeed);
  const maxSpeed = recordedMaxSpeed > 0 ? recordedMaxSpeed : speeds.some((value) => value > 0) ? Math.max(...speeds) : null;
  const averageSpeed = Number(session.avgSpeed) > 0
    ? Number(session.avgSpeed)
    : hasTimeData && totalDistance > 0 ? totalDistance / timerTime * 3.6 : null;
  const averagePaceSeconds = hasTimeData && totalDistance > 0 ? timerTime / (totalDistance / 1000) : null;
  const hasSpeedData = averageSpeed != null && speeds.some((value) => value > 0);
  const minAltitude = altitudes.length ? Math.min(...altitudes) : null;
  const maxAltitude = altitudes.length ? Math.max(...altitudes) : null;
  const altitudeRange = minAltitude != null && maxAltitude != null ? maxAltitude - minAltitude : null;
  const effectiveCadence = average(cadenceValues);
  const maxCadence = Number(session.maxCadence) > 0
    ? Number(session.maxCadence)
    : cadenceValues.length ? Math.max(...cadenceValues) : null;
  const cadenceCoverage = records.length ? cadenceValues.length / records.length * 100 : 0;
  const cadence = cadenceDistribution(cadenceValues);
  const averageTemperature = session.avgTemperature != null && Number.isFinite(Number(session.avgTemperature))
    ? Number(session.avgTemperature)
    : average(temperatures);
  const ascent = Number(session.totalAscent ?? 0);
  const descent = finite(session.totalDescent) ? Number(session.totalDescent) : null;
  const distanceKilometers = totalDistance / 1000;
  const ascentDensity = distanceKilometers > 0 ? ascent / distanceKilometers : 0;
  const routeGap = haversineMeters(first, last);
  const isLoop = routeGap != null && routeGap < Math.max(200, totalDistance * 0.02);
  const pace = paceDistribution(speeds, sport);
  const hasHeartRate = heartRateValues.length > records.length * 0.1 || Number(session.avgHeartRate) > 0;
  const hasPower = powerValues.length > records.length * 0.1 || Number(session.avgPower) > 0;
  const averageHeartRate = Number(session.avgHeartRate) > 0 ? Number(session.avgHeartRate) : average(heartRateValues);
  const maxHeartRate = Number(session.maxHeartRate) > 0
    ? Number(session.maxHeartRate)
    : heartRateValues.length ? Math.max(...heartRateValues) : averageHeartRate;
  const averagePower = Number(session.avgPower) > 0 ? Number(session.avgPower) : average(powerValues);
  const maxPower = Number(session.maxPower) > 0
    ? Number(session.maxPower)
    : powerValues.length ? Math.max(...powerValues) : averagePower;
  const gradeCoverage = gradeAnalysis.coverage;

  const terrain = ascentDensity < 5 ? '平缓路线' : ascentDensity < 15 ? '轻度起伏' : ascentDensity < 30 ? '连续起伏' : '爬坡路线';
  const routeShape = isLoop ? '闭环完成' : '点到点路线';
  const dominantPace = pace ? Object.entries(pace).sort((a, b) => b[1] - a[1])[0]?.[0] : null;
  const dominantPaceLabel = dominantPace == null
    ? '未记录可用时间与速度'
    : `${sportInfo.paceLabels[dominantPace === 'fast' ? 2 : dominantPace === 'steady' ? 1 : 0]}段占主导`;

  const recommendations = [];
  if (!hasTimeData) {
    recommendations.push({
      category: '数据',
      value: '轨迹没有有效时间轴',
      title: '时长、配速和停留应保持未记录',
      body: `当前 ${payload.format?.toUpperCase() || '轨迹'} 可以可靠还原路线、距离和海拔，但没有逐点时间，不能据此计算移动时长、平均配速或停留。`,
      actions: ['如果两步路中还能导出带时间的 GPX、KML 或 FIT，优先使用那一份。', '当前版本仍可用于路线复盘、坡度分析和 3D 导出。'],
    });
  } else if (elapsedTime > timerTime + 30) {
    recommendations.push({
      category: '节奏',
      value: `${Math.round(movingRatio)}% 移动占比`,
      title: movingRatio < 85 ? '减少碎片化停留' : '连续性已经不错',
      body: movingRatio < 85
        ? `全程有 ${formatClock(pauseSeconds)} 未在移动。可以区分主动休息、路况等待和真正的节奏中断，再决定是否需要调整路线。`
        : `停留时间只有 ${formatClock(pauseSeconds)}，路线连续性良好，可以继续维持当前节奏。`,
      actions: movingRatio < 85
        ? ['下次复盘时区分计划停留与被动等待，不把所有暂停都当作训练问题。', '若目标是连续骑行，优先调整路线而不是在路口抢时间。']
        : ['保留当前路线选择，并观察后半程速度是否仍能稳定。', '把相似路线作为后续节奏对比的基准。'],
    });
  }

  if (sport === 'cycling' && effectiveCadence != null && cadenceCoverage > 10) {
    const cadenceTitle = effectiveCadence < 70
      ? '平路试试更轻的齿比'
      : effectiveCadence <= 90
        ? '踏频处在舒适巡航区间'
        : '留意高踏频下的稳定性';
    recommendations.push({
      category: '踏频',
      value: `${Math.round(effectiveCadence)} rpm 有效踏频`,
      title: cadenceTitle,
      body: `有效踩踏中，70–90 rpm 的巡航区间占 ${Math.round(cadence.cruise)}%；有踏频的记录覆盖 ${Math.round(cadenceCoverage)}%。其余记录可能来自滑行、停车或传感器暂时丢失，不能直接视为低踏频。`,
      actions: ['在平路稳定段连续观察 5–10 分钟踏频，而不是追逐整段平均数。', '优先通过齿比和体感寻找稳定节奏，不把某个 rpm 当作所有路况的硬目标。'],
    });
  } else if (sport === 'running' && effectiveCadence != null && cadenceCoverage > 10) {
    recommendations.push({
      category: '步频',
      value: `${Math.round(effectiveCadence)} spm · ${Math.round(cadenceCoverage)}% 覆盖`,
      title: '步频需要结合设备定义与配速一起看',
      body: '不同设备可能记录单脚或双脚步频；在没有确认设备口径前，只适合比较同一设备下相似路段的变化。',
      actions: ['确认设备中的步频单位与记录口径。', '优先比较同一路线、相近配速下的稳定性，不套用统一目标值。'],
    });
  } else if (sport === 'cycling') {
    recommendations.push({
      category: '数据',
      value: '暂无踏频',
      title: '补齐踏频数据会更有用',
      body: '如果想分析骑行节奏，可以连接踏频传感器；仅用于路线分享则现有 GPS 数据已经足够。',
      actions: ['下一次骑行前确认踏频传感器已连接并有电。', '若只做路线分享，可以忽略这项缺失，不需要为了数据完整性额外购买设备。'],
    });
  }

  if (sport === 'hiking' && ascentDensity >= 30) {
    recommendations.push({
      category: '路线',
      value: `${ascentDensity.toFixed(1)} m/km · 最高 ${Math.round(maxAltitude ?? 0)} m`,
      title: '这是一条爬升密度较高的山地徒步',
      body: `全程约 ${(totalDistance / 1000).toFixed(1)} km，累计爬升约 ${Math.round(ascent)} m。距离不算很长，但单位距离的爬升集中，路线准备不能只看公里数。`,
      actions: ['出发前离线保存轨迹、天气与撤退路线，并为返程留出余量。', '把主要爬坡段和最高点作为补水、保暖与时间检查节点。'],
    });
  }

  if (isLoop && routeGap != null) {
    recommendations.push({
      category: '隐私',
      value: `起终点相距 ${Math.round(routeGap)} m`,
      title: '公开分享前隐藏起终点',
      body: '这是一条高度闭合的路线，起点和终点几乎重合。建议导出时自动裁掉或模糊首尾 300–500 米。',
      actions: ['公开发布前检查路线是否暴露住址、公司或固定集合点。', '优先隐藏首尾 300–500 米，同时避免在水印里写入精确地点。'],
    });
  }

  if (sport !== 'hiking' && hasTimeData && !hasHeartRate && !hasPower) {
    recommendations.push({
      category: '数据',
      value: '缺少心率与功率',
      title: '热量更适合看作设备估算',
      body: '当前数据足以做路线故事，但无法可靠判断训练负荷。若之后想分析强度和恢复，心率传感器会比继续堆叠 GPS 指标更有价值。',
      actions: ['把热量用于同设备、同设置下的相对比较，不当作精确摄入建议。', '若要分析强度，优先补充连续心率；功率分析还需要个人阈值。'],
    });
  }

  if (averageTemperature != null && averageTemperature >= 25 && timerTime >= 30 * 60) {
    const durationLabel = formatClock(timerTime);
    const temperatureLabel = Math.round(averageTemperature);
    const longHotRide = timerTime >= 2 * 60 * 60;
    const mediumHotRide = timerTime >= 60 * 60;
    recommendations.push({
      category: '补给',
      value: `${temperatureLabel}°C · ${durationLabel}`,
      title: longHotRide ? '长时间炎热活动要规划沿途补给' : mediumHotRide ? '高温活动提前规划补水' : '气温偏高，记得及时补水',
      body: longHotRide
        ? `本次移动 ${durationLabel}，设备记录平均环境温度 ${temperatureLabel}°C。一瓶水未必能覆盖全程；下次应结合路线补给点、体感和出汗情况规划途中补水与补给。`
        : mediumHotRide
          ? `本次移动 ${durationLabel}，设备记录平均环境温度 ${temperatureLabel}°C。出发前补水，并提前确认途中是否容易补充饮水。`
          : `本次移动 ${durationLabel}，设备记录平均环境温度 ${temperatureLabel}°C。带上饮水，并根据体感和出汗情况及时补充。`,
      actions: longHotRide
        ? ['出发前标记至少一个可补水点，并准备能覆盖延误时间的余量。', '根据个人出汗情况安排液体和电解质，不机械套用固定摄入量。']
        : ['出发前补水并随车携带饮水。', '出现异常头晕、恶心或寒战时停止骑行并及时降温求助。'],
    });
  }

  return {
    profile: {
      title: `${terrain} · ${routeShape}`,
      description: !hasTimeData
        ? `每公里爬升约 ${ascentDensity.toFixed(1)} 米，海拔 ${Math.round(minAltitude ?? 0)}–${Math.round(maxAltitude ?? 0)} 米；当前轨迹不含有效时间轴，因此不展示时长与配速。`
        : effectiveCadence != null
          ? `${dominantPaceLabel}，每公里爬升约 ${ascentDensity.toFixed(1)} 米；有效${sportInfo.cadence} ${Math.round(effectiveCadence)} ${sport === 'running' ? 'spm' : 'rpm'}，覆盖 ${Math.round(cadenceCoverage)}%。`
          : `${dominantPaceLabel}，每公里爬升约 ${ascentDensity.toFixed(1)} 米；本次轨迹未提供可用${sportInfo.cadence}。`,
    },
    metrics: {
      sport,
      totalDistance,
      timerTime,
      elapsedTime,
      hasTimeData,
      hasSpeedData,
      pauseSeconds,
      movingRatio,
      averageSpeed,
      averagePaceSeconds,
      maxSpeed,
      minAltitude,
      maxAltitude,
      altitudeRange,
      effectiveCadence,
      maxCadence,
      cadenceCoverage,
      cadence,
      averageTemperature,
      ascent,
      descent,
      ascentDensity,
      routeGap,
      isLoop,
      pace,
      hasHeartRate,
      hasPower,
      averageHeartRate,
      maxHeartRate,
      averagePower,
      maxPower,
      gradeCoverage,
      maxGrade: gradeAnalysis.maxGrade,
      representativeGrade: gradeAnalysis.representativeGrade,
      grade: gradeAnalysis.distribution,
      climbs: gradeAnalysis.climbs,
      gradeAnalyzedDistance: gradeAnalysis.analyzedDistanceMeters,
    },
    recommendations: recommendations.slice(0, 6),
  };
}
