#!/usr/bin/env bash
# Builds jlisa-wit.zip, the archive to upload to Zenodo for SV-COMP.
# The wrapper and the validator jars are packed into the single executable jlisa-wit.
set -euo pipefail

SVCOMP="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SVCOMP")"
LIB="$ROOT/build/install/jlisa-witness-validator/lib"
OUT="$ROOT/build/svcomp"

(cd "$ROOT" && ./gradlew installDist "$@")

rm -rf "$OUT" && mkdir -p "$OUT/jlisa-wit"
python3 -m venv "$OUT/venv"
"$OUT/venv/bin/pip" install -q pyinstaller
"$OUT/venv/bin/pyinstaller" "$SVCOMP/jlisa-wit.py" --onefile --clean --strip \
  --name jlisa-wit --add-data "$LIB:lib" \
  --distpath "$OUT/jlisa-wit" --workpath "$OUT/pyinstaller" --specpath "$OUT/pyinstaller"

cp -r "$SVCOMP/test" "$SVCOMP/smoketest.sh" "$SVCOMP/README.md" "$SVCOMP/LICENSE" "$OUT/jlisa-wit/"
(cd "$OUT" && zip -qr jlisa-wit.zip jlisa-wit)

"$SVCOMP/check-release.sh" "$OUT/jlisa-wit.zip"
