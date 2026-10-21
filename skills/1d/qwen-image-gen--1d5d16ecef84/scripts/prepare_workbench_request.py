#!/usr/bin/env python3
"""Build a Qwen workbench request locally. No network, GPU, login or submission."""
import argparse
import base64
import json
import math
import os
from pathlib import Path
import re


def legal_dimension(value):
    return type(value) is int and 256 <= value <= 2048 and value % 32 == 0


def ratio_pixels(value, quality):
    match = re.fullmatch(r"([1-9]\d{0,5}):([1-9]\d{0,5})", value)
    if not match:
        raise ValueError("wh_ratio must be positive integer W:H, e.g. 9:16")
    a, b = map(int, match.groups())
    d = math.gcd(a, b)
    a, b = a // d, b // d
    ratio = a / b
    if not 1 / 8 <= ratio <= 8:
        raise ValueError("Workbench ratio must lie between 1:8 and 8:1")
    target = 2048**2 * min(ratio, 1 / ratio) if quality == "high" else 1024**2
    low = math.ceil(256 / (32 * min(a, b)))
    high = math.floor(2048 / (32 * max(a, b)))
    if low <= high and high > 0:
        scale = min(high, max(low, int(math.sqrt(target / (a * b)) / 32 + 0.5)))
        return a * 32 * scale, b * 32 * scale
    return min(((w, h) for w in range(256, 2049, 32) for h in range(256, 2049, 32)),
               key=lambda wh: 50 * abs(math.log((wh[0] / wh[1]) / ratio))
               + abs(math.log(wh[0] * wh[1] / target)))


def prepare(data, *, mode="t2i", quality="standard", width=None, height=None,
            steps=None, seed=None, reference=None, transparent=False):
    if not isinstance(data, dict):
        raise ValueError("Rewrite must be one JSON object")
    allowed = {"rewritten_prompt", "wh_ratio", "ratio_follow"}
    if set(data) - allowed:
        raise ValueError("Rewrite JSON may contain only rewritten_prompt, wh_ratio and ratio_follow")
    prompt = data.get("rewritten_prompt")
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 20000:
        raise ValueError("rewritten_prompt must be nonempty text, at most 20000 characters")
    ratio, follow = data.get("wh_ratio", ""), data.get("ratio_follow", "")
    if not isinstance(ratio, str) or not isinstance(follow, str):
        raise ValueError("wh_ratio and ratio_follow must be strings")
    ratio, follow = ratio.strip(), follow.strip()
    if ratio and follow:
        raise ValueError("wh_ratio and ratio_follow are mutually exclusive")
    if mode not in ("t2i", "edit") or quality not in ("standard", "high"):
        raise ValueError("Invalid mode or quality")
    if type(transparent) is not bool:
        raise ValueError("transparent must be boolean")
    steps = (40 if mode == "edit" else 25) if steps is None else steps
    if type(steps) is not int or not 1 <= steps <= 60:
        raise ValueError("steps must be an integer from 1 to 60")
    if seed is not None and (type(seed) is not int or not 0 <= seed <= 9007199254740991):
        raise ValueError("seed must be a nonnegative JavaScript safe integer")
    body = {"mode": mode, "prompt": prompt.strip(), "steps": steps, "transparent": transparent}
    if seed is not None:
        body["seed"] = seed
    summary = {"mode": mode, "submitted": False}
    tags = re.findall(r"<image(\d+)>", prompt)

    if mode == "t2i":
        if reference is not None or follow or tags:
            raise ValueError("T2I cannot consume reference images; use edit")
        if not ratio:
            raise ValueError("T2I requires wh_ratio; preserve the Agent's canvas decision")
        suggested = ratio_pixels(ratio, quality)
        if width is not None or height is not None:
            if not legal_dimension(width) or not legal_dimension(height):
                raise ValueError("Explicit width and height must both be 256..2048 multiples of 32")
            source = "explicit-override"
        else:
            width, height = suggested
            source = "rewriter-ratio"
        body.update(width=width, height=height)
        a, b = map(int, ratio.split(":"))
        d = math.gcd(width, height)
        summary.update(width=width, height=height, requested_ratio=ratio,
                       actual_ratio=f"{width // d}:{height // d}",
                       approximate=(width * b != height * a), size_source=source)
    else:
        if ratio or width is not None or height is not None:
            raise ValueError("This workbench edit route follows the reference at ~1MP; it cannot apply a new output ratio or explicit pixels")
        if follow != "<image1>" or any(tag != "1" for tag in tags):
            raise ValueError("This workbench edit route accepts exactly one reference: <image1>")
        if reference is None:
            raise ValueError("Edit requires --reference with a local PNG/JPEG/WebP")
        path = Path(reference)
        if path.stat().st_size > 10 * 1024 * 1024:
            raise ValueError("Reference exceeds the 10 MiB workbench limit")
        raw = path.read_bytes()
        if raw.startswith(b"\x89PNG\r\n\x1a\n"):
            mime = "image/png"
        elif raw.startswith(b"\xff\xd8\xff"):
            mime = "image/jpeg"
        elif raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
            mime = "image/webp"
        else:
            raise ValueError("Reference signature must be PNG, JPEG or WebP")
        body["image"] = f"data:{mime};base64," + base64.b64encode(raw).decode("ascii")
        summary.update(output_sizing="reference-aspect-1024-area", reference_bytes=len(raw))
    return body, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rewrite", type=Path, help="Final rewrite JSON; no markdown wrapper")
    parser.add_argument("--out", type=Path, required=True, help="New local request JSON; never overwrites")
    parser.add_argument("--mode", choices=["t2i", "edit"], default="t2i")
    parser.add_argument("--quality", choices=["standard", "high"], default="standard")
    for name in ("width", "height", "steps", "seed"):
        parser.add_argument("--" + name, type=int)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--transparent", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.rewrite.read_text(encoding="utf-8"))
        body, summary = prepare(data, mode=args.mode, quality=args.quality, width=args.width,
                                height=args.height, steps=args.steps, seed=args.seed,
                                reference=args.reference, transparent=args.transparent)
        encoded = json.dumps(body, ensure_ascii=False, indent=2) + "\n"
        fd = os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(encoded)
        print(json.dumps({"output": str(args.out.resolve()), **summary}, ensure_ascii=False))
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
