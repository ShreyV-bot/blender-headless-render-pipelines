# Backfilling Missing Frames & Assembling the MP4

## Check for gaps and empty placeholders first

Stop all workers, then remove 0-byte PNGs and re-run one worker over the full range. Frames that already exist are skipped (`use_overwrite = False`).

```text
# Windows PowerShell
.\tools\cleanup_placeholders.ps1 -Dir "C:\Temp_Render"

# Linux / macOS
./tools/cleanup_placeholders.sh "$HOME/Temp_Render"
```

## Backfilling missing even frames

If an early run rendered only odd frames, target only the even ones using a start frame of 2 and a step (jump) of 2:

```text
"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe" -b --factory-startup ^
  "C:\Path\To\Your_Scene.blend" ^
  -P "C:\Temp_Render\method1_gpu_worker.py" -t 2 -s 2 -e 244 -j 2 -a
```

## FFmpeg (fastest)

```text
# Full 4,440 sequential frames at 60 FPS (Windows):
ffmpeg -framerate 60 -i "C:/Temp_Render/frame_%04d.png" ^
  -c:v libx264 -pix_fmt yuv420p -crf 18 "C:/Temp_Render/Final_Animation_60fps.mp4"

# Odd-only frames (1, 3, 5... = 2,220 frames) at 30 FPS on Linux/macOS:
ffmpeg -framerate 30 -pattern_type glob -i "$HOME/Temp_Render/frame_*.png" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 "$HOME/Temp_Render/Final_Animation_30fps.mp4"
```

Or use the helper scripts: `tools/make_video.sh [DIR] [FPS] [OUTPUT]` (Linux/macOS) and `tools/make_video.bat [DIR] [FPS] [OUTPUT]` (Windows).

## Blender only (no FFmpeg installed)

```text
blender -b --factory-startup -P tools/make_video_blender.py
```

Edit `FRAMES_DIR` and `FPS` at the top of the script. It reads the first frame's size so the video matches your rendered resolution (for example 960×540 at 50% scale), and it supports both the older `sequences` and newer `strips` sequencer API names.

> **Note:** the Blender-only route adds frames in sorted filename order. If your numbering has gaps, the video will skip over them without leaving a blank frame, so fill the gaps first.
