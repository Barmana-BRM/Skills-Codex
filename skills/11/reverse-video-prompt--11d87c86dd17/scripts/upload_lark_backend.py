#!/usr/bin/env python3
"""Upload reverse-video-prompt iteration data to a configured Lark Base.

This script requires an explicit local config. It does not contain credentials.
Attachment uploads are performed via lark-cli and use relative file paths from
the file's parent directory to satisfy lark-cli path safety rules.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = SKILL_DIR / "config" / "lark-backend.local.json"
REQUIRED_FIELD_KEYS = [
    "original_video",
    "prompt_1",
    "replica_video_1",
    "feedback_1",
    "prompt_2",
    "replica_video_2",
    "feedback_2",
]


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Lark backend config not found: {path}")
    config = json.loads(path.read_text(encoding="utf-8"))
    if not config.get("enabled"):
        raise SystemExit("Lark backend config is disabled.")
    if not config.get("consent_acknowledged"):
        raise SystemExit(
            "Lark backend consent is not acknowledged. Set consent_acknowledged=true "
            "only after the user understands what will be uploaded."
        )
    fields = config.get("fields", {})
    missing = [key for key in REQUIRED_FIELD_KEYS if key not in fields]
    if missing:
        raise SystemExit(f"Lark backend config is missing field mappings: {', '.join(missing)}")
    return config


def run_json(cmd: list[str], cwd: Path | None = None) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise SystemExit(
            f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr or proc.stdout}"
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Expected JSON output, got:\n{proc.stdout}") from exc


def read_value(text: str | None, file_path: str | None) -> str | None:
    if text and file_path:
        raise SystemExit("Use either inline text or file input, not both.")
    if file_path:
        return Path(file_path).expanduser().read_text(encoding="utf-8")
    return text


def build_text_payload(args: argparse.Namespace, fields: dict[str, str]) -> dict[str, str]:
    payload: dict[str, str] = {}
    text_items = [
        ("prompt_1", read_value(args.prompt_1, args.prompt_1_file)),
        ("feedback_1", read_value(args.feedback_1, args.feedback_1_file)),
        ("prompt_2", read_value(args.prompt_2, args.prompt_2_file)),
        ("feedback_2", read_value(args.feedback_2, args.feedback_2_file)),
    ]
    for key, value in text_items:
        if value is not None:
            payload[fields[key]] = value
    return payload


def requested_attachments(args: argparse.Namespace) -> list[tuple[str, str | None]]:
    return [
        ("original_video", args.original_video),
        ("replica_video_1", args.replica_video_1),
        ("replica_video_2", args.replica_video_2),
    ]


def upsert_record(config: dict[str, Any], record_id: str | None, payload: dict[str, str]) -> str:
    cmd = [
        "lark-cli",
        "base",
        "+record-upsert",
        "--as",
        "user",
        "--base-token",
        config["base_token"],
        "--table-id",
        config["table_id"],
        "--json",
        json.dumps(payload, ensure_ascii=False),
    ]
    if record_id:
        cmd.extend(["--record-id", record_id])
    result = run_json(cmd)
    record = result.get("data", {}).get("record", {})
    found = record.get("record_id") or record.get("id") or record_id
    if not found:
        raise SystemExit(f"Could not find record id in lark-cli output:\n{json.dumps(result, ensure_ascii=False)}")
    return found


def upload_attachment(config: dict[str, Any], record_id: str, field_id: str, file_path: str) -> None:
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"Attachment file not found: {path}")
    cmd = [
        "lark-cli",
        "base",
        "+record-upload-attachment",
        "--as",
        "user",
        "--base-token",
        config["base_token"],
        "--table-id",
        config["table_id"],
        "--record-id",
        record_id,
        "--field-id",
        field_id,
        "--file",
        path.name,
    ]
    run_json(cmd, cwd=path.parent)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload reverse-video-prompt data to Lark Base.")
    parser.add_argument("--config", default=os.environ.get("REVERSE_VIDEO_PROMPT_LARK_CONFIG", str(DEFAULT_CONFIG)))
    parser.add_argument("--record-id", help="Existing record id. Omit to create a new record.")
    parser.add_argument("--original-video")
    parser.add_argument("--prompt-1")
    parser.add_argument("--prompt-1-file")
    parser.add_argument("--replica-video-1")
    parser.add_argument("--feedback-1")
    parser.add_argument("--feedback-1-file")
    parser.add_argument("--prompt-2")
    parser.add_argument("--prompt-2-file")
    parser.add_argument("--replica-video-2")
    parser.add_argument("--feedback-2")
    parser.add_argument("--feedback-2-file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(Path(args.config).expanduser())
    fields = config["fields"]
    payload = build_text_payload(args, fields)
    attachments = requested_attachments(args)
    if not payload and not any(file_path for _, file_path in attachments):
        raise SystemExit("Nothing to upload. Provide at least one video, prompt, or feedback value.")

    # Create an empty row if this upload only contains attachments.
    record_id = upsert_record(config, args.record_id, payload)

    for key, file_path in attachments:
        if file_path:
            upload_attachment(config, record_id, fields[key], file_path)

    print(json.dumps({"ok": True, "record_id": record_id}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
