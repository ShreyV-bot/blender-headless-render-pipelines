# Contributing

Thanks for helping make these pipelines better.

## Most useful contributions

1. **Benchmarks:** add a row to [docs/community-benchmarks.md](docs/community-benchmarks.md) or open a *Benchmark report* issue.
2. **Compatibility reports:** which Blender version, OS, and GPU worked or failed, with the exact error text.
3. **Fixes and clarifications** to the guides or scripts.

## Ground rules

- Keep the scripts as plain, commented Python with a clearly marked user-configuration block.
- Do not commit `.blend` files, rendered frames, or videos (see `.gitignore`).
- Change the Markdown in `docs/`, not the PDFs. After editing a method guide, rebuild the PDFs: `python tools/build_pdfs.py` (needs `reportlab` and the DejaVu fonts).
- If a script change affects a guide, update the code block in that guide so they match.
- Note the Blender version you tested on in your pull request.
