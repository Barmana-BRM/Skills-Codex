import { createHash } from 'node:crypto';
import { readFileSync, realpathSync, statSync } from 'node:fs';
import { isAbsolute, relative, resolve, sep } from 'node:path';

const TRAITS = new Set(['look', 'camera', 'style', 'scene', 'wardrobe', 'pose', 'framing', 'lighting', 'expression']);
const ITEM_KEYS = ['title', 'prompt', 'category', 'traits'];
const FIXES = Object.freeze({
  face: 'Keep the intended facial structure coherent and align the eyes naturally.',
  hands: 'Keep the intended hand and finger anatomy coherent, with clear joints and natural contact with objects.',
  anatomy: 'Preserve the intended number of limbs and their natural connections, distinct contours, plausible proportions and physical support. Correct unintended duplicate, fused or disconnected limbs.',
  identity: 'Preserve the intended identity and distinguishing features. When an actual identity reference is supplied, use it consistently.',
  adherence: 'Follow the original subject, action, object count, lettering and composition requirements precisely.',
  texture: 'Keep surface detail and lighting consistent with the requested visual medium; correct unintended smearing or broken texture.',
  motion: 'Keep movement continuous, physical support plausible and the intended anatomy stable throughout the shot.',
  other: 'Correct the specific defect described below while preserving the original creative requirements.'
});

function fail(code) { const error = new Error(code); error.code = code; throw error; }
function plain(value) { return value !== null && typeof value === 'object' && !Array.isArray(value) && [Object.prototype, null].includes(Object.getPrototypeOf(value)); }
function exactKeys(value, expected, code) {
  if (!plain(value) || Object.keys(value).length !== expected.length || !expected.every(key => Object.hasOwn(value, key))) fail(code);
}
function string(value, max, code, required = true) {
  if (typeof value !== 'string' || value.length > max || /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/u.test(value)) fail(code);
  const result = value.trim();
  if (required && !result) fail(code);
  return result;
}
function parameters({ count, width, height, mode = 't2i' } = {}) {
  if (!Number.isInteger(count) || count < 1 || count > 12) fail('invalid_count');
  // These are application inputs, not a declaration of any model's size limit.
  if (![width, height].every(value => Number.isSafeInteger(value) && value > 0)) fail('invalid_dimensions');
  if (!['t2i', 'edit'].includes(mode)) fail('invalid_mode');
  return { count, width, height, mode };
}
function context(value, name, max = 16000) {
  if (value === undefined || value === null) return null;
  let encoded;
  try { encoded = JSON.stringify(value); } catch { fail('invalid_' + name); }
  if (typeof encoded !== 'string' || encoded.length > max) fail('invalid_' + name);
  return JSON.parse(encoded);
}
function planningContext(options, count) {
  const exploration = options.exploration ?? 0.2;
  const offset = options.offset ?? 0;
  const totalCount = options.totalCount ?? count;
  const existingTitles = options.existingTitles ?? [];
  if (typeof exploration !== 'number' || !Number.isFinite(exploration) || exploration < 0 || exploration > 1) fail('invalid_exploration');
  if (!Number.isInteger(totalCount) || totalCount < count || totalCount > 12 || !Number.isInteger(offset) || offset < 0 || offset + count > totalCount) fail('invalid_batch_context');
  if (!Array.isArray(existingTitles) || existingTitles.length > 100) fail('invalid_existing_titles');
  return { exploration, offset, totalCount, existingTitles: existingTitles.map(title => string(title, 100, 'invalid_existing_title')) };
}
function localFile(root, path) {
  if (typeof path !== 'string' || !path || isAbsolute(path) || path.includes('\\')) fail('invalid_instruction_path');
  const absolute = realpathSync(resolve(root, path));
  const rel = relative(root, absolute);
  if (!rel || rel === '..' || rel.startsWith('..' + sep) || isAbsolute(rel)) fail('invalid_instruction_path');
  if (!statSync(absolute).isFile() || statSync(absolute).size > 131072) fail('invalid_instruction_file');
  return absolute;
}

/** Load a portable skill from disk; never connects to a model or reads app settings. */
export function loadSkillBundle(skillDir) {
  const root = realpathSync(skillDir);
  const manifestBytes = readFileSync(localFile(root, 'runtime/manifest.json'));
  const manifest = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(manifestBytes));
  if (!plain(manifest) || manifest.schemaVersion !== 1 || manifest.id !== 'qwen-image-gen' || !/^\d+\.\d+\.\d+$/.test(manifest.version)) fail('invalid_skill_manifest');
  const paths = manifest.instructionFiles;
  if (!Array.isArray(paths) || !paths.length || paths.length > 20 || new Set(paths).size !== paths.length) fail('invalid_instruction_files');
  const hash = createHash('sha256');
  hash.update(JSON.stringify({ schemaVersion: manifest.schemaVersion, id: manifest.id, version: manifest.version }));
  const files = [], parts = [];
  let total = 0;
  // Runtime code also contains contract wording and validation rules. Pin it with
  // the guidance, without placing executable source in the model's instructions.
  const runtimePath = 'runtime/core.mjs';
  if (paths.includes(runtimePath)) fail('invalid_instruction_files');
  for (const path of [...paths, runtimePath]) {
    const bytes = readFileSync(localFile(root, path));
    total += bytes.length;
    if (total > 524288) fail('instruction_bundle_too_large');
    const content = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
    // Length-prefix names and bytes so distinct file boundaries cannot collide.
    hash.update('\n' + Buffer.byteLength(path) + ':' + path + ':' + bytes.length + ':');
    hash.update(bytes);
    files.push(Object.freeze({ path, sha256: createHash('sha256').update(bytes).digest('hex'), bytes: bytes.length }));
    if (path !== runtimePath) parts.push('### Shared file: ' + path + '\n' + content);
  }
  return Object.freeze({ id: manifest.id, version: manifest.version, digest: hash.digest('hex'), instructions: parts.join('\n\n'), files: Object.freeze(files) });
}

/** Build an OpenAI-compatible messages array; context stays outside shared rules. */
export function buildPlannerMessages(bundle, options = {}) {
  const { count, width, height, mode } = parameters(options);
  if (!plain(bundle) || bundle.id !== 'qwen-image-gen' || typeof bundle.instructions !== 'string' || !/^[a-f0-9]{64}$/.test(bundle.digest)) fail('invalid_skill_bundle');
  const brief = string(options.brief, 20000, 'invalid_brief');
  const referenceDescription = string(options.referenceDescription ?? '', 12000, 'invalid_reference_description', false);
  if (mode === 'edit' && !referenceDescription) fail('reference_description_required');
  const system = `You prepare individual Qwen-Image prompts from a user's creative brief using the shared skill below. This call only returns a plan; it does not generate images or perform operations.

The original brief is the current creative intent. Preserve its explicit subjects, counts, text, colors, poses, visual medium and constraints. Preferences may fill unspecified choices but must not contradict the original brief. Quality feedback corrects defects, not taste. A supplied reference description is contextual data, not evidence that you personally inspected an image. Do not claim a generation or inspection happened. Never turn an example in the shared skill into an unstated requirement for this brief.

Planning context may identify a chunk within a larger batch. Use its offset and existingTitles to avoid repeating earlier planned ideas; do not emit the earlier items again. The exploration fraction applies only to choices the original brief leaves open, and is not permission to change fixed requirements. Controlled comparisons may intentionally keep requested elements identical.

Return a single JSON object and nothing else, without Markdown fences or commentary: {"items":[{"title":"short title","prompt":"complete single-image prompt","category":"short visual category","traits":{"style":"visual style"}}]}. Return exactly ${count} items. Each item is one complete single-image prompt, not a collage or a batch instruction unless the original brief asks for a collage. Use only these four item keys. Title is 1–100 characters, prompt 1–20000, category 1–80. Traits is an object with optional text values (1–200 characters) under look, camera, style, scene, wardrobe, pose, framing, lighting, expression. Use only applicable traits; do not invent personal attributes.

The application owns width ${width}, height ${height}, and mode ${mode}. Do not emit dimensions, seeds, routes, URLs, paths, API calls, code or execution instructions as plan fields. In t2i mode no image is attached: do not use <imageN> tags or imply a reference identity is available. In edit mode describe the intended change and the parts to preserve; do not simultaneously freeze a pose or setting that the brief asks to change. The following shared materials describe several output formats for other tasks; this planning call uses only the items contract above.

Shared skill ${bundle.id}@${bundle.version}, digest ${bundle.digest}:
${bundle.instructions}`;
  const user = JSON.stringify({
    originalBrief: brief,
    generation: { count, width, height, mode },
    planningContext: planningContext(options, count),
    referenceDescription: referenceDescription || null,
    preferences: context(options.preferences, 'preferences'),
    qualityContext: context(options.qualityContext, 'quality_context')
  }, null, 2);
  return [{ role: 'system', content: system }, { role: 'user', content: user }];
}

/** Parse model text strictly. Model output cannot select files, routes or operations. */
export function validatePlan(raw, options) {
  const { count, mode } = parameters(options);
  let parsed = raw;
  if (typeof raw === 'string') {
    if (raw.length > 300000) fail('plan_too_large');
    try { parsed = JSON.parse(raw); } catch { fail('invalid_plan_json'); }
  }
  exactKeys(parsed, ['items'], 'invalid_plan_fields');
  if (!Array.isArray(parsed.items) || parsed.items.length !== count) fail('plan_count_mismatch');
  const items = parsed.items.map(item => {
    exactKeys(item, ITEM_KEYS, 'invalid_item_fields');
    const title = string(item.title, 100, 'invalid_title');
    const prompt = string(item.prompt, 20000, 'invalid_prompt');
    const category = string(item.category, 80, 'invalid_category');
    if (mode === 't2i' && /<\s*\/?\s*image\s*(?:\d+|n)?\s*\/?\s*>/iu.test(prompt)) fail('reference_tag_without_image');
    if (!plain(item.traits) || Object.keys(item.traits).some(key => !TRAITS.has(key))) fail('invalid_traits');
    const traits = Object.fromEntries(Object.entries(item.traits).map(([key, value]) => [key, string(value, 200, 'invalid_trait_value')]));
    return { title, prompt, category, traits };
  });
  return { items };
}

/** General correction text; user preference, storage and acceptance live downstream. */
export function qualityCorrection({ issues = [], note = '', correction = '' } = {}) {
  if (!Array.isArray(issues) || issues.some(issue => typeof issue !== 'string' || !Object.hasOwn(FIXES, issue))) fail('invalid_quality_issue');
  const observed = string(note, 1000, 'invalid_quality_note', false);
  const requested = string(correction, 2000, 'invalid_quality_correction', false);
  return [
    ...[...new Set(issues)].map(issue => FIXES[issue]),
    observed && 'Observed defects (do not depict these defects): ' + observed,
    requested && 'Requested correction: ' + requested
  ].filter(Boolean).join('\n');
}
