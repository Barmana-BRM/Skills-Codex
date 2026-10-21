# Community Upload

Use this reference when `config/community-upload.local.json` exists and has `"enabled": true`, `"auto_submit": true`, and `"consent_acknowledged": true`.

## Purpose

Community upload lets public users authorize once with their own GitHub account, then automatically submit reverse-video-prompt iteration cases to the maintainer repository:

`zhengzhentao86/reverse-video-prompt`

This uses GitHub Issues as the central backend. It does not require the maintainer to run a server and does not expose maintainer Lark credentials.

## Setup

Users opt in locally:

```bash
python3 scripts/setup_community_upload.py --enable --yes
```

The setup script:

- shows the privacy notice
- checks GitHub CLI `gh`
- launches `gh auth login` if needed
- writes `config/community-upload.local.json`

Disable:

```bash
python3 scripts/setup_community_upload.py --disable
```

## What Can Be Submitted

Submit only information the user is allowed to share:

- product category
- target platform/model
- prompt text
- reference video description or authorized link
- generated video description or authorized link
- user feedback
- root-cause diagnosis
- reusable rule candidate
- prompt fix summary

Do not upload raw local video files, private customer material, faces, voices, or local file paths by default.

## Skill Behavior

When enabled, call `scripts/community_submit.py` after meaningful milestones:

- after first prompt generation: stage `prompt`
- after generated-video feedback: stage `feedback`
- after a successful or much-improved generation: stage `success`

Generate a stable `case_id` for the source video or iteration thread and keep it in conversation context. Also keep `issue_number` when returned. Later submissions with the same `case_id` should comment on the same GitHub issue instead of creating duplicates.

If community submit fails, continue the prompt work and report the submit failure separately.

## Example Commands

Create or reuse a case issue after first prompt generation:

```bash
python3 scripts/community_submit.py \
  --stage prompt \
  --case-id window-film-20260624 \
  --title "Window film prompt reverse-engineering" \
  --product-category "window film" \
  --prompt-file ./prompt-v1.txt \
  --reference-desc "原片是家庭窗膜安装，先裁剪、喷水、撕背胶、短手刮贴膜。"
```

Append feedback after a generated attempt:

```bash
python3 scripts/community_submit.py \
  --stage feedback \
  --case-id window-film-20260624 \
  --title "Window film prompt reverse-engineering" \
  --generated-desc "生成片把短手刮变成长柄玻璃刮，窗膜变成皱银箔。" \
  --user-feedback "工具和材料都漂移，前三秒没有讲清楚产品。" \
  --observed-failure "tool identity drift, material-state drift, weak first-3-second selling point" \
  --reusable-rule "表面贴装类视频必须锁定工具物种、材料状态、流程阶段和动作同步声音。"
```

## Privacy Boundary

This is not hidden telemetry. It runs only after explicit local opt-in. Public packages should commit only `config/community-upload.example.json`, never `config/community-upload.local.json`.
