#!/usr/bin/env python3
"""Build a deterministic X search plan from a TSV query file."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


VALID_SORTS = {"latest": "live", "top": "top"}


def positive_int(value: str, *, field: str, line_no: int) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"line {line_no}: {field} must be an integer") from exc
    if parsed < 1:
        raise ValueError(f"line {line_no}: {field} must be >= 1")
    return parsed


def load_queries(path: Path, default_max_rows: int) -> list[dict[str, object]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not reader.fieldnames or "query" not in reader.fieldnames:
            raise ValueError("query TSV must contain a 'query' column")
        tasks: list[dict[str, object]] = []
        seen: set[tuple[str, str]] = set()
        for line_no, row in enumerate(reader, 2):
            query = (row.get("query") or "").strip()
            if not query:
                continue
            lang = (row.get("lang") or "UNK").strip().upper()
            round_no = positive_int((row.get("round") or "1").strip(), field="round", line_no=line_no)
            max_rows = positive_int(
                (row.get("max_rows") or str(default_max_rows)).strip(),
                field="max_rows",
                line_no=line_no,
            )
            sort = (row.get("sort") or "latest").strip().lower()
            if sort not in VALID_SORTS:
                raise ValueError(f"line {line_no}: sort must be latest or top")
            key = (query.casefold(), sort)
            if key in seen:
                raise ValueError(f"line {line_no}: duplicate query/sort pair")
            seen.add(key)
            index = len(tasks) + 1
            tasks.append(
                {
                    "task_id": f"{index:03d}",
                    "query": query,
                    "lang": lang,
                    "round": round_no,
                    "max_rows": max_rows,
                    "sort": sort,
                    "search_url": (
                        "https://x.com/search?q="
                        f"{quote(query, safe='')}&src=typed_query&f={VALID_SORTS[sort]}"
                    ),
                    "source_file": f"{index:03d}_{lang}.json",
                    "status": "pending",
                }
            )
    if not tasks:
        raise ValueError("query TSV contains no usable rows")
    return tasks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queries", required=True, type=Path, help="TSV with query/lang/round/max_rows/sort")
    parser.add_argument("--output", required=True, type=Path, help="Output request plan JSON")
    parser.add_argument("--default-max-rows", type=int, default=250)
    args = parser.parse_args()
    if args.default_max_rows < 1:
        parser.error("--default-max-rows must be >= 1")
    try:
        tasks = load_queries(args.queries, args.default_max_rows)
    except ValueError as exc:
        parser.error(str(exc))
    plan = {
        "platform": "X",
        "method": "chrome_dom_visible_ui",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tasks": tasks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(tasks)} tasks to {args.output}")


if __name__ == "__main__":
    main()

