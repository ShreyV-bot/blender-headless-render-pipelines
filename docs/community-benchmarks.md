# Community Benchmarks

The numbers in this repository come from one laptop. If you try a method, please add your result so others can compare. Open a pull request that appends a row, or file a **Benchmark report** issue.

| Method | CPU | GPU | RAM | Storage | Blender version | OS | Scene (frames, resolution, engine) | Seconds per frame | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Intel Core i7-1255U | Intel Iris Xe | 16 GB | NVMe | 4.4.3 | Windows | 4,440-frame 1920×1080 animation, EEVEE Next | 1.5–2.5 | Case study (shadows off, `-t 2`); resolution scale not recorded |
| 3 | Intel Core i7-1255U | Intel Iris Xe | 16 GB | NVMe | 4.4.3 | Windows | 4,440-frame 1920×1080 animation, EEVEE Next ×2 | 1.3–2.0 | Case study |
| 4 | Intel Core i7-1255U | Intel Iris Xe | 16 GB | NVMe | 4.4.3 | Windows | 4,440-frame 1920×1080 animation, EEVEE + Cycles | 1.2–1.8 | Case study (shading may differ between engines) |

Tips for a useful report: render the same 50–100 frame range with each method, note the Blender version and engine id, and say whether persistent data and shadows were on.
