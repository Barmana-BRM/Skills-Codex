# Lark Base 后台写入

Use this reference only when the user asks to use a Feishu/Lark Base as a data backend, or when `config/lark-backend.local.json` exists and has `"enabled": true`, `"auto_upload": true`, and `"consent_acknowledged": true`.

## Privacy Model

This backend is opt-in by configuration. Do not upload anything unless a local config explicitly enables it and acknowledges consent.

Public GitHub packages should commit only `config/lark-backend.example.json`. Do not commit `config/lark-backend.local.json`, app secrets, user access tokens, customer videos, or local media paths.

For community use, there are two safe deployment patterns:

1. **Per-user private backend**: each user authorizes their own Lark workspace and writes to their own Base.
2. **Central backend via explicit onboarding**: the maintainer provides an upload endpoint or Lark app OAuth flow. Users must clearly authorize upload during setup. Do not hide telemetry.

Raw media upload can involve copyright, faces, voices, customer data, and private local files. Make the install/onboarding text explicit: what is uploaded, where it is uploaded, who can access it, and how to disable it. For a shared public package, require users to set `consent_acknowledged=true` during setup before any automatic upload can run.

## Backend Schema

Create a Feishu/Lark Base table for iteration data, then copy `config/lark-backend.example.json` to `config/lark-backend.local.json` and fill in the real Base token, table id, form id, and field mappings.

Recommended fields:

- `original_video` -> `原视频`
- `prompt_1` -> `反推提示词 1`
- `replica_video_1` -> `复刻视频 1`
- `feedback_1` -> `复刻视频 1 修改意见`
- `prompt_2` -> `反推提示词 2`
- `replica_video_2` -> `复刻视频 2`
- `feedback_2` -> `复刻视频 2 修改意见`

## Upload Script

Use:

```bash
python3 scripts/upload_lark_backend.py --help
```

Examples:

Create a record with original video and first prompt:

```bash
python3 scripts/upload_lark_backend.py \
  --original-video ./reference.mp4 \
  --prompt-1-file ./prompt-v1.txt
```

Update an existing record after the first generated attempt:

```bash
python3 scripts/upload_lark_backend.py \
  --record-id recxxxx \
  --replica-video-1 ./generated-v1.mp4 \
  --feedback-1 "产品没有在前三秒出现，音频太弱。"
```

Create or update a second iteration:

```bash
python3 scripts/upload_lark_backend.py \
  --record-id recxxxx \
  --prompt-2-file ./prompt-v2.txt \
  --replica-video-2 ./generated-v2.mp4 \
  --feedback-2 "窗膜工具仍然漂移。"
```

## Skill Behavior

When enabled and available, upload after these moments:

- after receiving the original reference video: create a record and attach `原视频`
- after producing the first reverse prompt: write `反推提示词 1`
- after user provides generated video 1: attach `复刻视频 1`
- after user provides feedback on generated video 1: write `复刻视频 1 修改意见`
- after producing revised prompt: write `反推提示词 2`
- after user provides generated video 2: attach `复刻视频 2`
- after user provides feedback on generated video 2: write `复刻视频 2 修改意见`

Keep the `record_id` in the conversation context after the first upload. If the upload fails, continue the prompt work and report the upload failure separately.

## Limitations

- Skills do not have a universal install-time OAuth hook by themselves.
- A public skill cannot safely include the maintainer's Lark credentials.
- If a central backend is required for many users, build an explicit OAuth/setup flow or a small server endpoint. Do not rely on hidden local credentials.
