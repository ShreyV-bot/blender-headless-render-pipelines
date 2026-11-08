# Comparison of All Methods & Hardware Tuning Matrix

Figures marked "case study" come from the single test machine described in [00-case-study.md](00-case-study.md) (i7-1255U, Iris Xe, 16 GB RAM, NVMe). Methods 2 and 5 were not benchmarked in that session, so no frame times are claimed for them.

## Measured results from the case study

| Metric / Hardware Component | Default GUI Render (initial setup) | Headless EEVEE, no persistent data, shadows on | Method 1: GPU-only worker | Method 3: Dual EEVEE (2 GPU workers) | Method 4: Hybrid (EEVEE + Cycles) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Render engine(s)** | Cycles CPU (full GUI) | EEVEE Next (1 headless process) | EEVEE Next (1 process, shadows off) | EEVEE Next × 2 (2 processes) | EEVEE Next (window 1) + Cycles CPU (window 2) |
| **CPU role** | 100% uncapped (thermal throttling) | 12–16% (throttled to 1.16–1.57 GHz, waiting on GPU) | 15–20% (2 threads): evaluates meshes and feeds the GPU at high clock | 30–45% (4+4 threads): worker 2 preps geometry while worker 1 shades | 70–85% (2+8 threads): 8 threads raytrace while 2 feed the GPU |
| **GPU role** | 1% (idle in Cycles CPU mode) | 85–100% (stalled by `Shadow buffer full`) | 95–100%: pure rasterization without shadow-buffer stalls | 100%: alternates between worker 1 and worker 2 | 95–100%: dedicated to window 1 (EEVEE) |
| **System RAM** | 8.4–14.5 GB (GUI + viewport + add-ons) | about 2.2 GB (scene rebuilt every frame) | about 2.2 GB (`Peak: 2394M`, scene stays resident) | about 4.4 GB total (2.2 GB per process) | about 4.5 GB total (2.2 GB + 2.3 GB) |
| **NVMe SSD role** | Heavy OpenEXR writes + OneDrive sync lag | Re-reads textures every frame + PNG compression wait | 0% compression write (raw PNG in 0.04 s) | Placeholder lock sync + 0.04 s PNG writes | Placeholder lock sync + 0.04 s PNG writes |
| **Frame time & consistency** | 30–60+ s/frame (consistent) | 10.4–14.9 s/frame (shadow artifacts) | 1.5–2.5 s/frame (uniform lighting) | 1.3–2.0 s/frame (uniform lighting) | 1.2–1.8 s/frame (shading may differ between engines) |

## Where Methods 2 and 5 fit

| Method | Role | Benchmarked in case study? |
| :--- | :--- | :--- |
| Method 2: Low-RAM CPU-capped Cycles | True raytracing on a strict core quota or with no usable GPU. About 1.8–3.0 GB RAM, 65–80% CPU at 8 threads. | No |
| Method 5: Universal master script | Configurable single file. Behaves like Method 1 or a lighter Method 2 depending on Part A; speed depends on the preset you choose. | No |

## Why each setting helps

- **Why Method 1 is fast on integrated graphics:** On an Intel Core i7-1255U, the 10 CPU cores and the Intel Iris Xe GPU share one power limit. EEVEE Next does most of the pixel shading on the GPU. Locking Blender to 2 CPU threads (`-t 2`) and disabling virtual shadow maps (`eevee.use_shadows = False`) stops the CPU wasting wattage on idle threads and stops the shadow buffer overflowing, which took frame times from 14.9 s to about 1.5–2.5 s.
- **How RAM persistence (`use_persistent_data = True`) saves about 9 seconds per frame:** By default Blender purges meshes and textures from RAM after each frame. Rebuilding the room took about 9.0 s per frame while the GPU render itself took only about 1.4 s. Keeping the 2.2 GB scene resident removes that dead time.
- **How the NVMe SSD trades off with `compression = 0`:** Standard PNG saving uses the CPU for zlib compression, adding roughly 0.5–1.5 s of CPU wait per frame. Setting compression to 0 writes raw image buffers straight to the SSD in about 0.04 s.
- **When to choose Method 1 or 3 versus Method 4:** Choose Method 1 (or Method 3, dual EEVEE) when you need 100% identical lighting across every frame. Choose Method 4 (hybrid EEVEE + Cycles) when you want maximum hardware saturation (70–85% CPU plus 100% GPU). If lighting differs slightly between EEVEE and Cycles on your materials, give each engine its own block of frames (for example, EEVEE on `-s 1 -e 2500` and Cycles on `-s 2501 -e 4440`, or `-e 3200` / `-s 3201`; pick the split where one of your shots ends).

## Hardware tuning matrix

| Hardware tier & specs | Recommended method | `CPU_THREADS` / `-t` | `KEEP_SCENE_IN_RAM` | Samples & shadows |
| :--- | :--- | :--- | :--- | :--- |
| **Ultra-low-RAM laptop** (4–8 GB RAM, integrated GPU, 4 cores) | Method 1 (or Method 5 with the 4–8 GB preset) | 2 (`-t 2`) | False (prevents out-of-memory crashes on 8 GB systems) | `samples = 4`, `use_shadows = False`, scale 50% |
| **Thin & light laptop** (16 GB RAM, i7-1255U, Iris Xe, NVMe: the case-study machine) | Method 1 (GPU-only) or Method 4 (hybrid GPU + CPU) | GPU worker `-t 2`, CPU worker `-t 8` | True (scene uses only about 2.2 GB; saves about 9 s per frame) | `samples = 4–8`, `use_shadows = False`, `compression = 0` |
| **Mid-range gaming laptop / PC** (16–32 GB RAM, 6–8 core CPU, RTX 3060 / 4060) | Method 1 or 3 (EEVEE Next), or Cycles with GPU device | 6 (`-t 6`) | True | `samples = 16–32`, `use_shadows = True`, scale 100% |
| **High-end workstation** (64+ GB RAM, 16–32 core CPU, RTX 4080 / 4090) | Method 3 (two parallel GPU workers) or Cycles OptiX | 0 (auto) or `-t 8` per worker | True | `samples = 32–128`, `use_raytracing = True`, scale 100% |
| **No usable GPU, VRAM overflow, or strict core quota** | Method 2 (low-RAM Cycles) | 4–8 (your core quota) | True if the scene uses under 4 GB, otherwise False | `SAMPLES = 8–16`, 256px tiles, scale 50% |
