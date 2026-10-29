#!/usr/bin/env bash
# Downloads a Mine Mine no Mi release and decompiles it into .reference/ (git-ignored).
# The MMnM license allows decompiling for private use only, so nothing here is committed.
# Usage: tools/setup-reference.sh [version]   e.g. tools/setup-reference.sh 1.20.1-0.11.6
set -euo pipefail

VERSION="${1:-1.20.1-0.11.6}"
VINEFLOWER_VERSION="1.11.1"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REF="$ROOT/.reference/$VERSION"

mkdir -p "$REF" "$ROOT/.reference/tools"

VF="$ROOT/.reference/tools/vineflower-$VINEFLOWER_VERSION.jar"
if [ ! -s "$VF" ]; then
  curl -sSLo "$VF" "https://github.com/Vineflower/vineflower/releases/download/$VINEFLOWER_VERSION/vineflower-$VINEFLOWER_VERSION.jar"
fi

JAR="$REF/mine-mine-no-mi-$VERSION.jar"
if [ ! -s "$JAR" ]; then
  URL=$(curl -sS 'https://api.modrinth.com/v2/project/mine-mine-no-mi/version' \
    | jq -r --arg v "$VERSION" '.[] | select(.version_number == $v) | .files[0].url')
  [ -n "$URL" ] || { echo "Version $VERSION not found on Modrinth" >&2; exit 1; }
  curl -sSLo "$JAR" "$URL"
fi

mkdir -p "$REF/jar" "$REF/src"
unzip -qo "$JAR" -d "$REF/jar"
java -jar "$VF" -dgs=1 -log=WARN "$JAR" "$REF/src" > "$REF/decompile.log" 2>&1

echo "Decompiled to $REF/src (data files in $REF/jar)"
