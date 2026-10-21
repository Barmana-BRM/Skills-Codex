#!/usr/bin/env node

import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { createServer as createNetServer } from 'node:net';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer as createViteServer } from 'vite';
import { fetchActivityFile, parseActivityFile } from '../src/data.js';
import {
  cleanupReportSession,
  REPORT_RUNTIME_ROOT,
  REPORT_SESSION_TTL_MS,
  stageReport,
} from './prepare-report.mjs';

const skillRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const temporaryDirectory = await fs.mkdtemp(path.join(os.tmpdir(), 'ride-relief-test-'));
const analysisPath = path.join(temporaryDirectory, 'analysis.json');
let server;
let staged;

try {
  await fs.writeFile(analysisPath, JSON.stringify({
    schemaVersion: 1,
    reports: [{ source: 'demo.kml', provider: 'Runtime Test', deepAnalysis: [], recommendations: [] }],
  }));
  const portProbe = createNetServer();
  await new Promise((resolve, reject) => portProbe.once('error', reject).listen(0, '127.0.0.1', resolve));
  const availablePort = portProbe.address().port;
  await new Promise((resolve, reject) => portProbe.close((error) => error ? reject(error) : resolve()));
  server = await createViteServer({
    root: skillRoot,
    configFile: path.join(skillRoot, 'vite.config.js'),
    logLevel: 'silent',
    server: { host: '127.0.0.1', port: availablePort, strictPort: true },
  });
  await server.listen();
  const address = server.httpServer.address();
  assert.equal(typeof address, 'object');
  const baseUrl = `http://127.0.0.1:${address.port}/`;
  staged = await stageReport({
    trackPath: path.join(skillRoot, 'samples', 'demo.kml'),
    analysisPath,
    baseUrl,
  });

  const [pageResponse, analysisResponse] = await Promise.all([
    fetch(staged.url),
    fetch(staged.analysisUrl),
  ]);
  assert.equal(pageResponse.status, 200);
  assert.match(await pageResponse.text(), /id="fit-input"/);
  assert.equal(analysisResponse.status, 200);
  assert.equal((await analysisResponse.json()).reports[0].source, 'demo.kml');

  const file = await fetchActivityFile(staged.trackUrl, 'demo.kml');
  const payload = await parseActivityFile(file);
  assert.equal(payload.source, 'demo.kml');
  assert.equal(payload.format, 'kml');
  assert.ok(payload.records.length >= 12);

  const expiredAt = new Date(Date.now() - REPORT_SESSION_TTL_MS - 1000);
  await fs.utimes(path.join(REPORT_RUNTIME_ROOT, staged.session), expiredAt, expiredAt);
  assert.equal((await fetch(staged.trackUrl)).status, 410);
  console.log(`Report runtime check passed: URL staging · ${payload.records.length} KML points · 24h expiry · temporary session cleanup`);
} finally {
  if (server) await server.close();
  if (staged?.session) await cleanupReportSession(staged.session);
  await fs.rm(temporaryDirectory, { recursive: true, force: true });
}
