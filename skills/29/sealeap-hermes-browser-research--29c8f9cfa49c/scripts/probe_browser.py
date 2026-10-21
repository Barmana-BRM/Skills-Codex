#!/usr/bin/env python3
"""Inspect an installed CLI's help; never install, browse, or read profiles."""
import argparse
import json
import shutil
import subprocess


def classify(help_text):
    lowered = help_text.lower()
    if 'page_info' in lowered or 'new_tab(' in lowered:
        return 'python-helpers'
    if '--session' in lowered and 'open' in lowered and 'state' in lowered:
        return 'legacy-session-cli'
    return 'inspect-help-manually'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    binary = shutil.which('browser-use')
    result = {'browser_use_installed': bool(binary), 'browser_mcp': 'inspect-current-tool-inventory',
              'live_browser_verified': False, 'navigation_performed': False}
    if not binary:
        result.update(status='HOLD', reason='CLI not on PATH; use an available browser tool or authorized setup')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2
    try:
        proc = subprocess.run([binary, '--help'], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        result.update(status='HOLD', reason='CLI help unavailable')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2
    result.update(status='HELP_CHECKED' if proc.returncode == 0 else 'HOLD',
                  cli_help_exit_code=proc.returncode,
                  interface_hint=classify(proc.stdout + '\n' + proc.stderr))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if proc.returncode == 0 else 2


if __name__ == '__main__':
    raise SystemExit(main())
