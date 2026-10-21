#!/usr/bin/env bash
# Update the ctf-skill repo and re-sync every skill it defines to the install
# root. Refuses to run on a dirty working tree so local modifications can
# never be silently overwritten by a pull (dbskill principle: update preserves
# local work).
#
# Usage: update_skills.sh [--repo <path>] [--install-root <path>] [--dry-run]
# Env overrides: CTF_SKILL_REPO, CTF_SKILL_INSTALL
set -euo pipefail

REPO="${CTF_SKILL_REPO:-$HOME/Documents/ctf-skill/repo}"
INSTALL_ROOT="${CTF_SKILL_INSTALL:-$HOME/.agents/skills}"
DRY_RUN=0
while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --install-root) INSTALL_ROOT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

[ -d "$REPO/.git" ] || {
  echo "未找到仓库：$REPO（用 --repo 指定，或设 CTF_SKILL_REPO）" >&2
  exit 1
}
cd "$REPO"

if [ -n "$(git status --porcelain)" ]; then
  echo "工作区有未提交修改，更新已中止。先提交或 stash 后重试："
  git status --porcelain | head -20
  exit 1
fi

if [ "$DRY_RUN" = 1 ]; then
  echo "dry-run: git -C $REPO pull --ff-only，然后 rsync 各 skill 目录 -> $INSTALL_ROOT"
  exit 0
fi

git pull --ff-only

SYNCED=0
for dir in */; do
  [ -f "${dir}SKILL.md" ] || continue
  mkdir -p "$INSTALL_ROOT"
  rsync -a --delete "$dir" "$INSTALL_ROOT/${dir%/}/"
  SYNCED=$((SYNCED + 1))
done
echo "更新完成：$(git log -1 --oneline)，已同步 $SYNCED 个 skill 到 $INSTALL_ROOT"
