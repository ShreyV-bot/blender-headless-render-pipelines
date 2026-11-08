# Changelog

## 1.0.0

First public release of the five-method series.

### Added
- **Method 5: Universal Master Optimization Script** (`scripts/method5_fast_render_master.py`) with its own guide and PDF. It was previously "Method 1" in the combined markdown guide.
- Launchers for Windows (`launch/windows/*.bat`) and Linux/macOS (`launch/linux-macos/*.sh`).
- Tools: placeholder cleanup, FFmpeg video helpers, a Blender-only video script, and a PDF builder.
- Case study, power-setup guide, comparison and tuning matrix, consolidated troubleshooting, video-assembly guide, and community benchmarks page.

### Changed
- **One numbering scheme:** the PDF series numbering (Methods 1–4) is now canonical, with the master script as Method 5. The combined guide's older numbering is retired.
- **Script names are unique.** Methods 1 and 4 both used `gpu_worker.py` with different contents; they are now `method1_gpu_worker.py` and `method4_gpu_worker.py` (plus `method4_cpu_worker.py`).
- The EEVEE scripts pick `BLENDER_EEVEE_NEXT` (Blender 4.2–4.5) or `BLENDER_EEVEE` (Blender 5.x) automatically.
- The master script now sets 8-bit RGB PNG with 0% compression like the other methods, and stops with a clear error if `ENGINE_CHOICE` is not `'EEVEE'` or `'CYCLES'`.
- Each guide states the test machine and that timings come from one laptop.
- Method 4 explains how to resume an interrupted run and shows the split-by-range alternative as a full command.
- Series header now reads "Method N of 5".

### Fixed
- Method 3: PowerShell command `RemoveItem` corrected to `Remove-Item`.
- Method 2: stray non-English word in a script comment replaced ("hundreds of MB of BVH RAM").
- Cleanup instructions now warn to run only after all workers have stopped, since in-progress frames are 0-byte placeholders.

### Kept as-is
- The original machine path in the case study's reference run (`docs/00-case-study.md`) is intentionally left in because it documents the original research session.
