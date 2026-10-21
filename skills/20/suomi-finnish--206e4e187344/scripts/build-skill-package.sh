#!/usr/bin/env bash
# Rakentaa jaettavan skill-paketin dist/suomi-finnish.zip.
#
# Paketin juuressa on kansio suomi-finnish/, jonka sisällä SKILL.md ja
# references/. Tämä on muoto, jonka claude.ai hyväksyy skillin tuonnissa
# (Asetukset > Skills > Create skill).
#
# Aja repon juuresta:  ./scripts/build-skill-package.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="suomi-finnish"
DIST="$ROOT/dist"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

# Pidä koontiversio ajan tasalla ennen paketointia.
python3 "$ROOT/scripts/build-single-file.py" >/dev/null

mkdir -p "$STAGE/$NAME"
cp "$ROOT/SKILL.md" "$STAGE/$NAME/"
cp -R "$ROOT/references" "$STAGE/$NAME/"

mkdir -p "$DIST"
rm -f "$DIST/$NAME.zip"
( cd "$STAGE" && zip -q -r -X "$DIST/$NAME.zip" "$NAME" )

echo "Rakennettu: dist/$NAME.zip"
unzip -l "$DIST/$NAME.zip" | sed -n '4,$p'
