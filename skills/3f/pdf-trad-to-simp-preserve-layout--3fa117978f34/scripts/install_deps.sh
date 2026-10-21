#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="${1:-$SKILL_DIR/.venv}"

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r "$SCRIPT_DIR/requirements.txt"

printf 'Virtualenv ready at %s\n' "$VENV_DIR"
printf "Activate it with: source '%s/bin/activate'\n" "$VENV_DIR"
