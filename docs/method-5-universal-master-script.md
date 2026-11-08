<!-- series: BLENDER 4.2+ / 4.4+ PRODUCTION PIPELINE SERIES — METHOD 5 OF 5 -->
<!-- footer: Method 5: Universal Master Optimization Script (Customizable) -->
# Method 5: Universal Master Optimization Script
*One Customizable File — Pick EEVEE or Cycles, Cap CPU Threads, Control RAM Persistence & Output for Any PC or Laptop*

> **Tested on:** Blender 4.4.3 · Windows · Intel Core i7-1255U (10 cores / 12 threads) · Intel Iris Xe · 16 GB RAM · NVMe SSD. Utilization and timing figures in this guide come from that single machine; yours will differ.
> **Blender 5.x:** the EEVEE engine id is `BLENDER_EEVEE_NEXT` in Blender 4.2–4.5 and `BLENDER_EEVEE` in 5.x. The scripts detect the right id automatically; every other property was verified on Blender 4.4.3 only.

## 1. About This Method, Hardware Profile & When It Is Preferred

**How the Method Works:** Method 5 is a single, fully commented Python file (`method5_fast_render_master.py`) that works inside Blender's Scripting tab or from the command line with the `-P` flag. It is split into two logical parts you keep together in one file: **Part A** is a short configuration block (thread count, engine, RAM persistence, shadows, samples, resolution scale, frame step, output folder) and **Part B** is the execution block that applies those choices to the scene. By changing a handful of variables in Part A, the same file reproduces the behaviour of Method 1 (EEVEE on the GPU) or a lighter version of Method 2 (Cycles on the CPU), and it can serve as the worker file for two-process runs like Methods 3 and 4.

| Hardware Component | Target Utilization | Exact Role in Method 5 |
| :--- | :--- | :--- |
| GPU (Graphics Card / iGPU) | Depends on `ENGINE_CHOICE` | 95%–100% with `'EEVEE'`; idle with `'CYCLES'` on CPU. |
| CPU (Processor Cores) | Depends on `CPU_THREADS` | Capped at the number you choose (`0` = all threads); keep it at 2 for GPU-only EEVEE on U-series laptops. |
| System RAM (Memory) | Scene size (~2–3 GB in the case study) | Kept resident when `KEEP_SCENE_IN_RAM = True`; freed after every frame when `False`. |
| SSD / NVMe Storage | Fast Write & Lock Files | Zero-compression PNG output with placeholder locks for multi-worker runs. |

### When Is Method 5 Preferred?

- **Unknown or mixed hardware:** You want one file that you can tune for any PC or laptop instead of keeping a separate script per machine.
- **Quick experiments:** You want to switch between EEVEE and Cycles, or change threads, samples, and resolution, by editing a few clearly labelled lines.
- **Teams and repeatable setups:** One shared file is easier to document, review, and keep up to date than five variants.

### How Method 5 Relates to Methods 1–4

- **Versus Method 1:** Same EEVEE settings. Set `ENGINE_CHOICE = 'EEVEE'` and `CPU_THREADS = 2` (and pass `-t 2`) to match Method 1. Note that the file's default is `CPU_THREADS = 8`, which is not the lowest-power choice for EEVEE on a shared-power laptop.
- **Versus Method 2:** The Cycles branch is deliberately simpler: it keeps the thread cap, adaptive sampling, OpenImageDenoise, minimal bounces, and 256px tiles, but does not disable spatial splits, cap child particles, or turn off caustics. Use Method 2 when you are tight on RAM.
- **Versus Methods 3 and 4:** Method 5 renders with one engine per process. For two-process runs, launch the file twice with different start frames (see Step 3).

### Starting-Point Presets

These are starting points taken from this series' tuning matrix, not guarantees. Test on a short frame range first. The columns map to `ENGINE_CHOICE`, `CPU_THREADS`, `KEEP_SCENE_IN_RAM`, `ENABLE_EEVEE_SHADOWS`, `RENDER_SAMPLES`, and `RESOLUTION_SCALE` in Part A.

| Goal | Engine | Threads and `-t` | Keep scene in RAM | EEVEE shadows | Samples | Resolution scale |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Thin laptop with integrated GPU (like Method 1) | `'EEVEE'` | 2 | True | False | 4–8 | 50 |
| 4–8 GB RAM laptop | `'EEVEE'` | 2 | False | False | 4 | 50 |
| Mid-range gaming laptop / desktop GPU | `'EEVEE'` | 6 | True | True | 16–32 | 100 |
| No GPU or VRAM overflow (like Method 2) | `'CYCLES'` | 8 (or your core quota) | True if scene is under 4 GB | n/a | 8–16 | 50 |
| Final-quality stills | `'CYCLES'` | 0 (all threads) | True | n/a | 32–64 | 100 |

## 2. Complete Step-by-Step Guide (From Setup to Final MP4 Video)

### Step 1: Unlock OS High-Performance Mode

```text
# WINDOWS (Command Prompt as Administrator):
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# LINUX (Bash Terminal):
sudo cpupower frequency-set -g performance      # Or: powerprofilesctl set performance

# macOS (prevent system sleep during a headless render):
caffeinate -i &
```

### Step 2: Save and Customize the Master Script (`method5_fast_render_master.py`)

Save the file below as `method5_fast_render_master.py` (also in the repo under `scripts/`). Edit only the values in **Part A**; leave **Part B** unchanged. Keep both parts together in the same file. If `ENGINE_CHOICE` is anything other than `'EEVEE'` or `'CYCLES'`, the script stops with an error instead of silently keeping the engine saved in your `.blend`.

```python
# Method 5 - Universal Master Optimization Script (Customizable)   [scripts/method5_fast_render_master.py]
# Works in Blender's Scripting tab or via the command line with -P. Tested on Blender 4.4.3.
# Run: blender -b --factory-startup SCENE.blend -P THIS_FILE -t 2 -s 1 -e 4440 -j 1 -a
# --- PART A: HARDWARE & QUALITY CONFIGURATION BLOCK ---
import bpy
import os
import platform

# 1. CPU THREAD LIMIT (Set 8 to cap at 8 threads; 0 for 100% of all threads)
#    - Set 2 when using GPU-only EEVEE on U-series laptops to prevent power throttling.
CPU_THREADS = 8

# 2. RENDER ENGINE ('EEVEE' for GPU speed, 'CYCLES' for CPU/GPU raytracing)
ENGINE_CHOICE = 'EEVEE'

# 3. PERSISTENT DATA (True = keeps scene in RAM, eliminates the ~9s reload gap!)
#    Set False ONLY on 4GB-8GB RAM PCs if Blender crashes with Out of Memory.
KEEP_SCENE_IN_RAM = True

# 4. EEVEE SHADOWS (False = fixes "Error: Shadow buffer full" on Intel Iris Xe)
ENABLE_EEVEE_SHADOWS = False

# 5. QUALITY & FRAME STEP (FRAME_STEP = 1 for all frames, 2 for 30fps half-frames)
RENDER_SAMPLES = 4       # 4-8 for fast animation, 16-64 for final quality
RESOLUTION_SCALE = 50    # 50 = 960x540 (4x faster), 75 = 1440x810, 100 = 1080p
FRAME_STEP = 1           # 1 = Every frame (1,2,3..), 2 = Odd frames (1,3,5..)

# 6. AUTOMATIC CROSS-PLATFORM FAST SSD OUTPUT PATH (Outside OneDrive/Cloud)
if platform.system() == "Windows":
    OUTPUT_DIR = "C:/Temp_Render/"
else:
    OUTPUT_DIR = os.path.expanduser("~/Temp_Render/")

# --- PART B: ENGINE, MEMORY & NVMe SSD EXECUTION BLOCK (keep directly below Part A) ---
scene = bpy.context.scene
render = scene.render
eevee = scene.eevee
cycles = scene.cycles

# A. Apply CPU Thread Locking & Disable Post-Processing Overhead
render.threads_mode = 'FIXED' if CPU_THREADS > 0 else 'AUTO'
if CPU_THREADS > 0:
    render.threads = CPU_THREADS
render.use_compositing = False
render.use_sequencer = False
render.use_motion_blur = False   # Unified location in Blender 4.2+
render.use_persistent_data = KEEP_SCENE_IN_RAM

# B. Geometry Simplification (Reduces RAM & CPU Prep Time)
render.use_simplify = True
render.simplify_subdivision_render = 0   # Set 1 or 2 if curved models look boxy
render.simplify_child_particles_render = 0.0

# C. Configure Selected Render Engine (Blender 4.2 / 4.3 / 4.4+)
if ENGINE_CHOICE.upper() == 'EEVEE':
    # EEVEE engine id: 'BLENDER_EEVEE_NEXT' on Blender 4.2-4.5, 'BLENDER_EEVEE' on Blender 5.x
    try:
        render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError:
        render.engine = 'BLENDER_EEVEE'
    eevee.taa_render_samples = RENDER_SAMPLES
    eevee.use_raytracing = False
    eevee.use_shadows = ENABLE_EEVEE_SHADOWS
    eevee.shadow_step_count = 2
    eevee.use_volumetric_shadows = False
elif ENGINE_CHOICE.upper() == 'CYCLES':
    render.engine = 'CYCLES'
    cycles.device = 'CPU'            # Change to 'GPU' for CUDA/OptiX/HIP/OneAPI
    cycles.samples = RENDER_SAMPLES
    cycles.use_adaptive_sampling = True
    cycles.adaptive_threshold = 0.1
    cycles.use_denoising = True
    cycles.denoiser = 'OPENIMAGEDENOISE'
    cycles.denoising_prefilter = 'FAST'
    cycles.max_bounces = 2
    cycles.diffuse_bounces = 1
    cycles.glossy_bounces = 1
    cycles.transmission_bounces = 1
    cycles.volume_bounces = 0
    cycles.use_auto_tile = True
    cycles.tile_size = 256
else:
    raise ValueError("ENGINE_CHOICE must be 'EEVEE' or 'CYCLES', got: " + repr(ENGINE_CHOICE))

# D. Resolution, Frame Step & Zero-Compression NVMe SSD Output
render.resolution_x = 1920
render.resolution_y = 1080
render.resolution_percentage = RESOLUTION_SCALE
scene.frame_step = FRAME_STEP
os.makedirs(OUTPUT_DIR, exist_ok=True)
render.filepath = os.path.join(OUTPUT_DIR, "frame_")
render.use_overwrite = False     # Skips existing frames on disk
render.use_placeholder = True    # Creates 0-byte lock file for multi-worker
render.image_settings.file_format = 'PNG'
render.image_settings.color_mode = 'RGB'
render.image_settings.color_depth = '8'
render.image_settings.compression = 0   # 0% CPU compression = instant SSD write

print(f">>> METHOD 5 (UNIVERSAL MASTER: {ENGINE_CHOICE.upper()}, THREADS={CPU_THREADS}) ACTIVE <<<")
```

### Step 3: Run It (Scripting Tab or Command Line)

**Option A — Blender's Scripting tab:** open the file in the Text Editor and press Run Script. This applies the settings to the open scene; then render normally (Render > Render Animation). Settings made this way are saved with the `.blend` if you save it.

**Option B — Headless command line (recommended for long renders):** keep `-P` before `-a`, and pass `-t` with the same number as `CPU_THREADS`.

```text
# WINDOWS (Command Prompt):
"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe" -b --factory-startup ^
  "C:\Path\To\Your_Scene.blend" ^
  -P "C:\Temp_Render\method5_fast_render_master.py" -t 2 -s 1 -e 4440 -j 1 -a

# LINUX (Bash Terminal):
blender -b --factory-startup "$HOME/Path/To/Your_Scene.blend" \
  -P "$HOME/Temp_Render/method5_fast_render_master.py" -t 2 -s 1 -e 4440 -j 1 -a

# macOS (Zsh / Terminal):
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
  "$HOME/Path/To/Your_Scene.blend" \
  -P "$HOME/Temp_Render/method5_fast_render_master.py" -t 2 -s 1 -e 4440 -j 1 -a
```

**Option C — Two processes from the same file (Method 3 style):** set `CPU_THREADS = 4` and `ENGINE_CHOICE = 'EEVEE'`, then start the second worker one frame later. Both workers skip frames that already exist.

```text
# Linux / macOS (single terminal):
blender -b --factory-startup "$HOME/Path/To/Your_Scene.blend" \
  -P "$HOME/Temp_Render/method5_fast_render_master.py" -t 4 -s 1 -e 4440 -j 1 -a &
blender -b --factory-startup "$HOME/Path/To/Your_Scene.blend" \
  -P "$HOME/Temp_Render/method5_fast_render_master.py" -t 4 -s 2 -e 4440 -j 1 -a &
wait
```

> **Tip:** add `--python-exit-code 1` before `-P` if you want Blender to exit with an error code when the script raises an exception (for example, a mistyped `ENGINE_CHOICE`), instead of carrying on to render with the wrong settings.

### Step 4: Assemble the Final MP4 Video

```text
# Windows:
ffmpeg -framerate 60 -i "C:/Temp_Render/frame_%04d.png" ^
  -c:v libx264 -pix_fmt yuv420p -crf 18 "C:/Temp_Render/Final_Master_Video.mp4"

# Linux / macOS:
ffmpeg -framerate 60 -i "$HOME/Temp_Render/frame_%04d.png" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 "$HOME/Temp_Render/Final_Master_Video.mp4"
```

### Step 5: Troubleshooting Common Errors & Instant Fixes

| Error Message / Symptom | Root Cause | Exact Fix |
| :--- | :--- | :--- |
| Laptop throttles or fans run hard during an EEVEE render | `CPU_THREADS = 8` (the default) keeps many cores busy while the GPU does the real work. | Set `CPU_THREADS = 2` in Part A and pass `-t 2` on the command line. |
| Settings seem to be ignored | The script ran after `-a`, or it was run in the Scripting tab after the render started. | Put `-P "...method5_fast_render_master.py"` before `-a`; in the GUI, run the script before rendering. |
| `ValueError: ENGINE_CHOICE must be 'EEVEE' or 'CYCLES'` | Typo in `ENGINE_CHOICE`. | Use exactly `'EEVEE'` or `'CYCLES'` (case does not matter). |
| `Error: Shadow buffer full, may result in missing shadows` | Scene lights exceed the integrated GPU's shadow map pool. | Keep `ENABLE_EEVEE_SHADOWS = False`. |
| Out of memory or sudden process termination | The scene does not fit in RAM when kept persistent. | Set `KEEP_SCENE_IN_RAM = False`, lower `RESOLUTION_SCALE`, and keep subdivision capped. |
| `TypeError: ... enum "BLENDER_EEVEE_NEXT" not found` | Blender 5.x renamed the engine id back to `BLENDER_EEVEE`. | Use the script above (it detects the id automatically). |
| Only odd frames are rendered | `FRAME_STEP = 2`, or the `.blend` was saved with Step = 2. | Set `FRAME_STEP = 1` and pass `-j 1`. |

## 3. Conclusion & Final Verdict

**Final Line:** Method 5 (Universal Master Optimization Script) is the easiest way to apply this series' optimizations on any machine: edit a dozen clearly labelled values once, choose EEVEE or Cycles, and get the same zero-compression, RAM-persistent, thread-capped pipeline without maintaining a separate script for every PC.
