#!/usr/bin/env python3
"""Snapshot an RTL tree and compute the RTL code-change percentage.

Counting rule: nonblank, non-comment lines of RTL source files (.v .vh .sv .svh .vhd .vhdl).
Comments removed: '//' and '/* */' for Verilog/SystemVerilog, '--' for VHDL.
Change percentage = (added + deleted) / baseline lines * 100, where a replaced line counts
once as deleted and once as added. Added/deleted lines come from a multiset comparison of
normalized code lines per file (whitespace-collapsed), so pure reordering is not counted.
Uses only the Python standard library; never modifies the RTL tree.

Usage:
  python rtl_change_metrics.py snapshot <RTL_DIR> <SNAPSHOT_DIR>   # run BEFORE any edit
  python rtl_change_metrics.py compare  <SNAPSHOT_DIR> <RTL_DIR> [--json]
"""

import argparse
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

RTL_SUFFIXES = {".v", ".vh", ".sv", ".svh", ".vhd", ".vhdl"}
BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)


def code_lines(path):
    """Return normalized nonblank, non-comment lines of one RTL file."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() in {".vhd", ".vhdl"}:
        stripped = [re.sub(r"--.*$", "", line) for line in text.splitlines()]
    else:
        text = BLOCK_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)
        stripped = [re.sub(r"//.*$", "", line) for line in text.splitlines()]
    return [" ".join(line.split()) for line in stripped if line.strip()]


def rtl_files(root):
    return {
        p.relative_to(root).as_posix(): p
        for p in sorted(root.rglob("*"))
        if p.is_file() and p.suffix.lower() in RTL_SUFFIXES
    }


def snapshot(source, target):
    if target.exists() and any(target.iterdir()):
        print(f"error: snapshot directory '{target}' is not empty", file=sys.stderr)
        return 2
    files = rtl_files(source)
    for rel, path in files.items():
        destination = target / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
    print(f"snapshot: {len(files)} RTL files copied to {target}")
    return 0


def compare(base_dir, new_dir, as_json):
    base, new = rtl_files(base_dir), rtl_files(new_dir)
    baseline_total, added_total, deleted_total = 0, 0, 0
    changed = []
    for rel in sorted(set(base) | set(new)):
        before = Counter(code_lines(base[rel])) if rel in base else Counter()
        after = Counter(code_lines(new[rel])) if rel in new else Counter()
        baseline_total += sum(before.values())
        added = sum((after - before).values())
        deleted = sum((before - after).values())
        added_total += added
        deleted_total += deleted
        if added or deleted:
            status = "new" if rel not in base else "removed" if rel not in new else "modified"
            changed.append({"file": rel, "status": status, "added": added, "deleted": deleted})
    percentage = None if baseline_total == 0 else (added_total + deleted_total) / baseline_total * 100
    result = {
        "baseline_code_lines": baseline_total,
        "added_code_lines": added_total,
        "deleted_code_lines": deleted_total,
        "change_percentage": None if percentage is None else round(percentage, 2),
        "changed_files": changed,
    }
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"baseline RTL code lines: {baseline_total}")
        print(f"added: {added_total}  deleted: {deleted_total}")
        print("change percentage: " + ("unavailable (empty baseline)" if percentage is None else f"{percentage:.2f}%"))
        for item in changed:
            print(f"  {item['status']:9s} {item['file']}  +{item['added']} -{item['deleted']}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    snap = sub.add_parser("snapshot")
    snap.add_argument("rtl_dir")
    snap.add_argument("snapshot_dir")
    comp = sub.add_parser("compare")
    comp.add_argument("snapshot_dir")
    comp.add_argument("rtl_dir")
    comp.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.command == "snapshot":
        return snapshot(Path(args.rtl_dir), Path(args.snapshot_dir))
    return compare(Path(args.snapshot_dir), Path(args.rtl_dir), args.json)


if __name__ == "__main__":
    sys.exit(main())
