# Videro – AI video markup by one team

Turns the video file into:

- **`timeline.json`** - scenes / chapters, highlights, transcript with timecodes;
- **`subtitles.srt`** - subtitles;
**`hls/master.m3u8`** is an adaptive HLS stream for a web player.
- **`poster.jpg`** - cover.

All "magic" (recognition of scenes, table of contents, highlights, correction of terms) is considered
On the **NeuralDeep Hub* infrastructure, your `sk-` will be enabled via the OpenAI-compatible API.
Locally you only need `ffmpeg`. No database, no S3, no servers, pure CLI.

>> This is an open-source extraction of pipiline from the "Workshop" on hub.neuraldeep.ru - that
> tags video lessons. It's just a preprocessor so anyone can drive the same thing.
At home, paying for models on Hub.

## Live example (Prod)

The same Pipeline spins in the prode and marked, for example, a lesson
**["Configure the developer's workplace with Claude Code"](https://neuraldeep.ru/learn/lessons/claude-code-setup) * *
(1:34:27 → **64 chapters**, **132 highlights**, transcript, subtitles - all automatically):

Lesson markup: player, now in frame panel and chapters with timecodes (examples/assets/lesson-markup.png)

On the right - automatically generated ** chapters with timecodes and signatures**, the panel "now in the frame"
with an AI description of the current fragment, Highlight tabs / Transcript / "Ask". It's all from `timeline.json`.

And in [`examples/timeline.sample.json`](examples/timeline.sample.json) - **the real conclusion** of this
Script on a short demo (5 scenes with captions/OCR/topic/highlights) to immediately see the format.

# How it works.

```
видео.mp4
  ├─ ffmpeg  → HLS (720/480/360) + poster.jpg          [локально]
  └─ ffmpeg scene-detect → окна сцен
       ├─ 3 кадра/сцена → vision-модель (qwen3.6-fp8)  → caption/topic/highlight  [Hub /v1]
       ├─ аудио → SpeechCore (whisperX) → транскрипт+диаризация                    [Hub]
       └─ коррекция субтитров по OCR-контексту          → subtitles.srt            [Hub /v1]
  → timeline.json
```

-

##1. Get a token

1. Register with **https://hub.neuraldeep.ru** (Yandex login or email/password).
2. Open access to models - you need access to the **vision model `qwen3.6-fp8`**:
- **Wallet (PAYG):** Replenish the balance and turn on the PAYG switch - you pay by token, the entire catalog is available; **or**
**Subscription** (starter/pro) - if the tariff includes the desired models.
3. Create the `sk-...` API key.
4. (Optional) Subtitles/Transcripts require access to SpeechCore
(**https://speechcore.neuraldeep.ru**, is the same Hub account) - use its `sk-` token as `SPEECHCORE_TOKEN`.

```bash
export NEURALDEEP_API_KEY=sk-...        # обязательно
export SPEECHCORE_TOKEN=sk-...          # опционально (субтитры/транскрипт)
```

Endpoint is the default `https://api.neuraldeep.ru/v1`. OpenAI-compatible API
> so you can target your gateway via `ND_BASE_URL`
> (I need a multimodal model with `response_format: json_schema`).

##2. Installation

```bash
git clone <этот-репозиторий> && cd videro-skill
pip install -r requirements.txt          # только requests
# ffmpeg:  macOS → brew install ffmpeg | Ubuntu → sudo apt install -y ffmpeg
ffmpeg -version && ffprobe -version      # проверка
```

##3. Launch

```bash
python scripts/videro.py путь/к/видео.mp4
# → videro-out/видео/{timeline.json, subtitles.srt, poster.jpg, hls/master.m3u8}
```

Flags:

| flag | sense |
|---|---|
| `--out DIR` | Default `./videro-out/<имя>` |
| `--profile user\|full` | `user` = 720/480/360 (def), `full` = +1080p |
| `--lang ru\|en\|…` | Speech language for ASR |
| `--no-hls` | Markup only (without transcode) - faster and cheaper |

Ask for a video (Q&A on `timeline.json`):

```bash
python scripts/ask.py videro-out/видео/timeline.json "сделай оглавление с таймкодами"
```

Package:

```bash
for f in ./videos/*.mp4; do python scripts/videro.py "$f" --out "build/$(basename "${f%.*}")"; done
```

Use by an agent (Claude Code/Codex)

The repository is a self-contained **kill**. Throw the agent a repo link:

- **Claude Code** reads `SKILL.md` (frontmatter + instructions) and delivers the user himself
From “no token” to ready-made `timeline.json`.
**Codex and others read `AGENTS.md` (same contract).

Scripts in `scripts/` can simply be copied to the user's project and applied - they do not depend on anything in this repo except `requests` and `ffmpeg`.

## `timeline.json` format

```jsonc
{
  "duration_sec": 612.3,
  "model": "qwen3.6-fp8",
  "scenes": [
    {
      "start": 0.0, "end": 24.5, "n_frames": 3,
      "screen_type": "slide",          // slide/code/terminal/demo/browser/talking_head/other
      "caption": "Введение и цели урока",
      "action": "Спикер представляет план и ключевые темы.",
      "on_screen_text": "Agenda: setup, demo, Q&A",
      "topic": "Введение",             // группируй по topic → главы
      "highlight": false,
      "highlight_reason": "",
      "importance": 2                  // 1–5
    }
  ],
  "highlights": [ { "start": 120.0, "end": 156.0, "caption": "...", "reason": "...", "importance": 5 } ],
  "transcript": [ { "start": 0.4, "end": 3.1, "text": "...", "speaker": "SPEAKER_00" } ],
  "srt": "1\n00:00:00,400 --> 00:00:03,100\n...\n"
}
```

# Cost and productivity

- Markup is **frames** (not video-native): hour-long video → dozens of vision requests.
Focus on the balance of the Hub wallet.
`--no-hls` skips the transcode (saves CPU/time if HLS is not needed).
- Got a GPU with NVENC? `export HLS_VCODEC=h264_nvenc HLS_PRESET=p4` (code unchanged)

## Tuning (env)

The full list is in `.env.template`. Frequent: `NDT_VISION_MODEL`, `FRAMES_PER_SCENE`
`MAX_SCENE_SEC`, `ANALYZE_WORKERS`, `ND_BASE_URL`.

## Limitations

Scene markup requires a **multimodal** model with `image_url` + strict `json_schema`
(Default `qwen3.6-fp8` does; pure text model does not.)
Subtitles/transcripts require **ASR-with-timecodes** (SpeechCore). Without `SPEECHCORE_TOKEN`
`transcript`/`srt` will be empty.
- `FIX_PROMPT` in `scripts/analyze.py` is sharpened for IT / AI-content.
Under another domain, tweak the prompt.

## License

MIT - see `LICENSE`.
