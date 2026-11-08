# Case Study: What Was Diagnosed & Solved

This repository grew out of one real optimization session: a **4,440-frame animation at 1920×1080 (60 FPS)** in **Blender 4.4.3**. Everything in the five methods comes from fixing the bottlenecks below. All timings and utilization figures on this page were measured or observed on this one machine; treat them as a worked example, not a benchmark promise.

## Test machine

- **CPU:** 12th Gen Intel Core i7-1255U (10 cores / 12 logical processors, 1.70 GHz base)
- **RAM:** 16 GB system RAM (about 8.4 GB used by Windows at idle, leaving about 7.3 GB available)
- **GPU:** integrated Intel Iris Xe Graphics
- **Storage:** 1 TB SOLIDIGM NVMe SSD (`SSDPFKNU010TZH`)

## The seven bottlenecks

By analysing Task Manager performance graphs and Blender command-line logs across the test runs, seven major hardware and software bottlenecks were found and fixed.

| Stage / Bottleneck Discovered | Root Cause Analysis | Engineering Fix Applied | Measured Impact |
| :--- | :--- | :--- | :--- |
| **1. Initial setup** (Cycles CPU + OpenEXR + OneDrive) | CPU path-tracing on a mobile processor takes minutes per frame. Saving uncompressed OpenEXR into a OneDrive folder triggered constant cloud-sync CPU/RAM spikes. | Switched output to a local NVMe directory (`C:/Temp_Render/`) and changed the format to 8-bit PNG with 0% CPU compression. | Eliminated cloud-sync freezes; reduced disk write time to 0.04 s per frame. |
| **2. UI and add-on crash** (`GPUShader` and `bgl` errors in CLI) | Blender's GUI uses 2–3 GB of RAM. In headless mode (`-b`), third-party add-ons (Bbrush, PolyQuilt, BlendKit) crashed trying to call OpenGL drawing shaders. | Added the `--factory-startup` flag to bypass third-party add-ons and run pure headless background rendering. | Saved about 2.5 GB of RAM; eliminated startup tracebacks and OpenGL crashes. |
| **3. Folder naming mismatch** (`No such file or directory`) | The desktop folder was named `Portfolio_2.O` (ending in a capital letter O) rather than `Portfolio_2.0` (number zero). | Matched the exact path (`Portfolio_2.O`) and launched `cmd` directly from the File Explorer address bar. | Resolved CLI file-loading errors immediately. |
| **4. Geometry reload delay** (10.4 s per frame with a 9 s idle gap) | With `use_persistent_data = False`, Blender destroyed and rebuilt the entire scene mesh data in RAM before every single frame. | Verified peak scene RAM was only about 2.4 GB (`Peak: 2394M`), so `render.use_persistent_data = True` was safe. | Frame time dropped from 10.4 s to 3.8 s per frame (about 3× faster). |
| **5. EEVEE Next API change** (`AttributeError: use_motion_blur`) | Blender 4.2+ replaced legacy EEVEE with `BLENDER_EEVEE_NEXT` and moved motion blur from `scene.eevee` to `scene.render.use_motion_blur`. | Updated the Python calls to `scene.render.use_motion_blur = False` and `eevee.taa_render_samples = 4`. | Restored full script execution in Blender 4.4.3 without a mid-script abort. |
| **6. GPU shadow buffer overflow** (`Error: Shadow buffer full`) | At frame 239+, scene lights exceeded the integrated GPU's virtual shadow map memory, spiking GPU load to 100% and frame times to 14.9 s. | Disabled the shadow buffer bottleneck (`eevee.use_shadows = False`). | Eliminated console error spam and restored 1.5 s–2.5 s GPU frame times. |
| **7. U-series CPU throttling** (CPU stuck at 16% / 1.16 GHz) | EEVEE only uses the GPU. Meanwhile, Windows power management throttled the i7-1255U to 1.16 GHz while the iGPU ran at 100%. | Unlocked the OS High Performance power plan and created both a dedicated GPU-only worker (`-t 2`) and a hybrid dual-worker setup (GPU worker + CPU worker). | Pushed CPU utilization to 70–85% alongside 100% GPU utilization. |

## How the findings map to the methods

| Finding | Where it ended up |
| :--- | :--- |
| Local SSD, 0% PNG compression, no OneDrive | All methods (output block) |
| `--factory-startup` for headless runs | All methods (CLI command) |
| `use_persistent_data = True` | Methods 1–5 (switchable) |
| `eevee.use_shadows = False` on integrated GPUs | Methods 1, 3, 4, 5 |
| 2 CPU helper threads for EEVEE | Methods 1, 4 (and Method 5 preset) |
| Two cooperating processes with placeholder locks | Methods 3, 4 |
| Strict thread cap + small tiles for Cycles | Methods 2, 4 (CPU worker), 5 |

## Reference run from the original session

The exact commands used on the test machine are kept here for reference. Your paths will differ. In this session the two workers started at frames 245 and 246, and the earlier even frames were back-filled separately (second command below).

```text
:: CMD Window 1 (GPU EEVEE worker - 2 CPU helper threads + 100% GPU):
"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe" -b --factory-startup ^
  "C:\Users\hp\OneDrive\Desktop\Portfolio_2.O\Animation_Final.blend" ^
  -P "C:\Temp_Render\method4_gpu_worker.py" -t 2 -s 245 -e 4440 -j 1 -a

:: CMD Window 2 (8-thread CPU Cycles worker - drives CPU to 70-85%):
"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe" -b --factory-startup ^
  "C:\Users\hp\OneDrive\Desktop\Portfolio_2.O\Animation_Final.blend" ^
  -P "C:\Temp_Render\method4_cpu_worker.py" -t 8 -s 246 -e 4440 -j 1 -a
```

Missing even frames (2, 4, 6 ... 244) were back-filled with a stepped range:

```text
:: Target ONLY even frames using Start=2 (-s 2) and Jump=2 (-j 2):
"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe" -b --factory-startup ^
  "C:\Users\hp\OneDrive\Desktop\Portfolio_2.O\Animation_Final.blend" ^
  -P "C:\Temp_Render\method1_gpu_worker.py" -t 2 -s 2 -e 244 -j 2 -a
```
