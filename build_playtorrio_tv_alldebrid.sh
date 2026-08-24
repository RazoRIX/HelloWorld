#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${1:-PlayTorrioTV-AllDebrid}"

python3 "$SCRIPT_DIR/apply_alldebrid.py" --clone "$DEST"
cd "$DEST"
flutter pub get
flutter build apk --release --split-per-abi

echo
echo "Build complete. APKs:"
find build/app/outputs/flutter-apk -maxdepth 1 -type f -name '*-release.apk' -print || true
