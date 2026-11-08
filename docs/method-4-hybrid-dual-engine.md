<!-- series: BLENDER 4.2+ / 4.4+ PRODUCTION PIPELINE SERIES — METHOD 4 OF 5 -->
<!-- footer: Method 4: Hybrid Dual-Engine Rendering (GPU EEVEE + CPU Cycles) -->
# Method 4: Hybrid Dual-Engine Rendering (GPU + CPU)
*Simultaneous 100% GPU EEVEE Next Worker + 8-Thread (75–85%) CPU Cycles Worker Coordinated via NVMe SSD*

> **Tested on:** Blender 4.4.3 · Windows · Intel Core i7-1255U (10 cores / 12 threads) · Intel Iris Xe · 16 GB RAM · NVMe SSD. Utilization and timing figures in this guide come from that single machine; yours will differ.
> **Blender 5.x:** the EEVEE engine id is `BLENDER_EEVEE_NEXT` in Blender 4.2–4.5 and `BLENDER_EEVEE` in 5.x. The scripts detect the right id automatically; every other property was verified on Blender 4.4.3 only.

## 1. About This Method, Hardware Profile & When It Is Preferred

**How the Method Works:** When rendering with EEVEE Next on an integrated GPU (like Intel Iris Xe) or an entry-level GPU, the graphics processor quickly hits 100% utilization while a multi-core CPU (such as a 10-core / 12-thread Intel Core i7-1255U) sits idle at 12%–16%. Because EEVEE cannot use CPU cores to render pixels, the only way to harness both silicon units simultaneously is a hybrid dual-engine pipeline: Window 1 (`method4_gpu_worker.py`) runs EEVEE Next on the GPU (using 2 CPU helper threads), while Window 2 (`method4_cpu_worker.py`) runs ultra-stripped Cycles on 8 CPU threads. Both workers share the same SSD output directory via 0-byte placeholder locks (or render separate scene shots) so no hardware sits idle.

| Hardware Component | Target Utilization | Exact Role in Method 4 |
| :--- | :--- | :--- |
| GPU (Graphics Card / iGPU) | 95% – 100% (Worker 1) | Dedicated exclusively to Worker 1 (`method4_gpu_worker.py`) for fast EEVEE Next rasterization. |
| CPU (Processor Cores) | 75% – 85% (2 + 8 Threads) | 2 threads feed Worker 1's GPU while 8 threads raytrace and AI-denoise frames in Worker 2 (`method4_cpu_worker.py`). |
| System RAM (Memory) | Moderate (~4.5 – 6.2 GB Total) | Holds Worker 1 (~2.2 GB) and Worker 2 (~2.3 GB) persistently in RAM (`use_persistent_data = True`). |
| NVMe SSD Storage | Lock-File Sync & Fast Write | Prevents frame collisions via `use_placeholder = True` and writes uncompressed PNGs in 0.04s. |

### When Is Method 4 Preferred?

- **Maximum Hardware Saturation (70–85% CPU + 100% GPU):** When your GPU is bottlenecked at 100% in EEVEE and you have 8+ idle CPU threads that you want actively rendering frames at the same time.
- **Simple / Baked Material Scenes or Multi-Shot Animations:** Ideal when your materials (such as baked textures or simple diffuse walls) look nearly identical in EEVEE and 1-bounce Cycles, OR when you assign Worker 1 (EEVEE) to Shot A (`-s 1 -e 3000`) and Worker 2 (Cycles) to Shot B (`-s 3001 -e 4440`).

## 2. Complete Step-by-Step Guide (From Setup to Final MP4 Video)

### Step 1: Unlock OS High-Performance Mode (Critical for Hybrid Load)

When both the CPU and GPU are loaded simultaneously on a laptop, keep the AC charger plugged in, elevate the back of the laptop for airflow, and unlock the OS power governor:

```text
# WINDOWS (Command Prompt as Administrator):
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# LINUX (Bash Terminal):
sudo cpupower frequency-set -g performance
```

### Step 2: Create Both Worker Scripts

Save the first script as `C:\Temp_Render\method4_gpu_worker.py` and the second as `C:\Temp_Render\method4_cpu_worker.py` (or inside `~/Temp_Render/` on Linux/macOS). Both are also in the repo under `scripts/`.

**Script 1: `method4_gpu_worker.py`** — runs EEVEE Next on the GPU plus 2 CPU helper threads.

```python
# Method 4 - Hybrid Dual-Engine, WORKER 1: EEVEE Next on 100% GPU + 2 CPU helper threads
# [scripts/method4_gpu_worker.py]   Tested on Blender 4.4.3.
# Run: blender -b --factory-startup SCENE.blend -P THIS_FILE -t 2 -s 1 -e 4440 -j 1 -a
import bpy, os, platform

s = bpy.context.scene
r = s.render
eevee = s.eevee

# EEVEE engine id: 'BLENDER_EEVEE_NEXT' on Blender 4.2-4.5, 'BLENDER_EEVEE' on Blender 5.x
try:
    r.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    r.engine = 'BLENDER_EEVEE'
s.frame_step = 1                       # 1 = Every frame sequentially
r.threads_mode = 'FIXED'
r.threads = 2                          # 2 CPU helper threads
r.use_persistent_data = True
r.use_compositing = False
r.use_sequencer = False
r.use_motion_blur = False

eevee.taa_render_samples = 4
eevee.use_raytracing = False
eevee.use_shadows = False              # Prevents "Error: Shadow buffer full"
eevee.use_volumetric_shadows = False

r.use_simplify = True
r.simplify_subdivision_render = 0
r.resolution_x = 1920
r.resolution_y = 1080
r.resolution_percentage = 50

out = "C:/Temp_Render/" if platform.system() == "Windows" else os.path.expanduser("~/Temp_Render/")
os.makedirs(out, exist_ok=True)
r.filepath = os.path.join(out, "frame_")
r.use_overwrite = False
r.use_placeholder = True
r.image_settings.file_format = 'PNG'
r.image_settings.compression = 0

print(">>> METHOD 4 / WORKER 1 (GPU EEVEE) ACTIVE <<<")
```

**Script 2: `method4_cpu_worker.py`** — runs ultra-fast Cycles on 8 CPU threads (75–85% CPU).

```python
# Method 4 - Hybrid Dual-Engine, WORKER 2: ultra-fast Cycles on 8 CPU threads (75-85% CPU)
# [scripts/method4_cpu_worker.py]   Tested on Blender 4.4.3.
# Run: blender -b --factory-startup SCENE.blend -P THIS_FILE -t 8 -s 2 -e 4440 -j 1 -a
import bpy, os, platform

s = bpy.context.scene
r = s.render
c = s.cycles

r.engine = 'CYCLES'
c.device = 'CPU'
s.frame_step = 1                       # 1 = Every frame sequentially
r.threads_mode = 'FIXED'
r.threads = 8                          # Customise: set 6, 8, or 12 for your CPU!
r.use_persistent_data = True
r.use_compositing = False
r.use_sequencer = False
r.use_motion_blur = False

c.samples = 4                          # Ultra-fast 4 samples + AI denoiser
c.use_adaptive_sampling = True
c.adaptive_threshold = 0.1
c.max_bounces = 1
c.diffuse_bounces = 1
c.glossy_bounces = 0
c.transmission_bounces = 0
c.volume_bounces = 0
c.use_denoising = True
c.denoiser = 'OPENIMAGEDENOISE'
c.denoising_prefilter = 'FAST'
c.use_auto_tile = True
c.tile_size = 256

r.use_simplify = True
r.simplify_subdivision_render = 0
r.resolution_x = 1920
r.resolution_y = 1080
r.resolution_percentage = 50

out = "C:/Temp_Render/" if platform.system() == "Windows" else os.path.expanduser("~/Temp_Render/")
os.makedirs(out, exist_ok=True)
r.filepath = os.path.join(out, "frame_")
r.use_overwrite = False
r.use_placeholder = True
r.image_settings.file_format = 'PNG'
r.image_settings.compression = 0

print(">>> METHOD 4 / WORKER 2 (CPU CYCLES) ACTIVE <<<")
```

### Step 3: Launch Both Workers Simultaneously (Shared Queue or Split Range)

```text
# WINDOWS: open TWO Command Prompt windows side by side.
# Window 1 (GPU EEVEE worker - starts at frame 1):
"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe" -b --factory-startup ^
  "C:\Path\To\Your_Scene.blend" ^
  -P "C:\Temp_Render\method4_gpu_worker.py" -t 2 -s 1 -e 4440 -j 1 -a

# Window 2 (8-thread CPU Cycles worker - starts at frame 2):
"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe" -b --factory-startup ^
  "C:\Path\To\Your_Scene.blend" ^
  -P "C:\Temp_Render\method4_cpu_worker.py" -t 8 -s 2 -e 4440 -j 1 -a
```

```text
# LINUX / macOS (single terminal, parallel launch):
blender -b --factory-startup "$HOME/Path/To/Your_Scene.blend" \
  -P "$HOME/Temp_Render/method4_gpu_worker.py" -t 2 -s 1 -e 4440 -j 1 -a &
blender -b --factory-startup "$HOME/Path/To/Your_Scene.blend" \
  -P "$HOME/Temp_Render/method4_cpu_worker.py" -t 8 -s 2 -e 4440 -j 1 -a &
wait
```

**Alternative — split by range (recommended when EEVEE and Cycles look different on your materials).** Give each engine its own block of frames so no two neighbouring frames come from different engines. The split point below is only an example; choose the frame where one of your shots ends. Windows commands are shown; on Linux/macOS use the same arguments.

```text
# Window 1 (GPU EEVEE) renders frames 1-3200:
"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe" -b --factory-startup ^
  "C:\Path\To\Your_Scene.blend" ^
  -P "C:\Temp_Render\method4_gpu_worker.py" -t 2 -s 1 -e 3200 -j 1 -a

# Window 2 (CPU Cycles) renders frames 3201-4440:
"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe" -b --factory-startup ^
  "C:\Path\To\Your_Scene.blend" ^
  -P "C:\Temp_Render\method4_cpu_worker.py" -t 8 -s 3201 -e 4440 -j 1 -a
```

**Resuming an interrupted run.** Because `use_overwrite = False` skips frames that already exist, you can restart from where you stopped. For example, if frames 1–244 are finished, start the GPU worker at `-s 245` and the CPU worker at `-s 246` (keep the two start frames one apart).

### Step 4: Assemble the Final MP4 Video

```text
# Convert all 4,440 PNG frames into a 60 FPS MP4 via FFmpeg:
ffmpeg -framerate 60 -i "C:/Temp_Render/frame_%04d.png" ^
  -c:v libx264 -pix_fmt yuv420p -crf 18 "C:/Temp_Render/Final_Hybrid_Video.mp4"
```

### Step 5: Troubleshooting Common Errors & Instant Fixes

| Error Message / Symptom | Root Cause | Exact Fix |
| :--- | :--- | :--- |
| Subtle brightness flicker between alternating frames in the MP4 video | EEVEE (rasterized) and Cycles (raytraced) calculate shadows/reflections differently on complex shaders. | Split by range instead of alternating: Window 1 (GPU) on `-s 1 -e 3200` and Window 2 (CPU) on `-s 3201 -e 4440`, or use Method 3 (two EEVEE workers). |
| Laptop CPU clock drops to 1.1 GHz when both windows run | Combined CPU + iGPU wattage exceeds the laptop's thermal/power envelope. | Reduce to `r.threads = 6` (`-t 6`) in `method4_cpu_worker.py` so the iGPU retains enough power headroom. |
| `TypeError: ... enum "BLENDER_EEVEE_NEXT" not found` | Blender 5.x renamed the engine id back to `BLENDER_EEVEE`. | Use `method4_gpu_worker.py` from this series (it detects the id automatically). |

## 3. Conclusion & Final Verdict

**Final Line:** Method 4 (Hybrid Dual-Engine GPU EEVEE + CPU Cycles) is the ultimate hardware-saturation technique when you want every single resource in your computer — 100% GPU, 75–85% CPU (8 cores), system RAM, and NVMe SSD — working simultaneously to finish large frame counts as fast as physically possible.
