#!/usr/bin/env bash
# Remove 0-byte placeholder PNGs left behind by an interrupted render (Linux / macOS).
# IMPORTANT: run this ONLY after every Blender worker has stopped. While a render is running,
# in-progress frames are 0-byte placeholders on purpose, and deleting them breaks the lock system.
set -euo pipefail
DIR="${1:-$HOME/Temp_Render}"
find "$DIR" -maxdepth 1 -name "*.png" -size 0 -print -delete
echo "Done. Re-run one worker (e.g. -s 1 -e 4440 -j 1 -a) to fill any gaps."
