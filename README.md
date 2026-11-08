# Blender Headless Render Pipelines

Five tested ways to render Blender 4.2+ animations fast and with low RAM from the command line: GPU-only EEVEE, CPU-capped Cycles, parallel EEVEE workers, a hybrid GPU + CPU pipeline, and one universal master script you can tune for any PC.

The methods come from a real optimization session on a 4,440-frame, 1920×1080 animation (Blender 4.4.3, Intel i7-1255U laptop with Iris Xe graphics). On that machine, frame times fell from 30–60+ seconds per frame in the default GUI setup to roughly 1.2–2.5 seconds per frame. Those figures are one laptop's results; see [community benchmarks](docs/community-benchmarks.md) and add yours.

## The five methods

| # | Method | Engine | Best for | Guide | Script | PDF |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Dedicated GPU-only worker | EEVEE Next | Thin laptops with shared CPU/GPU power; single-GPU desktops | [guide](docs/method-1-gpu-only-eevee.md) | [`method1_gpu_worker.py`](scripts/method1_gpu_worker.py) | [PDF](docs/pdf/Method_1_GPU_Only_EEVEE.pdf) |
| 2 | Low-RAM CPU-capped Cycles | Cycles (CPU) | Strict core quota, no usable GPU, true raytracing | [guide](docs/method-2-cpu-capped-cycles.md) | [`method2_cycles_low_ram.py`](scripts/method2_cycles_low_ram.py) | [PDF](docs/pdf/Method_2_Low_RAM_Cycles.pdf) |
| 3 | Parallel multi-process EEVEE | EEVEE Next ×2 | 16 GB+ systems, animation- or modifier-heavy scenes | [guide](docs/method-3-parallel-eevee.md) | [`method3_parallel_eevee.py`](scripts/method3_parallel_eevee.py) | [PDF](docs/pdf/Method_3_Parallel_EEVEE.pdf) |
| 4 | Hybrid dual-engine | EEVEE (GPU) + Cycles (CPU) | Saturating GPU and CPU at once | [guide](docs/method-4-hybrid-dual-engine.md) | [`method4_gpu_worker.py`](scripts/method4_gpu_worker.py), [`method4_cpu_worker.py`](scripts/method4_cpu_worker.py) | [PDF](docs/pdf/Method_4_Hybrid_Dual_Engine.pdf) |
| 5 | Universal master script | EEVEE or Cycles | Any PC; one file you tune by editing a few variables | [guide](docs/method-5-universal-master-script.md) | [`method5_fast_render_master.py`](scripts/method5_fast_render_master.py) | [PDF](docs/pdf/Method_5_Universal_Master_Script.pdf) |

## Which method should I use?

- **Laptop with integrated graphics, want the simplest fast setup:** Method 1.
- **No GPU, GPU memory too small, or you must cap CPU cores:** Method 2.
- **16 GB+ RAM and each frame has a long CPU preparation pause:** Method 3.
- **GPU is at 100% and the CPU is idle, and your materials look similar in EEVEE and Cycles:** Method 4.
- **Not sure, or you want one file for many machines:** Method 5, then compare against the others.

The full table with hardware tiers is in [comparison-and-tuning-matrix.md](docs/comparison-and-tuning-matrix.md).

## Quick start (Method 1)

1. Create an output folder outside any cloud-synced folder: `C:\Temp_Render` (Windows) or `~/Temp_Render` (Linux/macOS).
2. Copy [`scripts/method1_gpu_worker.py`](scripts/method1_gpu_worker.py) into that folder.
3. Run (Windows shown; Linux/macOS commands are in the guide):

```text
"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe" -b --factory-startup ^
  "C:\Path\To\Your_Scene.blend" ^
  -P "C:\Temp_Render\method1_gpu_worker.py" -t 2 -s 1 -e 4440 -j 1 -a
```

4. Turn the PNG frames into a video: `tools/make_video.sh` / `tools/make_video.bat`, or see [video-assembly.md](docs/video-assembly.md).

Ready-made launchers with editable variables are in [`launch/`](launch/). Before long laptop renders, read [01-os-power-setup.md](docs/01-os-power-setup.md).

## Repository layout

```text
blender-headless-render-pipelines/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── .gitignore
├── .github/ISSUE_TEMPLATE/benchmark-report.md
├── docs/
│   ├── 00-case-study.md                  what was diagnosed and fixed (7 bottlenecks)
│   ├── 01-os-power-setup.md              power plans, laptop checklist
│   ├── method-1-gpu-only-eevee.md
│   ├── method-2-cpu-capped-cycles.md
│   ├── method-3-parallel-eevee.md
│   ├── method-4-hybrid-dual-engine.md
│   ├── method-5-universal-master-script.md
│   ├── comparison-and-tuning-matrix.md
│   ├── troubleshooting.md
│   ├── video-assembly.md
│   ├── community-benchmarks.md
│   └── pdf/                              printable copies of the five method guides
├── scripts/                              the Blender Python files (copy these into Temp_Render)
├── launch/
│   ├── windows/                          .bat launchers (edit variables at the top)
│   └── linux-macos/                      .sh launchers
├── tools/                                cleanup, video assembly, PDF builder
└── assets/screenshots/                   Task Manager graphs, before/after frame times
```

## Compatibility

- **Tested on:** Blender 4.4.3 (Windows).
- **Blender 4.2–4.5:** EEVEE Next engine id is `BLENDER_EEVEE_NEXT`.
- **Blender 5.x:** the engine id is `BLENDER_EEVEE` again. The scripts detect which one to use. Other properties were not re-verified on 5.x, so report any differences.
- **Operating systems:** Windows, Linux, and macOS command lines are provided for every method.

## Contributing

Benchmarks, fixes, and reports from other hardware are very welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). The Markdown files in `docs/` are the source of truth for the PDFs; rebuild them with `python tools/build_pdfs.py`.

## License

MIT. See [LICENSE](LICENSE).
