import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

const EARTH_RADIUS = 6_371_000;
const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
const lerp = (start, end, amount) => start + (end - start) * amount;
const smoothstep = (value) => value * value * (3 - 2 * value);

const SLOPE_COLOR_STOPS = [
  { slope: -0.08, color: new THREE.Color(0x48a6c8) },
  { slope: -0.03, color: new THREE.Color(0x78d3c5) },
  { slope: 0, color: new THREE.Color(0xf1f4de) },
  { slope: 0.03, color: new THREE.Color(0xd6ff64) },
  { slope: 0.06, color: new THREE.Color(0xffc857) },
  { slope: 0.1, color: new THREE.Color(0xff6b42) },
];

const PALETTES = {
  night: { route: 0xd6ff64, curtain: 0x95c63d, dot: 0xf4ffbd, grid: 0x52604d, fog: 0x0b0d0c },
  paper: { route: 0xff6b42, curtain: 0xd75b3b, dot: 0xffd7a1, grid: 0x66584e, fog: 0x15110f },
  ice: { route: 0x72e8ff, curtain: 0x2e9fba, dot: 0xd8fbff, grid: 0x3e5961, fog: 0x081013 },
};

function disposeObject(object) {
  object.traverse((child) => {
    child.geometry?.dispose?.();
    if (Array.isArray(child.material)) child.material.forEach((material) => material.dispose?.());
    else child.material?.dispose?.();
    if (child.material?.map) child.material.map.dispose?.();
  });
}

function horizontalDistance(a, b) {
  const meanLatitude = ((a.lat + b.lat) * 0.5 * Math.PI) / 180;
  const deltaLatitude = ((b.lat - a.lat) * Math.PI) / 180;
  const deltaLongitude = ((b.lon - a.lon) * Math.PI) / 180;
  const north = deltaLatitude * EARTH_RADIUS;
  const east = deltaLongitude * EARTH_RADIUS * Math.cos(meanLatitude);
  return Math.hypot(north, east);
}

function colorForSlope(slope, target = new THREE.Color()) {
  const boundedSlope = clamp(
    slope,
    SLOPE_COLOR_STOPS[0].slope,
    SLOPE_COLOR_STOPS.at(-1).slope,
  );
  for (let index = 1; index < SLOPE_COLOR_STOPS.length; index += 1) {
    const start = SLOPE_COLOR_STOPS[index - 1];
    const end = SLOPE_COLOR_STOPS[index];
    if (boundedSlope <= end.slope) {
      const amount = (boundedSlope - start.slope) / Math.max(0.0001, end.slope - start.slope);
      return target.copy(start.color).lerp(end.color, smoothstep(amount));
    }
  }
  return target.copy(SLOPE_COLOR_STOPS.at(-1).color);
}

function buildSlopeProfile(metadata) {
  if (metadata.length < 2) return metadata.map(() => 0);
  const distances = [0];
  for (let index = 1; index < metadata.length; index += 1) {
    distances.push(distances[index - 1] + horizontalDistance(metadata[index - 1], metadata[index]));
  }

  const recordedGrades = metadata.map((record) => Number(record.grade));
  const reliableGradeCount = recordedGrades.filter(Number.isFinite).length;
  const useRecordedGrade = reliableGradeCount >= metadata.length * 0.5
    && recordedGrades.some((grade) => Number.isFinite(grade) && Math.abs(grade) > 0.05);

  let rawSlopes;
  if (useRecordedGrade) {
    // FIT grade is already device-filtered; a short spatial pass removes remaining sample jitter.
    rawSlopes = recordedGrades.map((grade) => clamp((Number.isFinite(grade) ? grade : 0) / 100, -0.16, 0.18));
  } else {
    // Fall back to altitude-derived grade when the FIT device did not record a grade field.
    const filteredAltitudes = metadata.map((_, index) => {
      let weightedAltitude = 0;
      let totalWeight = 0;
      for (let sample = 0; sample < metadata.length; sample += 1) {
        const distance = Math.abs(distances[sample] - distances[index]);
        if (distance > 32) continue;
        const weight = 1 - distance / 32;
        weightedAltitude += (Number(metadata[sample].altitude) || 0) * weight;
        totalWeight += weight;
      }
      return totalWeight ? weightedAltitude / totalWeight : Number(metadata[index].altitude) || 0;
    });
    rawSlopes = metadata.map((_, index) => {
      let left = index;
      let right = index;
      while (left > 0 && distances[index] - distances[left] < 55) left -= 1;
      while (right < metadata.length - 1 && distances[right] - distances[index] < 55) right += 1;
      const run = Math.max(1, distances[right] - distances[left]);
      return clamp((filteredAltitudes[right] - filteredAltitudes[left]) / run, -0.16, 0.18);
    });
  }

  return rawSlopes.map((_, index) => {
    let weightedSlope = 0;
    let totalWeight = 0;
    for (let sample = 0; sample < rawSlopes.length; sample += 1) {
      const distance = Math.abs(distances[sample] - distances[index]);
      if (distance > 45) continue;
      const weight = 1 - distance / 45;
      weightedSlope += rawSlopes[sample] * weight;
      totalWeight += weight;
    }
    return totalWeight ? weightedSlope / totalWeight : rawSlopes[index];
  });
}

function addSlopeColorsToTube(geometry, slopes, tubularSegments, radialSegments) {
  const colors = new Float32Array(geometry.attributes.position.count * 3);
  const workingColor = new THREE.Color();
  for (let segment = 0; segment <= tubularSegments; segment += 1) {
    const sourcePosition = (segment / tubularSegments) * Math.max(0, slopes.length - 1);
    const sourceIndex = Math.floor(sourcePosition);
    const nextIndex = Math.min(slopes.length - 1, sourceIndex + 1);
    const slope = lerp(slopes[sourceIndex] ?? 0, slopes[nextIndex] ?? 0, smoothstep(sourcePosition - sourceIndex));
    colorForSlope(slope, workingColor);
    for (let radial = 0; radial <= radialSegments; radial += 1) {
      const vertex = segment * (radialSegments + 1) + radial;
      colors[vertex * 3] = workingColor.r;
      colors[vertex * 3 + 1] = workingColor.g;
      colors[vertex * 3 + 2] = workingColor.b;
    }
  }
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
}

function makeLabelTexture(text, accent) {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 160;
  const context = canvas.getContext('2d');
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.font = '700 58px Arial, sans-serif';
  context.textAlign = 'center';
  context.textBaseline = 'middle';
  context.shadowColor = 'rgba(0,0,0,.65)';
  context.shadowBlur = 16;
  context.fillStyle = `#${accent.toString(16).padStart(6, '0')}`;
  context.fillText(text, canvas.width / 2, canvas.height / 2);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.minFilter = THREE.LinearFilter;
  return texture;
}

function roundedRect(context, x, y, width, height, radius) {
  const r = Math.min(radius, width / 2, height / 2);
  context.beginPath();
  context.moveTo(x + r, y);
  context.arcTo(x + width, y, x + width, y + height, r);
  context.arcTo(x + width, y + height, x, y + height, r);
  context.arcTo(x, y + height, x, y, r);
  context.arcTo(x, y, x + width, y, r);
  context.closePath();
}

function makePhotoTexture(photo) {
  const canvas = document.createElement('canvas');
  canvas.width = 480;
  canvas.height = 610;
  const context = canvas.getContext('2d');
  context.clearRect(0, 0, canvas.width, canvas.height);
  roundedRect(context, 8, 8, 464, 594, 28);
  context.save();
  context.clip();
  context.fillStyle = '#181b18';
  context.fillRect(0, 0, canvas.width, canvas.height);

  const imageRatio = photo.image.naturalWidth / photo.image.naturalHeight;
  const targetRatio = canvas.width / canvas.height;
  let sourceWidth = photo.image.naturalWidth;
  let sourceHeight = photo.image.naturalHeight;
  let sourceX = 0;
  let sourceY = 0;
  if (imageRatio > targetRatio) {
    sourceWidth = sourceHeight * targetRatio;
    sourceX = (photo.image.naturalWidth - sourceWidth) / 2;
  } else {
    sourceHeight = sourceWidth / targetRatio;
    sourceY = (photo.image.naturalHeight - sourceHeight) / 2;
  }
  context.drawImage(photo.image, sourceX, sourceY, sourceWidth, sourceHeight, 0, 0, canvas.width, canvas.height);
  const gradient = context.createLinearGradient(0, canvas.height * 0.5, 0, canvas.height);
  gradient.addColorStop(0, 'rgba(5,7,6,0)');
  gradient.addColorStop(1, 'rgba(5,7,6,.9)');
  context.fillStyle = gradient;
  context.fillRect(0, canvas.height * 0.45, canvas.width, canvas.height * 0.55);
  context.restore();

  context.lineWidth = 8;
  context.strokeStyle = 'rgba(246,248,235,.92)';
  roundedRect(context, 8, 8, 464, 594, 28);
  context.stroke();
  context.fillStyle = '#f6f8eb';
  context.font = '700 28px Arial, sans-serif';
  context.textAlign = 'left';
  context.fillText(photo.label.slice(0, 20), 38, 548);
  context.fillStyle = 'rgba(246,248,235,.72)';
  context.font = '600 20px Arial, sans-serif';
  context.fillText(photo.method.toUpperCase(), 38, 579);

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.minFilter = THREE.LinearFilter;
  return texture;
}

function makePhotoPulseTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 256;
  const context = canvas.getContext('2d');
  const gradient = context.createRadialGradient(128, 128, 8, 128, 128, 124);
  gradient.addColorStop(0, 'rgba(255,255,255,1)');
  gradient.addColorStop(0.18, 'rgba(214,255,100,.92)');
  gradient.addColorStop(0.48, 'rgba(214,255,100,.24)');
  gradient.addColorStop(1, 'rgba(214,255,100,0)');
  context.fillStyle = gradient;
  context.fillRect(0, 0, canvas.width, canvas.height);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.minFilter = THREE.LinearFilter;
  return texture;
}

export class RouteScene {
  constructor(canvas, onFrame, options = {}) {
    this.canvas = canvas;
    this.onFrame = onFrame;
    this.transparentBackground = Boolean(options.transparent);
    this.showGround = options.showGround ?? !this.transparentBackground;
    this.routeRadius = options.routeRadius ?? 0.66;
    this.routeGlowRadius = options.routeGlowRadius ?? 1.55;
    this.photoMarkersOnlyOnCue = Boolean(options.photoMarkersOnlyOnCue);
    this.scene = new THREE.Scene();
    this.scene.background = this.transparentBackground ? null : new THREE.Color(PALETTES.night.fog);
    this.scene.fog = this.transparentBackground ? null : new THREE.FogExp2(PALETTES.night.fog, 0.0032);
    this.camera = new THREE.PerspectiveCamera(36, 1, 0.1, 2000);
    this.renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: this.transparentBackground,
      premultipliedAlpha: false,
      preserveDrawingBuffer: true,
    });
    if (this.transparentBackground) this.renderer.setClearColor(0x000000, 0);
    this.previewPixelRatio = Math.min(window.devicePixelRatio, 2);
    this.exportRenderActive = false;
    this.renderer.setPixelRatio(this.previewPixelRatio);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.08;

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.055;
    this.controls.enablePan = false;
    this.controls.minDistance = 90;
    this.controls.maxDistance = 420;
    this.controls.maxPolarAngle = Math.PI * 0.49;
    this.controls.minPolarAngle = Math.PI * 0.12;

    this.timer = new THREE.Timer();
    this.timer.connect(document);
    this.routeGroup = new THREE.Group();
    this.routeGroup.rotation.order = 'YXZ';
    this.scene.add(this.routeGroup);
    this.photoMarkers = [];
    this.progress = 0;
    this.playing = true;
    this.spinning = true;
    this.presentationControlled = false;
    this.presentationElapsed = 0;
    this.spinAngle = 0;
    this.motionBlend = 1;
    this.autoSpinDuration = 22;
    this.basePitch = THREE.MathUtils.degToRad(-7);
    this.baseRoll = THREE.MathUtils.degToRad(-3);
    this.pitchAmplitude = THREE.MathUtils.degToRad(1.4);
    this.rollAmplitude = THREE.MathUtils.degToRad(0.8);
    this.bobAmplitude = 2.2;
    this.playbackSeconds = 18;
    this.paletteName = 'night';
    this.ready = false;
    this.resizeObserver = new ResizeObserver(() => this.resize());
    this.resizeObserver.observe(canvas.parentElement);
    this.resetCamera();
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  resetCamera() {
    const width = this.canvas.parentElement?.clientWidth ?? 1000;
    const narrow = width < 720;
    const compact = width < 460;
    this.camera.position.set(
      narrow ? 5 : 14,
      compact ? 162 : narrow ? 170 : 114,
      compact ? 336 : narrow ? 350 : 255,
    );
    this.controls.target.set(0, 8, 0);
    this.controls.update();
  }

  resize() {
    if (this.exportRenderActive) return;
    const parent = this.canvas.parentElement;
    if (!parent) return;
    const width = Math.max(1, parent.clientWidth);
    const height = Math.max(1, parent.clientHeight);
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height, false);
  }

  beginExportRender(width, height) {
    const renderWidth = Math.max(1, Math.round(width));
    const renderHeight = Math.max(1, Math.round(height));
    this.exportRenderActive = true;
    this.renderer.setPixelRatio(1);
    this.camera.aspect = renderWidth / renderHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(renderWidth, renderHeight, false);
  }

  endExportRender() {
    if (!this.exportRenderActive) return;
    this.exportRenderActive = false;
    this.renderer.setPixelRatio(this.previewPixelRatio);
    this.resize();
  }

  setRoute(payload) {
    this.clearRoute();
    this.payload = payload;
    this.records = payload.records;
    const { vectors, metadata, baseY } = this.projectRecords(payload.records);
    this.routeVectors = vectors;
    this.routeMetadata = metadata;
    this.baseY = baseY;
    this.slopeProfile = buildSlopeProfile(metadata);
    this.curve = new THREE.CatmullRomCurve3(vectors, false, 'centripetal', 0.32);
    const segments = clamp(vectors.length * 3, 420, 1500);
    const palette = PALETTES[this.paletteName];

    const glowGeometry = new THREE.TubeGeometry(this.curve, segments, this.routeGlowRadius, 8, false);
    addSlopeColorsToTube(glowGeometry, this.slopeProfile, segments, 8);
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      vertexColors: true,
      transparent: true,
      opacity: 0.16,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    this.glowMesh = new THREE.Mesh(glowGeometry, glowMaterial);
    this.routeGroup.add(this.glowMesh);

    const routeGeometry = new THREE.TubeGeometry(this.curve, segments, this.routeRadius, 5, false);
    addSlopeColorsToTube(routeGeometry, this.slopeProfile, segments, 5);
    const routeMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff, vertexColors: true });
    this.routeMesh = new THREE.Mesh(routeGeometry, routeMaterial);
    this.routeGroup.add(this.routeMesh);

    this.curtainMaterial = this.createCurtainMaterial();
    this.curtainMesh = new THREE.Mesh(
      this.createCurtainGeometry(vectors, baseY, this.slopeProfile),
      this.curtainMaterial,
    );
    this.routeGroup.add(this.curtainMesh);

    if (this.showGround) this.addGround(baseY, palette);
    this.addElevationLabels(vectors, metadata, palette);
    this.addRiderDot(palette);
    this.progress = 0;
    this.ready = true;
    this.resetCamera();
    this.resize();
  }

  projectRecords(records) {
    const lats = records.map((record) => record.lat);
    const lons = records.map((record) => record.lon);
    const altitudes = records.map((record) => Number(record.altitude) || 0);
    const lat0 = (Math.min(...lats) + Math.max(...lats)) / 2;
    const lon0 = (Math.min(...lons) + Math.max(...lons)) / 2;
    const cosLat = Math.cos((lat0 * Math.PI) / 180);
    const raw = records.map((record) => ({
      x: EARTH_RADIUS * ((record.lon - lon0) * Math.PI / 180) * cosLat,
      z: -EARTH_RADIUS * ((record.lat - lat0) * Math.PI / 180),
      altitude: Number(record.altitude) || 0,
      record,
    }));
    const minX = Math.min(...raw.map((point) => point.x));
    const maxX = Math.max(...raw.map((point) => point.x));
    const minZ = Math.min(...raw.map((point) => point.z));
    const maxZ = Math.max(...raw.map((point) => point.z));
    const minAltitude = Math.min(...altitudes);
    const maxAltitude = Math.max(...altitudes);
    const horizontalScale = 170 / Math.max(maxX - minX, maxZ - minZ, 1);
    const altitudeRange = Math.max(maxAltitude - minAltitude, 1);
    const verticalRange = clamp(altitudeRange * horizontalScale * 6.5, 18, 44);
    const verticalScale = verticalRange / altitudeRange;
    const centerX = (minX + maxX) / 2;
    const centerZ = (minZ + maxZ) / 2;
    const baseY = -14;

    const maxPoints = 520;
    const stride = Math.max(1, Math.ceil(records.length / maxPoints));
    const picked = raw.filter((_, index) => index % stride === 0 || index === raw.length - 1);
    const vectors = [];
    const metadata = [];
    let previous = null;
    for (let index = 0; index < picked.length; index += 1) {
      const item = picked[index];
      const target = new THREE.Vector3(
        (item.x - centerX) * horizontalScale,
        4 + (item.altitude - minAltitude) * verticalScale,
        (item.z - centerZ) * horizontalScale,
      );
      if (previous) {
        target.x = lerp(target.x, previous.x, 0.18);
        target.y = lerp(target.y, previous.y, 0.3);
        target.z = lerp(target.z, previous.z, 0.18);
      }
      vectors.push(target);
      metadata.push({ ...item.record, point: target.clone(), sourceIndex: index * stride });
      previous = target;
    }
    return { vectors, metadata, baseY };
  }

  createCurtainGeometry(points, baseY, slopes) {
    const positions = [];
    const fades = [];
    const colors = [];
    const colorA = new THREE.Color();
    const colorB = new THREE.Color();
    const bottomAColor = new THREE.Color();
    const bottomBColor = new THREE.Color();
    for (let index = 1; index < points.length; index += 1) {
      const a = points[index - 1];
      const b = points[index];
      const bottomA = new THREE.Vector3(a.x, baseY, a.z);
      const bottomB = new THREE.Vector3(b.x, baseY, b.z);
      colorForSlope(slopes[index - 1] ?? 0, colorA);
      colorForSlope(slopes[index] ?? 0, colorB);
      bottomAColor.copy(colorA).multiplyScalar(0.24);
      bottomBColor.copy(colorB).multiplyScalar(0.24);
      positions.push(
        a.x, a.y, a.z,
        b.x, b.y, b.z,
        bottomA.x, bottomA.y, bottomA.z,
        b.x, b.y, b.z,
        bottomB.x, bottomB.y, bottomB.z,
        bottomA.x, bottomA.y, bottomA.z,
      );
      fades.push(1, 1, 0, 1, 0, 0);
      colors.push(
        colorA.r, colorA.g, colorA.b,
        colorB.r, colorB.g, colorB.b,
        bottomAColor.r, bottomAColor.g, bottomAColor.b,
        colorB.r, colorB.g, colorB.b,
        bottomBColor.r, bottomBColor.g, bottomBColor.b,
        bottomAColor.r, bottomAColor.g, bottomAColor.b,
      );
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('aFade', new THREE.Float32BufferAttribute(fades, 1));
    geometry.setAttribute('aSlopeColor', new THREE.Float32BufferAttribute(colors, 3));
    geometry.computeVertexNormals();
    return geometry;
  }

  createCurtainMaterial() {
    return new THREE.ShaderMaterial({
      uniforms: { uOpacity: { value: 0.38 } },
      vertexShader: `
        attribute float aFade;
        attribute vec3 aSlopeColor;
        varying float vFade;
        varying vec3 vSlopeColor;
        void main() {
          vFade = aFade;
          vSlopeColor = aSlopeColor;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform float uOpacity;
        varying float vFade;
        varying vec3 vSlopeColor;
        void main() {
          float alpha = pow(smoothstep(0.0, 1.0, vFade), 1.55) * uOpacity;
          gl_FragColor = vec4(vSlopeColor, alpha);
        }
      `,
      transparent: true,
      depthWrite: false,
      side: THREE.DoubleSide,
    });
  }

  addGround(baseY, palette) {
    const disc = new THREE.Mesh(
      new THREE.CircleGeometry(126, 96),
      new THREE.MeshBasicMaterial({ color: palette.fog, transparent: true, opacity: 0.5, depthWrite: false }),
    );
    disc.rotation.x = -Math.PI / 2;
    disc.position.y = baseY - 0.12;
    this.routeGroup.add(disc);

    this.grid = new THREE.GridHelper(250, 18, palette.grid, palette.grid);
    this.grid.position.y = baseY - 0.04;
    this.grid.material.transparent = true;
    this.grid.material.opacity = 0.14;
    this.grid.material.depthWrite = false;
    this.routeGroup.add(this.grid);

    const ringMaterial = new THREE.MeshBasicMaterial({ color: palette.route, transparent: true, opacity: 0.1, side: THREE.DoubleSide });
    for (const radius of [54, 92, 123]) {
      const ring = new THREE.Mesh(new THREE.RingGeometry(radius - 0.16, radius, 128), ringMaterial.clone());
      ring.rotation.x = -Math.PI / 2;
      ring.position.y = baseY + 0.02;
      this.routeGroup.add(ring);
    }
  }

  addElevationLabels(vectors, metadata, palette) {
    let minIndex = 0;
    let maxIndex = 0;
    for (let index = 1; index < metadata.length; index += 1) {
      if (metadata[index].altitude < metadata[minIndex].altitude) minIndex = index;
      if (metadata[index].altitude > metadata[maxIndex].altitude) maxIndex = index;
    }
    this.labelSprites = [];
    for (const [index, icon] of [[minIndex, '▼'], [maxIndex, '▲']]) {
      const point = vectors[index];
      const text = `${icon} ${Math.round(metadata[index].altitude)} M`;
      const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
        map: makeLabelTexture(text, palette.route),
        transparent: true,
        depthWrite: false,
      }));
      sprite.position.copy(point).add(new THREE.Vector3(0, 15, 0));
      sprite.scale.set(28, 8.75, 1);
      this.routeGroup.add(sprite);
      const line = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints([point, point.clone().add(new THREE.Vector3(0, 11, 0))]),
        new THREE.LineBasicMaterial({ color: palette.route, transparent: true, opacity: 0.55 }),
      );
      this.routeGroup.add(line);
      this.labelSprites.push({ sprite, line, text });
    }
  }

  addRiderDot(palette) {
    this.rider = new THREE.Mesh(
      new THREE.SphereGeometry(1.9, 18, 18),
      new THREE.MeshBasicMaterial({ color: palette.dot }),
    );
    this.riderGlow = new THREE.Mesh(
      new THREE.SphereGeometry(3.7, 18, 18),
      new THREE.MeshBasicMaterial({ color: palette.dot, transparent: true, opacity: 0.22, blending: THREE.AdditiveBlending, depthWrite: false }),
    );
    this.routeGroup.add(this.rider, this.riderGlow);
  }

  addPhoto(photo) {
    if (!this.curve) return;
    const point = this.curve.getPointAt(clamp(photo.progress, 0, 1));
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({
      map: makePhotoPulseTexture(),
      transparent: true,
      depthWrite: false,
      opacity: 0,
      blending: THREE.AdditiveBlending,
    }));
    halo.position.copy(point).add(new THREE.Vector3(0, 6, 0));
    halo.scale.set(18, 18, 1);
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
      map: makePhotoTexture(photo),
      transparent: true,
      depthWrite: false,
      opacity: 0.42,
    }));
    sprite.center.set(0.5, 0.08);
    sprite.position.copy(point).add(new THREE.Vector3(0, 6, 0));
    sprite.scale.set(11, 14, 1);
    const line = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints([point, point.clone().add(new THREE.Vector3(0, 6, 0))]),
      new THREE.LineBasicMaterial({ color: PALETTES[this.paletteName].route, transparent: true, opacity: 0.3 }),
    );
    if (this.photoMarkersOnlyOnCue) {
      sprite.visible = false;
      line.visible = false;
      halo.visible = false;
    }
    this.routeGroup.add(line, halo, sprite);
    const marker = { photo, sprite, line, halo, active: false, cueStrength: 0 };
    this.photoMarkers.push(marker);
    return marker;
  }

  clearPhotos() {
    for (const marker of this.photoMarkers) {
      this.routeGroup.remove(marker.sprite, marker.line, marker.halo);
      disposeObject(marker.sprite);
      disposeObject(marker.line);
      disposeObject(marker.halo);
    }
    this.photoMarkers = [];
  }

  setPhotoCue(photo, strength = 0) {
    const bounded = clamp(Number(strength) || 0, 0, 1);
    for (const marker of this.photoMarkers) {
      marker.cueStrength = marker.photo === photo ? bounded : 0;
    }
  }

  clearRoute() {
    if (this.routeGroup) disposeObject(this.routeGroup);
    this.scene.remove(this.routeGroup);
    this.routeGroup = new THREE.Group();
    this.routeGroup.rotation.order = 'YXZ';
    this.scene.add(this.routeGroup);
    this.photoMarkers = [];
    this.ready = false;
  }

  setPalette(name) {
    if (!PALETTES[name]) return;
    this.paletteName = name;
    const palette = PALETTES[name];
    this.scene.background?.setHex(palette.fog);
    this.scene.fog?.color.setHex(palette.fog);
    if (this.rider) this.rider.material.color.setHex(palette.dot);
    if (this.riderGlow) this.riderGlow.material.color.setHex(palette.dot);
    if (this.grid) this.grid.material.color.setHex(palette.grid);
    if (this.payload) {
      for (const item of this.labelSprites ?? []) {
        item.sprite.material.map.dispose();
        item.sprite.material.map = makeLabelTexture(item.text, palette.route);
        item.sprite.material.needsUpdate = true;
        item.line.material.color.setHex(palette.route);
      }
      for (const marker of this.photoMarkers) marker.line.material.color.setHex(palette.route);
    }
  }

  progressForCoordinate(latitude, longitude) {
    if (!this.routeMetadata?.length) return 0;
    const cosLat = Math.cos((latitude * Math.PI) / 180);
    let bestIndex = 0;
    let bestDistance = Infinity;
    for (let index = 0; index < this.routeMetadata.length; index += 1) {
      const record = this.routeMetadata[index];
      const dx = (record.lon - longitude) * cosLat;
      const dy = record.lat - latitude;
      const distance = dx * dx + dy * dy;
      if (distance < bestDistance) {
        bestDistance = distance;
        bestIndex = index;
      }
    }
    return bestIndex / Math.max(1, this.routeMetadata.length - 1);
  }

  progressForTimestamp(date) {
    if (!this.records?.length) return null;
    const target = date.getTime();
    const times = this.records.map((record) => new Date(record.timestamp).getTime());
    if (!Number.isFinite(times[0]) || !Number.isFinite(times.at(-1))) return null;
    const timezoneOffsets = [0, -8 * 3600_000, 8 * 3600_000];
    let adjustedTarget = target;
    let smallestRangeDistance = Infinity;
    for (const offset of timezoneOffsets) {
      const candidate = target + offset;
      const distance = candidate < times[0] ? times[0] - candidate : candidate > times.at(-1) ? candidate - times.at(-1) : 0;
      if (distance < smallestRangeDistance) {
        adjustedTarget = candidate;
        smallestRangeDistance = distance;
      }
    }
    if (smallestRangeDistance > 12 * 3600_000) return null;
    let bestIndex = 0;
    let bestDistance = Infinity;
    for (let index = 0; index < times.length; index += 1) {
      const distance = Math.abs(times[index] - adjustedTarget);
      if (distance < bestDistance) {
        bestDistance = distance;
        bestIndex = index;
      }
    }
    return bestIndex / Math.max(1, times.length - 1);
  }

  setProgress(progress) {
    this.progress = ((progress % 1) + 1) % 1;
  }

  setPresentationProgress(progress) {
    this.presentationControlled = true;
    const boundedProgress = clamp(Number(progress) || 0, 0, 1);
    const phase = boundedProgress * Math.PI * 2;
    this.spinAngle = phase;
    this.presentationElapsed = phase / 0.66;
    this.routeGroup.rotation.y = phase;
    this.routeGroup.rotation.x = this.basePitch + Math.sin(phase) * this.pitchAmplitude;
    this.routeGroup.rotation.z = this.baseRoll + Math.sin(phase * 0.75 + 0.8) * this.rollAmplitude;
    this.routeGroup.position.y = Math.sin(phase) * this.bobAmplitude;
  }

  sampleAt(progress) {
    if (!this.records?.length) return null;
    return this.records[Math.min(this.records.length - 1, Math.round(progress * (this.records.length - 1)))];
  }

  activePhoto(progress) {
    if (!this.photoMarkers.length) return null;
    let nearest = null;
    let nearestDistance = Infinity;
    for (const marker of this.photoMarkers) {
      const rawDistance = Math.abs(progress - marker.photo.progress);
      const distance = Math.min(rawDistance, 1 - rawDistance);
      if (distance < nearestDistance) {
        nearestDistance = distance;
        nearest = marker;
      }
    }
    return nearest?.photo ?? null;
  }

  updatePresentationMotion(delta) {
    if (this.presentationControlled) return;
    const targetBlend = this.spinning ? 1 : 0;
    this.motionBlend = lerp(this.motionBlend, targetBlend, Math.min(1, delta * 3.2));

    if (this.motionBlend > 0.001) {
      this.presentationElapsed += delta * this.motionBlend;
    }
    if (this.spinning) {
      const radiansPerSecond = (Math.PI * 2) / this.autoSpinDuration;
      this.spinAngle = (this.spinAngle + delta * radiansPerSecond) % (Math.PI * 2);
    }

    const floatAmount = this.motionBlend;
    this.routeGroup.rotation.y = this.spinAngle;
    this.routeGroup.rotation.x = this.basePitch
      + Math.sin(this.presentationElapsed * 0.72) * this.pitchAmplitude * floatAmount;
    this.routeGroup.rotation.z = this.baseRoll
      + Math.sin(this.presentationElapsed * 0.54 + 0.8) * this.rollAmplitude * floatAmount;
    this.routeGroup.position.y = Math.sin(this.presentationElapsed * 0.66)
      * this.bobAmplitude
      * floatAmount;
  }

  renderFrame(timestamp = performance.now()) {
    if (this.ready) {
      const point = this.curve.getPointAt(this.progress);
      this.rider.position.copy(point);
      this.riderGlow.position.copy(point);
      const pulse = 1 + ((timestamp / 900) % 1) * 1.25;
      this.riderGlow.scale.setScalar(pulse);
      this.riderGlow.material.opacity = 0.27 * (2 - pulse);

      for (const marker of this.photoMarkers) {
        if (this.photoMarkersOnlyOnCue) {
          const cue = marker.cueStrength;
          const visible = cue > 0.001;
          marker.sprite.visible = visible;
          marker.line.visible = visible;
          marker.halo.visible = visible;
          if (visible) {
            const targetWidth = 11 + cue * 11;
            marker.sprite.scale.x = targetWidth;
            marker.sprite.scale.y = targetWidth * 1.27;
            marker.sprite.material.opacity = 0.18 + cue * 0.82;
            marker.line.material.opacity = 0.16 + cue * 0.7;
            marker.halo.scale.setScalar(18 + cue * 32);
            marker.halo.material.opacity = cue * (0.52 + 0.28 * Math.sin(timestamp / 80));
          }
          marker.active = visible;
          continue;
        }
        const rawDistance = Math.abs(this.progress - marker.photo.progress);
        const distance = Math.min(rawDistance, 1 - rawDistance);
        const routeEmphasis = 1 - smoothstep(clamp(distance / 0.058, 0, 1));
        const emphasis = Math.max(routeEmphasis, marker.cueStrength);
        const active = emphasis > 0.08;
        const targetWidth = 11 + emphasis * 9;
        marker.sprite.scale.x = lerp(marker.sprite.scale.x, targetWidth, 0.09);
        marker.sprite.scale.y = marker.sprite.scale.x * 1.27;
        marker.sprite.material.opacity = lerp(marker.sprite.material.opacity, 0.34 + emphasis * 0.66, 0.11);
        marker.line.material.opacity = lerp(marker.line.material.opacity, 0.22 + emphasis * 0.56, 0.11);
        marker.halo.scale.setScalar(18 + marker.cueStrength * 30);
        marker.halo.material.opacity = marker.cueStrength * (0.52 + 0.28 * Math.sin(timestamp / 80));
        marker.active = active;
      }
      this.onFrame?.(this.progress, this.sampleAt(this.progress), this.activePhoto(this.progress));
    }
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }

  animate(timestamp) {
    requestAnimationFrame(this.animate);
    this.timer.update(timestamp);
    const delta = Math.min(this.timer.getDelta(), 0.05);
    if (this.ready) {
      if (this.playing) this.setProgress(this.progress + delta / this.playbackSeconds);
      this.updatePresentationMotion(delta);
    }
    this.renderFrame(timestamp);
  }
}
