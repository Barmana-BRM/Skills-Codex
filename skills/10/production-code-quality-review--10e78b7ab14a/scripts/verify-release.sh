#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_DIR="${1:-$PWD}"
export PYTHONDONTWRITEBYTECODE=1

echo "[1/6] Running unit tests"
python3 -m unittest discover "$ROOT_DIR/tests" -v

echo "[2/6] Collecting structured review context"
python3 "$ROOT_DIR/scripts/collect-review-context.py" --repo "$REPO_DIR"

echo "[3/6] Suggesting safe verification commands"
python3 "$ROOT_DIR/scripts/run-safe-checks.py" --repo "$REPO_DIR"

echo "[4/6] Generating compact review summary"
python3 "$ROOT_DIR/scripts/review-entrypoint.py" --repo "$REPO_DIR" --format compact

echo "[5/6] Verifying local install helper"
bash "$ROOT_DIR/scripts/install-local-skill.sh"

echo "[6/6] Verifying local update helper"
bash "$ROOT_DIR/scripts/update-local-skill.sh"

echo "Release verification completed successfully."
