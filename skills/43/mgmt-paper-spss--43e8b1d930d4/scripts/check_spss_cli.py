#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


MAC_CANDIDATES = [
    "/Applications/IBM SPSS Statistics/SPSS Statistics.app/Contents/MacOS/stats",
    "/Applications/IBM SPSS Statistics 29/SPSS Statistics.app/Contents/MacOS/stats",
    "/Applications/IBM SPSS Statistics 30/SPSS Statistics.app/Contents/MacOS/stats",
]


def find_spss() -> list[str]:
    found = [path for name in ["spss", "stats", "SPSS"] if (path := shutil.which(name))]
    found.extend(path for path in MAC_CANDIDATES if Path(path).exists())
    return sorted(dict.fromkeys(found))


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect SPSS CLI and optionally run a syntax smoke test.")
    parser.add_argument("--syntax", type=Path, help="Optional .sps file to run.")
    parser.add_argument("--executable", help="Explicit SPSS executable path.")
    args = parser.parse_args()

    candidates = [args.executable] if args.executable else find_spss()
    if not candidates:
        print("SPSS executable not found.")
        return 2
    executable = candidates[0]
    print(f"SPSS executable: {executable}")
    if args.syntax:
        proc = subprocess.run([executable, "-f", str(args.syntax.resolve())], text=True, capture_output=True, check=False)
        print(proc.stdout)
        print(proc.stderr)
        return proc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

