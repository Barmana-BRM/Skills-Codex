#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const skillRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const required = [
  'SKILL.md',
  'agents/openai.yaml',
  'package.json',
  'package-lock.json',
  'index.html',
  'vite.config.js',
  'samples/demo.kml',
  'scripts/analyze-fit.mjs',
  'scripts/check-install.mjs',
  'scripts/check-report-runtime.mjs',
  'scripts/prepare-report.mjs',
  'src/data.js',
  'src/main.js',
  'public/skill-analysis.json',
  'references/export-workflow.md',
  'references/location-enrichment.md',
  'references/report-contract.md',
  'references/ui-report-contract.md',
];
const moduleChecks = [
  '@phosphor-icons/web/regular',
  'exifr',
  'fit-file-parser',
  'h264-mp4-encoder',
  'html-to-image',
  'mediabunny',
  'three',
  'vite',
];
const ignoredDirectories = new Set(['.git', 'dist', 'node_modules', 'outputs', 'work']);

function machineList(values) {
  return values.length ? values.map((value) => encodeURIComponent(value)).join(',') : '-';
}

function nodeIsSupported(version = process.versions.node) {
  const [major, minor] = version.split('.').map(Number);
  return (major === 20 && minor >= 19) || (major === 22 && minor >= 12) || major > 22;
}

function markdownFiles(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) return ignoredDirectories.has(entry.name) ? [] : markdownFiles(absolute);
    return entry.isFile() && entry.name.endsWith('.md') ? [absolute] : [];
  });
}

const missingFiles = required.filter((relativePath) => !fs.existsSync(path.join(skillRoot, relativePath)));
const markdown = markdownFiles(skillRoot);
const brokenLinks = [];
for (const markdownPath of markdown) {
  const source = fs.readFileSync(markdownPath, 'utf8');
  for (const match of source.matchAll(/\]\(([^)]+)\)/g)) {
    const target = match[1].trim().split('#')[0];
    if (!target || /^(?:https?:|mailto:)/.test(target)) continue;
    const resolved = path.resolve(path.dirname(markdownPath), decodeURIComponent(target));
    if (!fs.existsSync(resolved)) brokenLinks.push(`${path.relative(skillRoot, markdownPath)}->${target}`);
  }
}

if (missingFiles.length || brokenLinks.length) {
  console.log(`ERROR missing_files=${machineList(missingFiles)} broken_links=${machineList(brokenLinks)}`);
  process.exit(1);
}

if (!nodeIsSupported()) {
  console.log(`UNSUPPORTED_NODE current=${process.versions.node} required=${encodeURIComponent('^20.19.0 || >=22.12.0')}`);
  process.exit(3);
}

const resolveFromRoot = createRequire(path.join(skillRoot, 'package.json'));
const missingModules = moduleChecks.filter((moduleName) => {
  try {
    resolveFromRoot.resolve(moduleName);
    return false;
  } catch {
    return true;
  }
});

if (missingModules.length) {
  console.log(`NEED_INSTALL missing_modules=${machineList(missingModules)}`);
  process.exit(2);
}

console.log(`OK skill=fit-ride-studio required_files=${required.length} markdown_files=${markdown.length} node=${process.versions.node}`);
