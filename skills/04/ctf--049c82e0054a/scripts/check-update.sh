#!/usr/bin/env bash
# Version check for ctf-super-hub, mirroring dbskill's check-update.sh design:
# reads the official UPDATE.json from GitHub, at most one network request per
# 24h (cached), prints a reminder ONLY when a newer version exists, and stays
# completely silent on failure/timeout so routing is never disturbed.
#
# Usage: check-update.sh <local_version>
# Env overrides (for testing): CTF_UPDATE_URL, CTF_UPDATE_CACHE_DIR
set -u

LOCAL_VERSION="${1:-}"
[ -n "$LOCAL_VERSION" ] || exit 0

CACHE_DIR="${CTF_UPDATE_CACHE_DIR:-$HOME/.cache/ctf-super-hub}"
CACHE_FILE="$CACHE_DIR/update_check_at"
NOW="$(date +%s)"

if [ -f "$CACHE_FILE" ]; then
  LAST="$(cat "$CACHE_FILE" 2>/dev/null)"
  case "$LAST" in ''|*[!0-9]*) LAST=0 ;; esac
  [ $((NOW - LAST)) -lt 86400 ] && exit 0
fi

URL="${CTF_UPDATE_URL:-https://raw.githubusercontent.com/asdfgh1445/ctf-super-hub/main/UPDATE.json}"
mkdir -p "$CACHE_DIR" 2>/dev/null || exit 0
echo "$NOW" > "$CACHE_FILE" 2>/dev/null

REMOTE="$(curl -fsSL --max-time 5 "$URL" 2>/dev/null)" || exit 0
[ -n "$REMOTE" ] || exit 0

REMOTE_VERSION="$(printf '%s' "$REMOTE" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("version","").strip())' 2>/dev/null)" || exit 0
[ -n "$REMOTE_VERSION" ] || exit 0

VERDICT="$(python3 - "$LOCAL_VERSION" "$REMOTE_VERSION" <<'PY' 2>/dev/null
import sys
def parts(v):
    out = []
    for p in v.strip().split("."):
        try:
            out.append(int(p))
        except ValueError:
            out.append(0)
    return out
l, r = parts(sys.argv[1]), parts(sys.argv[2])
print("yes" if r > l else "no")
PY
)" || exit 0
[ "$VERDICT" = "yes" ] || exit 0

NOTES="$(printf '%s' "$REMOTE" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("notes","有新版本可更新"))' 2>/dev/null)" || NOTES="有新版本可更新"
echo "🔔 ctf-super-hub 有新版本 ${REMOTE_VERSION}（当前 ${LOCAL_VERSION}）：${NOTES}。回复 1 立即更新。"
