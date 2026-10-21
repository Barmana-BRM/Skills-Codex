#!/usr/bin/env python3
"""Discover which skills from this repo are actually installed.

The router (ctf-super-hub) calls this instead of trusting a hardcoded list,
so a stale or partially-updated install can never steer routing. Mirrors the
dynamic-discovery pattern of dbskill's list-official-skills.py.

Usage (from the router, any context):
    python3 "<this skill dir>/scripts/list-installed-skills.py"

Context handling:
- Repo mode (repo root with SKILL-INDEX.md two levels up): enumerate the
  repo's own skill directories and report each one's install status.
- Install mode (running from ~/.agents/skills or similar): scan install roots
  for this repo's namespace (ctf-*, strix-*, solve-challenge, brainstorming),
  union with the bundled snapshot so renamed/retired skills still surface.

Output: one markdown line per skill with its installed path and description,
or a `MISSING:` line when the skill is not installed.
"""

import argparse
import json
import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INSTALL_ROOTS = [
    os.path.expanduser("~/.agents/skills"),
    os.path.expanduser("~/.zcode/skills"),
    os.path.expanduser("~/.claude/skills"),
]
NAMESPACE_RE = re.compile(r"^(ctf-|strix-|solve-challenge$|brainstorming$)")

# Offline fallback: authoritative snapshot of this repo's skills. Skills added
# upstream are still discovered in install mode via the namespace scan.
FALLBACK_SKILLS = [
    "brainstorming", "solve-challenge",
    "ctf-ai-ml", "ctf-beginner-hub", "ctf-crypto", "ctf-forensics",
    "ctf-malware", "ctf-misc", "ctf-osint", "ctf-pwn", "ctf-reverse",
    "ctf-super-hub", "ctf-web", "ctf-writeup",
    "strix-authentication-jwt", "strix-beginner-hub",
    "strix-broken-function-level-authorization", "strix-business-logic",
    "strix-csrf", "strix-ffuf", "strix-httpx", "strix-idor",
    "strix-insecure-file-uploads", "strix-information-disclosure",
    "strix-katana", "strix-nuclei", "strix-open-redirect",
    "strix-path-traversal-lfi-rfi", "strix-quick", "strix-rce",
    "strix-sql-injection", "strix-sqlmap", "strix-ssrf", "strix-standard",
    "strix-xss",
]

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
DESC_RE = re.compile(r'^description:\s*"?(.+?)"?\s*$', re.M)


def in_repo_mode():
    return os.path.isfile(os.path.join(REPO_ROOT, "SKILL-INDEX.md"))


def repo_skill_names():
    found = []
    try:
        for entry in sorted(os.listdir(REPO_ROOT)):
            if os.path.isfile(os.path.join(REPO_ROOT, entry, "SKILL.md")):
                found.append(entry)
    except OSError:
        pass
    return found


def installed_namespace_names():
    """Skills in install roots matching this repo's namespace."""
    names = set()
    for root in INSTALL_ROOTS:
        try:
            for entry in os.listdir(root):
                if NAMESPACE_RE.match(entry) and os.path.isfile(
                        os.path.join(root, entry, "SKILL.md")):
                    names.add(entry)
        except OSError:
            continue
    return names


def read_description(skill_md_path):
    try:
        with open(skill_md_path, encoding="utf-8") as fh:
            match = FRONTMATTER_RE.match(fh.read(8192))
        if not match:
            return ""
        desc = DESC_RE.search(match.group(1))
        return desc.group(1).strip().strip('"') if desc else ""
    except OSError:
        return ""


def find_installed(name):
    for root in INSTALL_ROOTS:
        candidate = os.path.join(root, name, "SKILL.md")
        if os.path.isfile(candidate):
            return candidate
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    args = parser.parse_args()

    if in_repo_mode():
        names = repo_skill_names()
    else:
        installed = installed_namespace_names()
        names = sorted(set(FALLBACK_SKILLS) | installed)
    if not names:
        names = FALLBACK_SKILLS

    results = []
    for name in names:
        path = find_installed(name)
        results.append({
            "name": name,
            "installed": path is not None,
            "path": path or "",
            "description": read_description(path) if path else "",
        })

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    missing = 0
    for item in results:
        if item["installed"]:
            desc = item["description"]
            # Trim long descriptions to keep router output compact.
            if len(desc) > 120:
                desc = desc[:117] + "..."
            print(f"- `{item['name']}` — {desc}")
        else:
            missing += 1
            print(f"- MISSING: `{item['name']}` — defined but not installed")
    if missing:
        print(f"\n{missing} skill(s) missing from install roots; route only to installed skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
