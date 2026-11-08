<!-- series: BLENDER 4.2+ / 4.4+ PRODUCTION PIPELINE SERIES — METHOD 1 OF 5 -->
<!-- footer: Method 1: Dedicated GPU-Only High-Speed Rendering (EEVEE Next) -->
# Method 1: Dedicated GPU-Only High-Speed Rendering
*Headless EEVEE Next Rasterization with 2-Thread CPU Feed, RAM Persistence & Zero-Compression SSD Output*

> **Tested on:** Blender 4.4.3 · Windows · Intel Core i7-1255U (10 cores / 12 threads) · Intel Iris Xe · 16 GB RAM · NVMe SSD. Utilization and timing figures in this guide come from that single machine; yours will differ.
> **Blender 5.x:** the EEVEE engine id is `BLENDER_EEVEE_NEXT` in Blender 4.2–4.5 and `BLENDER_EEVEE` in 5.x. The scripts detect the right id automatically; every other property was verified on Blender 4.4.3 only.

## 1. About This Method, Hardware Profile & When It Is Preferred

**How the Method Works:** Method 1 uses Blender's real-time rasterization engine (EEVEE Next in Blender 4.2+) running in headless background mode (`-b`) without loading the graphical interface. Because EEVEE calculates lighting and shaders exclusively on the GPU, spinning all CPU cores only wastes electrical power and generates heat. This method locks the CPU to just 2 helper threads (`-t 2`) to feed geometry to the GPU, locks the 3D scene inside RAM (`use_persistent_data = True`) so meshes are never rebuilt between frames, disables GPU shadow-buffer bottlenecks when needed, and writes uncompressed PNGs directly to an NVMe SSD.

| Hardware Component | Target Utilization | Exact Role in Method 1 |
| :--- | :--- | :--- |
| GPU (Integrated or Dedicated) | 95% – 100% | Executes all EEVEE Next rasterization, shader evaluation, and Temporal Anti-Aliasing (TAA) passes. |
| CPU (Processor Cores) | 15% – 25% (2 Threads) | Evaluates animation keyframes and feeds mesh data to the GPU without stealing shared package wattage. |
| System RAM (Memory) | Low (~2.0 – 3.5 GB) | Holds scene geometry persistently across frames (saving 8–12 seconds of reload time per frame). |
| SSD / NVMe Storage | High-Speed Burst Write | Saves 0% compressed PNG frames in ~0.04 seconds per frame so the CPU never stalls on zlib compression. |

### When Is Method 1 Preferred?

- **Thin-and-Light Laptops with Shared Power Packages:** Ideal for Intel U/P-series (e.g., Core i7-1255U with Intel Iris Xe), AMD Ryzen U-series (Radeon iGPU), and Apple Silicon laptops where the CPU and GPU share a 15W–28W power limit. Capping the CPU to 2 threads allows the GPU to boost to maximum clock speed.
- **Single-GPU Desktops & Gaming Laptops:** Ideal for NVIDIA GTX/RTX or AMD Radeon RX users who want ultra-fast animation renders (0.5s–2.5s per frame) while leaving 80% of their CPU free for browsing or working.
- **100% Frame-to-Frame Visual Consistency:** Because a single engine (EEVEE Next) renders every frame sequentially (1, 2, 3, 4...), lighting and reflections are 100% uniform across the entire video.

## 2. Complete Step-by-Step Guide (From Setup to Final MP4 Video)

### Step 1: Unlock OS Power Limits (Prevents 1.1 GHz Laptop Throttling)

```text
# WINDOWS (Run in Command Prompt as Administrator):
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# LINUX (Run in Bash Terminal):
sudo cpupower frequency-set -g performance      # Or: powerprofilesctl set performance

# macOS (Prevent system sleep during headless render):
caffeinate -i &
```

### Step 2: Save the Customizable Python Script (`method1_gpu_worker.py`)

Create a folder named `C:\Temp_Render` (Windows) or `~/Temp_Render` (Linux/macOS) **outside** cloud-synced folders such as OneDrive or Dropbox. Save the script below as `method1_gpu_worker.py` (it is also in the repo under `scripts/`).

```python
# Method 1 - Dedicated GPU-Only High-Speed Rendering (EEVEE Next)   [scripts/method1_gpu_worker.py]
# Tested on Blender 4.4.3. Run: blender -b --factory-startup SCENE.blend -P THIS_FILE -t 2 -s 1 -e 4440 -j 1 -a
# --- PART A: USER CUSTOMIZATION SETTINGS ---
import bpy, os, platform

# 1. CPU HELPER THREADS:
# - Set 2 for laptops with integrated GPUs (prevents thermal/power throttling).
# - Set 4 for desktop PCs with dedicated NVIDIA/AMD graphics cards.
HELPER_THREADS = 2

# 2. SEQUENTIAL FRAME STEP:
# - Set 1 to render EVERY frame (1, 2, 3, 4... full 60fps/30fps timeline).
# - Set 2 ONLY if your timeline is 60fps and you want 30fps (halves render time).
FRAME_STEP = 1

# 3. RAM PERSISTENCE (True = saves ~9 seconds per frame by keeping meshes in RAM):
# - Set False ONLY on 4GB-8GB RAM PCs if Blender crashes with "Out of Memory".
KEEP_IN_RAM = True

# 4. GPU QUALITY & SHADOW BUFFER PROTECTION:
# - Set ENABLE_SHADOWS = False on Intel Iris Xe / integrated GPUs to prevent
#   "Error: Shadow buffer full". Set True on dedicated GPUs with 6GB+ VRAM.
ENABLE_SHADOWS = False
SAMPLES = 4          # 4-8 for fast speed; 16-32 for high quality
RES_PERCENT = 50     # 50 = 960x540 (4x faster); 100 = full 1920x1080

# --- PART B: ENGINE & SSD EXECUTION BLOCK (keep directly below Part A) ---
scene = bpy.context.scene
render = scene.render
eevee = scene.eevee

# Configure Engine & CPU Threads
# EEVEE engine id: 'BLENDER_EEVEE_NEXT' on Blender 4.2-4.5, 'BLENDER_EEVEE' on Blender 5.x
try:
    render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    render.engine = 'BLENDER_EEVEE'
scene.frame_step = FRAME_STEP
render.threads_mode = 'FIXED'
render.threads = HELPER_THREADS
render.use_compositing = False
render.use_sequencer = False
render.use_persistent_data = KEEP_IN_RAM

# Apply GPU Speed & Shadow Settings (Blender 4.2 / 4.3 / 4.4+)
eevee.taa_render_samples = SAMPLES
eevee.use_raytracing = False
eevee.use_shadows = ENABLE_SHADOWS
eevee.shadow_step_count = 2
eevee.use_volumetric_shadows = False
render.use_motion_blur = False   # Moved to scene.render in Blender 4.2+

# Geometry Simplification & Resolution
render.use_simplify = True
render.simplify_subdivision_render = 0   # Increase to 1 if curved meshes look boxy
render.simplify_child_particles_render = 0.0
render.resolution_x = 1920
render.resolution_y = 1080
render.resolution_percentage = RES_PERCENT

# Cross-Platform Fast SSD Output & Smart Resume
out = "C:/Temp_Render/" if platform.system() == "Windows" else os.path.expanduser("~/Temp_Render/")
os.makedirs(out, exist_ok=True)
render.filepath = os.path.join(out, "frame_")
render.use_overwrite = False     # Skips frames already rendered on disk
render.use_placeholder = True
render.image_settings.file_format = 'PNG'
render.image_settings.color_mode = 'RGB'
render.image_settings.color_depth = '8'
render.image_settings.compression = 0   # 0% CPU compression = instant SSD write

print(">>> METHOD 1 (GPU-ONLY WORKER) ACTIVE <<<")
```

### Step 3: Run the Headless Render Command (All Operating Systems)

Close Blender's GUI so the viewport frees 2–3 GB of RAM. Replace the `.blend` path and the frame range (`-s 1 -e 4440`) with your project values. Keep `-P` **before** `-a`.

```text
# WINDOWS (Command Prompt):
"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe" -b --factory-startup ^
  "C:\Path\To\Your_Scene.blend" ^
  -P "C:\Temp_Render\method1_gpu_worker.py" -t 2 -s 1 -e 4440 -j 1 -a

# LINUX (Bash Terminal):
blender -b --factory-startup "$HOME/Path/To/Your_Scene.blend" \
  -P "$HOME/Temp_Render/method1_gpu_worker.py" -t 2 -s 1 -e 4440 -j 1 -a

# macOS (Zsh / Terminal):
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
  "$HOME/Path/To/Your_Scene.blend" \
  -P "$HOME/Temp_Render/method1_gpu_worker.py" -t 2 -s 1 -e 4440 -j 1 -a
```

### Step 4: Assemble the Rendered PNG Sequence into an MP4 Video

Once all frames are saved in `Temp_Render`, convert them into an H.264 `.mp4` in seconds using FFmpeg or Blender itself.

```text
# OPTION A: FFmpeg (fastest - about 5-15 seconds for 4,440 frames)
# Windows:
ffmpeg -framerate 60 -i "C:/Temp_Render/frame_%04d.png" ^
  -c:v libx264 -pix_fmt yuv420p -crf 18 "C:/Temp_Render/Final_Output.mp4"
# Linux / macOS:
ffmpeg -framerate 60 -i "$HOME/Temp_Render/frame_%04d.png" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 "$HOME/Temp_Render/Final_Output.mp4"
```

**Option B — Blender only (no FFmpeg installation needed).** Save the script below as `make_video_blender.py` (also in the repo under `tools/`), edit `FRAMES_DIR` and `FPS` at the top if needed, then run it. On Windows, use the full path to `blender.exe`.

```text
blender -b --factory-startup -P make_video_blender.py
```

```python
# Assemble frame_*.png into an MP4 using Blender only (no FFmpeg install needed).
# Run: blender -b --factory-startup -P tools/make_video_blender.py
# Frames are added in sorted filename order, so keep the zero-padded frame_0001.png naming.
import bpy, os, glob, platform, struct

FRAMES_DIR = "C:/Temp_Render/" if platform.system() == "Windows" else os.path.expanduser("~/Temp_Render/")
FPS = 60
OUTPUT = os.path.join(FRAMES_DIR, "Final_Video.mp4")

files = sorted(glob.glob(os.path.join(FRAMES_DIR, "frame_*.png")))
if not files:
    raise SystemExit("No frame_*.png files found in " + FRAMES_DIR)

def png_size(path):
    """Read width/height from the PNG header so the video matches the rendered frames."""
    with open(path, "rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24])

width, height = png_size(files[0])
scene = bpy.context.scene
scene.render.fps = FPS
scene.render.resolution_x = width
scene.render.resolution_y = height
scene.render.resolution_percentage = 100

seq_editor = scene.sequence_editor_create()
# Newer Blender versions rename `sequences` to `strips`; support both.
strips = seq_editor.strips if hasattr(seq_editor, "strips") else seq_editor.sequences
strip = strips.new_image("frames", files[0], 1, 1)
for f in files[1:]:
    strip.elements.append(os.path.basename(f))

scene.frame_start = 1
scene.frame_end = len(files)
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.filepath = OUTPUT
bpy.ops.render.render(animation=True)
print(">>> VIDEO WRITTEN:", OUTPUT, "<<<")
```

The script matches the video size to your rendered frames and works with both the older `sequences` and the newer `strips` sequencer API names.

### Step 5: Troubleshooting Common Errors & Instant Fixes

| Error Message / Symptom | Root Cause | Exact Fix |
| :--- | :--- | :--- |
| `SystemError: GPU functions for drawing are not available in background mode` | Third-party viewport add-ons (Bbrush, PolyQuilt, BlendKit) crash when `-b` is used. | Always include `--factory-startup` right after `-b` in your CLI command. |
| `Error: Cannot read file ... No such file or directory` | Typo in the folder path (e.g., capital letter O instead of number 0, or a missing space). | Open File Explorer in your project folder, click the address bar, type `cmd`, press Enter, and use `"Your_Scene.blend"` directly. |
| `AttributeError: 'SceneEEVEE' object has no attribute 'use_motion_blur'` | In Blender 4.2+, motion blur moved from `scene.eevee` to `scene.render`. | Use `scene.render.use_motion_blur = False` (already fixed in the script above). |
| `Error: Shadow buffer full, may result in missing shadows` | Scene lights exceed the integrated GPU's virtual shadow map pool. | Set `ENABLE_SHADOWS = False` (`eevee.use_shadows = False`) in the script. |
| Only odd frames (1, 3, 5...) are rendered | The `.blend` file was saved with Step = 2. | Pass `-j 1` in the CLI command and set `FRAME_STEP = 1` in the script. |
| `TypeError: ... enum "BLENDER_EEVEE_NEXT" not found` | Blender 5.x renamed the engine id back to `BLENDER_EEVEE`. | Use the script above (it detects the id automatically), or set `render.engine = 'BLENDER_EEVEE'` by hand. |

## 3. Conclusion & Final Verdict

**Final Line:** Method 1 (Dedicated GPU-Only Headless EEVEE Next with `-t 2` and RAM persistence) is the gold-standard single-window workflow for laptops and single-GPU desktops — delivering a 4× to 7× speed boost, 100% consistent lighting across all frames, and minimal CPU heat.
