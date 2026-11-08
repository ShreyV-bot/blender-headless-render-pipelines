#!/usr/bin/env bash
# Assemble frame_0001.png ... into an H.264 MP4 with FFmpeg (Linux / macOS).
# Usage: ./make_video.sh [FRAMES_DIR] [FPS] [OUTPUT.mp4]
set -euo pipefail
DIR="${1:-$HOME/Temp_Render}"
FPS="${2:-60}"
OUT="${3:-$DIR/Final_Output.mp4}"
ffmpeg -framerate "$FPS" -i "$DIR/frame_%04d.png" -c:v libx264 -pix_fmt yuv420p -crf 18 "$OUT"
