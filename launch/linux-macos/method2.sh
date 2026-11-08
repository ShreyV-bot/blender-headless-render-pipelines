#!/usr/bin/env bash
# Method 2 - Low-RAM CPU-capped Cycles
# Usage: ./method2.sh /path/to/Your_Scene.blend [START_FRAME] [END_FRAME]
# macOS: export BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
set -euo pipefail
BLENDER="${BLENDER:-blender}"
SCENE="${1:?Usage: $0 /path/to/Your_Scene.blend [START_FRAME] [END_FRAME]}"
START="${2:-1}"
END="${3:-4440}"
SECOND_START=$((START + 1))
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS="$HERE/../../scripts"

"$BLENDER" -b --factory-startup "$SCENE" -P "$SCRIPTS/method2_cycles_low_ram.py" -t 8 -s "$START" -e "$END" -j 1 -a
