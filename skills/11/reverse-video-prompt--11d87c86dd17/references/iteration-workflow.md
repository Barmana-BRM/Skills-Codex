# 复刻反馈与自迭代工作流

Use this reference when the user sends a generated video after a previous reverse-engineered prompt, asks to iterate the prompt, asks to improve the skill itself, or wants to prepare a GitHub/community contribution.

## Principle

Treat every generated attempt as a data point, not automatically as a skill change.

The goal is to improve the prompt first, then decide whether the failure teaches a reusable rule. A reusable rule should help different products, scenes, or models, not only one clip.

## Required Inputs

Ask for or infer as many of these as possible:

- reference video or frame sequence
- generated attempt video(s)
- prompt version used to generate the attempt
- video model or platform, if known
- product category and target market
- user's concrete feedback, if any
- what "usable" means for this case: closer to reference, better TikTok Shop conversion, fewer artifacts, stronger first 3 seconds, better audio, etc.

If some inputs are missing, continue with the available evidence and mark assumptions. Do not block on perfect metadata unless the missing item is essential.

## Iteration Loop

1. Build comparable evidence.
   - Use matched timestamps, contact sheets, close-up frames, and audio checks when possible.
   - Compare the first 0-3 seconds separately from the full clip.
   - For audio, check onset, loudness, silence/noise-gating, speech density, action-sound transients, and whether the first line carries product/pain/proof information.

2. Diagnose drift.
   - Identify what changed visually: product, camera role, subject count, physical process, tool identity, character credibility, local authenticity, scene density, product prominence, proof action, or model polish.
   - Identify what changed in audio: silent opening, missing mouth voice, weak action sounds, late voiceover, generic ambience, low information density, or dead-air gaps.
   - Identify what changed commercially: unclear product category, weak first-3-second hook, missing pain point, no visible proof, over-complex secondary task, or untrustworthy factual errors.

3. Attribute likely prompt causes.
   - Was the prompt too vague?
   - Did product visibility wording override camera role?
   - Did realism bury the product?
   - Did the task become too complex?
   - Were audio instructions too generic?
   - Were negatives broad instead of targeted?
   - Did the prompt copy a reference contradiction?

4. Produce a revised prompt.
   - Fix the first 0-3 seconds first.
   - Lock the product's physical state and proof action.
   - Simplify any secondary task that caused factual errors.
   - Add only targeted negative constraints.
   - Keep the user's preferred prompt grammar and length when a prompt reference exists.

5. Classify the learning.
   - `prompt-only`: useful for this clip but too specific to become a skill rule.
   - `candidate skill rule`: likely reusable across product categories or repeated failures.
   - `reference-template update`: belongs in a template or domain section, not the main workflow.
   - `eval case`: good regression test for future skill changes.
   - `tooling`: repeated manual evidence work suggests a helper script or checklist should be added.

6. Decide whether to update the skill.
   - Update the skill only for reusable failures, repeated patterns, or high-impact blind spots.
   - Prefer small rules and checklists over long examples.
   - Avoid adding one clip's incidental product, scene, character, private path, or model artifact to the main workflow.

## Learning Card

When proposing a skill change, write a compact learning card:

```yaml
case_id: short-human-name
product_category: e.g. knee pads / window film / fragrance / cleaner
target_market: e.g. US TikTok Shop
reference_intent: what the original clip was trying to sell or prove
generated_failure: what went wrong in the generated attempt
user_feedback: what the user said, if any
root_cause: likely missing or misleading prompt constraint
reusable_rule: portable rule to add or strengthen
change_level: prompt-only | candidate skill rule | reference-template update | eval case | tooling
prompt_fix_summary: how the new prompt changes the model's center of gravity
risk_of_overfit: low | medium | high
privacy_note: whether any shared media/text should be excluded from GitHub
```

## Skill Change Gate

Apply this gate before editing `SKILL.md` or reference files:

- Reusable: Does the rule apply beyond one product or one exact clip?
- Observable: Can a future agent detect the failure from video/audio evidence?
- Actionable: Does the rule tell the prompt writer what to write differently?
- Lean: Can it be expressed as one checklist item, one small paragraph, or one template slot?
- Non-private: Does it avoid user-specific paths, private media, identifiable people, and copyrighted raw assets?
- Non-conflicting: Does it fit the existing camera, product, audio, and physical-correctness rules?

If two or more answers are "no", keep it as a prompt-only fix or eval case instead of changing the skill.

## Recommended Output For Iteration Runs

```text
【差异诊断】
Reference vs generated attempt, including first 3 seconds, product proof, audio, and artifacts.

【问题归因】
Which prompt choices likely caused the drift.

【新版提示词】
Copy-ready revised prompt.

【迭代记录】
Learning card in concise prose or YAML.

【是否建议更新 Skill】
prompt-only / candidate skill rule / reference-template update / eval case / tooling, with reason.

【可提交到 GitHub 的摘要】
One short issue or PR summary if this should become a community contribution.
```

## GitHub Contribution Model

Recommended repository structure:

```text
reverse-video-prompt/
├── SKILL.md
├── references/
│   ├── prompt-framework.md
│   └── iteration-workflow.md
├── scripts/
│   ├── README.md
│   └── export_iteration_case.py
├── evals/
│   └── evals.json
├── examples/
│   └── README.md
├── CONTRIBUTING.md
└── .github/
    ├── ISSUE_TEMPLATE/
    │   └── iteration-case.yml
    └── pull_request_template.md
```

Community issues should provide:

- product category
- target platform/model
- reference video description or authorized link
- generated attempt description or authorized link
- prompt used
- specific failure notes
- proposed reusable rule, if the contributor has one

Do not require contributors to upload raw videos publicly. They can share:

- contact sheets
- timestamped screenshots
- short text descriptions
- private links they have rights to share
- local reproduction notes

## Upload Policy

This skill does not upload usage records or media by itself. Automatic public upload is risky because reverse-engineering work often involves downloaded platform videos, customer materials, faces, voices, and local files.

Use an explicit opt-in upload model:

1. local analysis first
2. local export package second
3. user review and consent third
4. GitHub issue or PR upload last

The bundled script follows this rule:

```bash
python3 scripts/export_iteration_case.py \
  --title "Short case title" \
  --product-category "window film" \
  --observed-failure "The generated clip changed the short squeegee into a long cleaning tool." \
  --repo owner/reverse-video-prompt \
  --upload issue \
  --yes
```

Without `--upload issue --yes`, the script only writes local files.

Avoid raw-media upload by default. If the community later wants richer evidence hosting, use a separate consent-based process such as:

- contributor-owned cloud links
- signed upload forms
- private repo for sensitive cases
- redacted contact sheets
- generated metadata only

Do not implement silent telemetry in the skill. Silent telemetry would make users less willing to share real failed cases, and it creates privacy and copyright risk.

## Pull Request Standard

A PR should include at least one of:

- a reusable rule added to `SKILL.md` or `references/prompt-framework.md`
- a new eval case in `evals/evals.json`
- a domain-specific reference section
- a helper script for repeated evidence extraction

Every PR should explain:

- which failure it fixes
- why the fix is reusable
- what was deliberately not added to avoid overfitting
- whether any media or examples are private/copyrighted and excluded

## Eval Case Shape

Use lightweight evals for subjective video-prompt work. The expected output should describe behaviors, not exact words.

```json
{
  "id": "window-film-tool-identity",
  "prompt": "用户给原片和失败生成片，失败片把短手刮变成长柄清洁刮、黑蓝平膜变银色皱膜。请诊断并改提示词。",
  "expected_output": "Should identify tool/material identity drift, preserve process phases, revise prompt with short hand squeegee, flat mirror film, action-synchronized audio, and targeted negatives.",
  "files": []
}
```

## Versioning

For public releases:

- patch version: wording fix or one narrow rule
- minor version: new workflow, template section, or eval category
- major version: incompatible output format or major skill behavior change

Keep a short changelog entry:

```text
YYYY-MM-DD: Added first-3-second hook and audio information-density checks based on repeated ecommerce recreation failures.
```
