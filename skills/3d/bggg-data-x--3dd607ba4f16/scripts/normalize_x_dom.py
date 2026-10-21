#!/usr/bin/env python3
"""Normalize X query packages captured from rendered Chrome DOM into JSONL."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


METRIC_PATTERNS = {
    "replies": r"([\d,.]+[KM]?)\s+repl(?:y|ies)",
    "reposts": r"([\d,.]+[KM]?)\s+reposts?",
    "likes": r"([\d,.]+[KM]?)\s+likes?",
    "bookmarks": r"([\d,.]+[KM]?)\s+bookmarks?",
    "views": r"([\d,.]+[KM]?)\s+views?",
}


def metric_number(value: str) -> int:
    cleaned = value.replace(",", "").strip().upper()
    multiplier = 1
    if cleaned.endswith("K"):
        multiplier, cleaned = 1_000, cleaned[:-1]
    elif cleaned.endswith("M"):
        multiplier, cleaned = 1_000_000, cleaned[:-1]
    try:
        return int(float(cleaned) * multiplier)
    except ValueError:
        return 0


def parse_engagement(raw: str) -> dict[str, int]:
    parsed: dict[str, int] = {}
    for name, pattern in METRIC_PATTERNS.items():
        match = re.search(pattern, raw or "", flags=re.I)
        parsed[name] = metric_number(match.group(1)) if match else 0
    return parsed


def read_keywords(path: Path | None) -> list[str]:
    if path is None:
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def source_id(native_id: str | None, url: str, text: str) -> str:
    identity = native_id or url or text
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]


def valid_iso_date(value: Any) -> bool:
    if not value:
        return False
    try:
        datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", nargs="+", required=True, type=Path, help="Per-query JSON packages")
    parser.add_argument("--output", required=True, type=Path, help="Normalized JSONL")
    parser.add_argument("--summary", required=True, type=Path, help="Audit summary JSON")
    parser.add_argument("--keywords", type=Path, help="Optional literal keyword list")
    args = parser.parse_args()

    keywords = read_keywords(args.keywords)
    merged: dict[str, dict[str, Any]] = {}
    stats = Counter()
    query_counts: Counter[str] = Counter()
    language_observations: Counter[str] = Counter()
    dates: list[str] = []

    for path in args.inputs:
        stats["source_files"] += 1
        try:
            package = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            stats["invalid_source_files"] += 1
            print(f"warning: skipped {path}: {exc}")
            continue
        if not isinstance(package, dict) or not isinstance(package.get("rows"), list):
            stats["invalid_source_files"] += 1
            print(f"warning: skipped {path}: expected object with rows[]")
            continue
        query = str(package.get("query") or "").strip()
        lang = str(package.get("lang") or "UNK").strip().upper()
        round_no = int(package.get("round") or 1)
        collected_at = package.get("collected_at")
        for raw_row in package["rows"]:
            stats["observations"] += 1
            if not isinstance(raw_row, dict):
                stats["invalid_rows"] += 1
                continue
            text = str(raw_row.get("text_raw") or "").strip()
            native_id = str(raw_row.get("native_id") or "").strip() or None
            url = str(raw_row.get("url") or "").strip()
            if not text:
                stats["missing_text"] += 1
                continue
            if not native_id and not url:
                stats["missing_identity"] += 1
                continue
            if native_id and not re.fullmatch(r"\d+", native_id):
                stats["invalid_native_id"] += 1
                continue
            date = raw_row.get("date")
            if date and not valid_iso_date(date):
                stats["invalid_date"] += 1
                date = None
            if date:
                dates.append(str(date))
            raw_engagement = str(raw_row.get("engagement_raw") or "")
            key = native_id or url
            row = merged.get(key)
            if row is None:
                hits = [term for term in keywords if term.casefold() in text.casefold()]
                row = {
                    "platform": "X",
                    "lang": lang,
                    "source_id": source_id(native_id, url, text),
                    "native_id": native_id,
                    "date": date,
                    "text_raw": text,
                    "engagement": {"raw": raw_engagement, **parse_engagement(raw_engagement)},
                    "context": {
                        "content_type": "post",
                        "author_handle": raw_row.get("author_handle"),
                        "author_display_raw": raw_row.get("author_display_raw"),
                        "url": url,
                        "queries": [],
                        "query_langs": [],
                        "text_lang_attr": raw_row.get("text_lang_attr"),
                        "source_route": "chrome_dom_visible_ui",
                        "card_text_raw": raw_row.get("card_text_raw"),
                        "collected_at": raw_row.get("collected_at") or collected_at,
                        "source_files": [],
                    },
                    "keyword_hit": hits,
                    "round": round_no,
                }
                merged[key] = row
            else:
                stats["duplicate_observations"] += 1
                if len(text) > len(str(row["text_raw"])):
                    row["text_raw"] = text
                old = row["engagement"]
                new = parse_engagement(raw_engagement)
                for metric, value in new.items():
                    old[metric] = max(int(old.get(metric) or 0), value)
                row["round"] = min(int(row["round"]), round_no)
            context = row["context"]
            if query and query not in context["queries"]:
                context["queries"].append(query)
            if lang not in context["query_langs"]:
                context["query_langs"].append(lang)
            source_path = str(path)
            if source_path not in context["source_files"]:
                context["source_files"].append(source_path)
            query_counts[query or "(missing)"] += 1
            language_observations[lang] += 1

    rows = sorted(
        merged.values(),
        key=lambda row: (str(row.get("date") or ""), str(row.get("native_id") or "")),
        reverse=True,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    unique_languages = Counter(row["lang"] for row in rows)
    stats["unique_rows"] = len(rows)
    stats["missing_url"] = sum(not (row.get("context") or {}).get("url") for row in rows)
    stats["missing_date_unique"] = sum(not row.get("date") for row in rows)
    summary = {
        **dict(stats),
        "query_observations": dict(query_counts),
        "language_observations": dict(language_observations),
        "unique_rows_by_primary_lang": dict(unique_languages),
        "earliest_date": min(dates) if dates else None,
        "latest_date": max(dates) if dates else None,
        "output": str(args.output),
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} unique rows to {args.output}")


if __name__ == "__main__":
    main()

