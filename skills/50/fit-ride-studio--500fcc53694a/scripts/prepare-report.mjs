#!/usr/bin/env node

import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

export const REPORT_RUNTIME_PREFIX = '/__ride-relief-runtime/';
export const REPORT_RUNTIME_ROOT = path.join(os.tmpdir(), 'guizang-sports-skill-runtime-v1');
export const REPORT_SESSION_TTL_MS = 24 * 60 * 60 * 1000;
const sessionPattern = /^[a-z0-9]+-[a-f0-9]{12}$/;

function usage() {
  return `Usage:
  node scripts/prepare-report.mjs --track <file.fit|file.kml> [--analysis <report.json>] [--base-url http://127.0.0.1:5174]
  node scripts/prepare-report.mjs --cleanup <session-id>`;
}

function parseArguments(argv) {
  const options = { baseUrl: 'http://127.0.0.1:5174/' };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === '--help' || argument === '-h') return { help: true };
    if (argument === '--track') options.trackPath = argv[++index];
    else if (argument === '--analysis') options.analysisPath = argv[++index];
    else if (argument === '--base-url') options.baseUrl = argv[++index];
    else if (argument === '--cleanup') options.cleanupSession = argv[++index];
    else throw new Error(`Unknown option: ${argument}`);
  }
  return options;
}

async function ensureRuntimeRoot() {
  await fs.mkdir(REPORT_RUNTIME_ROOT, { recursive: true, mode: 0o700 });
  await fs.chmod(REPORT_RUNTIME_ROOT, 0o700);
}

export async function cleanupStaleSessions(now = Date.now()) {
  await ensureRuntimeRoot();
  const entries = await fs.readdir(REPORT_RUNTIME_ROOT, { withFileTypes: true });
  await Promise.all(entries.filter((entry) => entry.isDirectory() && sessionPattern.test(entry.name)).map(async (entry) => {
    const directory = path.join(REPORT_RUNTIME_ROOT, entry.name);
    const details = await fs.stat(directory);
    if (now - details.mtimeMs > REPORT_SESSION_TTL_MS) await fs.rm(directory, { recursive: true, force: true });
  }));
}

export async function cleanupReportSession(sessionId) {
  if (!sessionPattern.test(String(sessionId))) throw new Error('Invalid report session id');
  const directory = path.join(REPORT_RUNTIME_ROOT, sessionId);
  await fs.rm(directory, { recursive: true, force: true });
}

async function copyPrivate(source, destination) {
  await fs.copyFile(source, destination);
  await fs.chmod(destination, 0o600);
}

function localBaseUrl(value) {
  const url = new URL(value);
  if (url.protocol !== 'http:' || !['127.0.0.1', 'localhost'].includes(url.hostname)) {
    throw new Error('--base-url must use http://127.0.0.1 or http://localhost');
  }
  url.pathname = '/';
  url.search = '';
  url.hash = '';
  return url;
}

export async function stageReport({ trackPath, analysisPath = null, baseUrl = 'http://127.0.0.1:5174/' }) {
  if (!trackPath) throw new Error('--track is required');
  const sourceTrack = path.resolve(trackPath);
  const trackDetails = await fs.stat(sourceTrack);
  if (!trackDetails.isFile()) throw new Error('Track path must be a file');
  const trackName = path.basename(sourceTrack);
  const extension = path.extname(trackName).toLowerCase();
  if (!['.fit', '.kml'].includes(extension)) throw new Error('Track must be a .fit or .kml file');

  let sourceAnalysis = null;
  if (analysisPath) {
    sourceAnalysis = path.resolve(analysisPath);
    const analysis = JSON.parse(await fs.readFile(sourceAnalysis, 'utf8'));
    if (!analysis || analysis.schemaVersion !== 1 || !Array.isArray(analysis.reports)) {
      throw new Error('Analysis JSON must follow schemaVersion 1 with a reports array');
    }
    if (!analysis.reports.some((report) => report?.source === trackName)) {
      throw new Error(`Analysis JSON has no report matching source ${trackName}`);
    }
  }

  await cleanupStaleSessions();
  const sessionId = `${Date.now().toString(36)}-${crypto.randomBytes(6).toString('hex')}`;
  const sessionDirectory = path.join(REPORT_RUNTIME_ROOT, sessionId);
  await fs.mkdir(sessionDirectory, { mode: 0o700 });

  const stagedTrack = path.join(sessionDirectory, trackName);
  await copyPrivate(sourceTrack, stagedTrack);
  const relativeTrackUrl = `${REPORT_RUNTIME_PREFIX}${sessionId}/${encodeURIComponent(trackName)}`;

  let relativeAnalysisUrl = null;
  if (sourceAnalysis) {
    const stagedAnalysis = path.join(sessionDirectory, 'analysis.json');
    await copyPrivate(sourceAnalysis, stagedAnalysis);
    relativeAnalysisUrl = `${REPORT_RUNTIME_PREFIX}${sessionId}/analysis.json`;
  }

  const reportUrl = localBaseUrl(baseUrl);
  reportUrl.searchParams.set('track', relativeTrackUrl);
  reportUrl.searchParams.set('name', trackName);
  if (relativeAnalysisUrl) reportUrl.searchParams.set('analysis', relativeAnalysisUrl);

  return {
    status: 'OK',
    session: sessionId,
    url: reportUrl.href,
    trackUrl: new URL(relativeTrackUrl, reportUrl).href,
    analysisUrl: relativeAnalysisUrl ? new URL(relativeAnalysisUrl, reportUrl).href : null,
    expiresAfterHours: 24,
  };
}

async function main() {
  try {
    const options = parseArguments(process.argv.slice(2));
    if (options.help) {
      console.log(usage());
      return;
    }
    if (options.cleanupSession) {
      await cleanupReportSession(options.cleanupSession);
      console.log(JSON.stringify({ status: 'OK', cleaned: options.cleanupSession }));
      return;
    }
    console.log(JSON.stringify(await stageReport(options)));
  } catch (error) {
    console.log(`ERROR message=${encodeURIComponent(error.message)}`);
    process.exitCode = 1;
  }
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) await main();
