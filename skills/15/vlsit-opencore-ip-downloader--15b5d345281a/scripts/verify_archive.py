#!/usr/bin/env python3
"""Check a downloaded .zip/.tar* archive before extraction and record its SHA-256.

Checks: archive integrity, unsafe member paths (absolute, drive-letter, '..'),
link members that escape the archive root, and presence of license/README files.
The script only reads the archive; it never extracts or executes anything.
Uses only the Python standard library.

Usage: python verify_archive.py <ARCHIVE> [--json]
Exit code: 0 = no blocking finding, 1 = integrity or path-safety failure, 2 = usage error.
"""

import argparse
import hashlib
import json
import posixpath
import sys
import tarfile
import zipfile
from pathlib import Path

LICENSE_HINTS = ("license", "licence", "copying", "copyright")
README_HINTS = ("readme",)


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unsafe_path(name):
    """Return a reason string when a member name could escape the extraction root."""
    normalized = name.replace("\\", "/")
    if normalized.startswith("/") or (len(normalized) > 1 and normalized[1] == ":"):
        return "absolute path"
    if ".." in posixpath.normpath(normalized).split("/"):
        return "parent-directory traversal"
    return None


def inspect_zip(path):
    findings, names = [], []
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad is not None:
            findings.append(f"integrity failure: first bad member is '{bad}'")
        for info in archive.infolist():
            names.append(info.filename)
            reason = unsafe_path(info.filename)
            if reason:
                findings.append(f"unsafe member '{info.filename}': {reason}")
    return findings, names


def inspect_tar(path):
    findings, names = [], []
    with tarfile.open(path) as archive:
        for member in archive:  # iterating forces a full stream read, which detects truncation
            names.append(member.name)
            reason = unsafe_path(member.name)
            if reason:
                findings.append(f"unsafe member '{member.name}': {reason}")
            if member.issym() or member.islnk():
                base = posixpath.dirname(member.name)
                target = member.linkname if member.islnk() else posixpath.join(base, member.linkname)
                if unsafe_path(target):
                    findings.append(f"link '{member.name}' -> '{member.linkname}' escapes the archive root")
            if member.isdev():
                findings.append(f"device member '{member.name}'")
    return findings, names


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("archive")
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    args = parser.parse_args()

    path = Path(args.archive)
    if not path.is_file():
        print(f"error: '{path}' is not a file", file=sys.stderr)
        return 2

    try:
        if zipfile.is_zipfile(path):
            kind, (findings, names) = "zip", inspect_zip(path)
        elif tarfile.is_tarfile(path):
            kind, (findings, names) = "tar", inspect_tar(path)
        else:
            print("error: unsupported archive type (expected zip or tar)", file=sys.stderr)
            return 2
    except (zipfile.BadZipFile, tarfile.TarError, OSError, EOFError) as exc:
        kind, names, findings = "unknown", [], [f"integrity failure: {exc}"]

    lowered = [posixpath.basename(n.replace("\\", "/")).lower() for n in names]
    result = {
        "archive": str(path),
        "type": kind,
        "size_bytes": path.stat().st_size,
        "sha256": sha256_of(path),
        "member_count": len(names),
        "has_license_file": any(b.startswith(LICENSE_HINTS) for b in lowered),
        "has_readme_file": any(b.startswith(README_HINTS) for b in lowered),
        "blocking_findings": findings,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            if key != "blocking_findings":
                print(f"{key}: {value}")
        print("blocking_findings: " + ("none" if not findings else ""))
        for finding in findings:
            print(f"  - {finding}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
