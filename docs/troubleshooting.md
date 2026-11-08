# Troubleshooting: Common Errors & Instant Fixes

Grouped by symptom. Each fix has been used in at least one of the five methods.

## Launching Blender from the command line

| Error / Symptom | Root cause | Fix |
| :--- | :--- | :--- |
| `SystemError: GPU functions for drawing are not available in background mode` | Third-party viewport add-ons (Bbrush, PolyQuilt, BlendKit) crash when `-b` is used. | Always include `--factory-startup` right after `-b`. |
| `Error: Cannot read file ... No such file or directory` | Typo in the path (capital letter O instead of number 0, or a missing space). | Open File Explorer in the project folder, click the address bar, type `cmd`, press Enter, and use `"Your_Scene.blend"` directly. |
| Script settings seem ignored | The script ran after `-a`, or `-t` was omitted. | Put `-P ".../script.py"` **before** `-a`, and pass `-t N` matching the script's thread setting. |
| Only odd frames (1, 3, 5...) are rendered | The `.blend` was saved with Step = 2. | Pass `-j 1` on the CLI and set `FRAME_STEP = 1` in the script. |

## EEVEE / Python API errors

| Error / Symptom | Root cause | Fix |
| :--- | :--- | :--- |
| `AttributeError: 'SceneEEVEE' object has no attribute 'use_motion_blur'` | In Blender 4.2+, motion blur moved from `scene.eevee` to `scene.render`. | Use `scene.render.use_motion_blur = False` (already done in every script here). |
| `TypeError: ... enum "BLENDER_EEVEE_NEXT" not found` | Blender 5.x renamed the engine id back to `BLENDER_EEVEE` (it is `BLENDER_EEVEE_NEXT` in 4.2–4.5). | Use the scripts in this repo (they detect the id), or set the id by hand. Other EEVEE properties were verified on Blender 4.4.3 only. |
| `Error: Shadow buffer full, may result in missing shadows` | Scene lights exceed the integrated GPU's virtual shadow map pool. | Set `ENABLE_SHADOWS = False` (`eevee.use_shadows = False`). |

## Memory and performance

| Error / Symptom | Root cause | Fix |
| :--- | :--- | :--- |
| Out of memory or sudden process termination (Cycles) | Textures or subdivision levels exceed physical RAM. | `KEEP_SCENE_IN_RAM = False`, `TILE_SIZE = 128`, `simplify_subdivision_render = 0`. |
| System RAM hits 98% and Windows stutters (two workers) | Two instances with persistent data exceed free memory on an 8 GB PC. | Set `KEEP_IN_RAM = False` on one worker, or use Method 1. |
| Render uses 100% of all CPU cores instead of 8 | `-t 8` was omitted or overridden after the script ran. | Keep `r.threads = 8` in the script **and** `-t 8` before `-a`. |
| Laptop throttles during an EEVEE render | Too many CPU threads compete with the iGPU for the shared power limit. | Use 2 helper threads (`-t 2`) for EEVEE on U-series laptops. |
| Laptop CPU clock drops to 1.1 GHz when both hybrid windows run | Combined CPU + iGPU wattage exceeds the thermal/power envelope. | Reduce the CPU worker to `-t 6` and `r.threads = 6`. |
| Denoised Cycles image looks blotchy or blurry | 4 samples is too low for dark indoor shadows. | `SAMPLES = 16` and `c.denoising_prefilter = 'ACCURATE'`. |

## Multiple workers and placeholder files

| Error / Symptom | Root cause | Fix |
| :--- | :--- | :--- |
| Both windows render the same frame numbers | `use_placeholder = True` / `use_overwrite = False` was not applied before `-a`. | Make sure `-P` comes before `-a` in both commands. |
| FFmpeg fails on a specific frame | A 0-byte placeholder was left behind when a window was closed mid-frame. | Stop all workers, delete 0-byte PNGs (`tools/cleanup_placeholders.*`), then rerun one worker with `-s 1 -e <last> -j 1 -a` to fill the gap. |
| Subtle brightness flicker between alternating frames | EEVEE and Cycles shade complex materials differently. | Split by range instead of alternating frames, or use Method 3 (two EEVEE workers). |

> **Warning:** delete 0-byte PNGs only after every worker has stopped. While a render is running, in-progress frames are 0-byte placeholders on purpose.
