#!/usr/bin/env bash
# Method 1 - Dedicated GPU-only EEVEE Next worker
# Usage: ./method1.sh /path/to/Your_Scene.blend [START_FRAME] [END_FRAME]
# macOS: export BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
set -euo pipefail
BLENDER="${BLENDER:-blender}"
SCENE="${1:?Usage: $0 /path/to/Your_Scene.blend [START_FRAME] [END_FRAME]}"
START="${2:-1}"
END="${3:-4440}"
SECOND_START=$((START + 1))
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS="$HERE/../../scripts"

"$BLENDER" -b --factory-startup "$SCENE" -P "$SCRIPTS/method1_gpu_worker.py" -t 2 -s "$START" -e "$END" -j 1 -a
