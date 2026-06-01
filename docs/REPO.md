# Repository mode

Point pdf-genesis at any research repo to produce a PDF.

## With manifest (deterministic full paper)

Create `.pdf-genesis/manifest.json`:

```json
{
  "title": "My Study",
  "pipeline": "scripts/run_paper_pipeline.sh",
  "builder": "scripts/build_research_paper.py",
  "output": "papers/My_Report.pdf"
}
```

```bash
pdf-genesis repo /path/to/your-repo
```

- **`pipeline`** — regenerates exports (simulation, figures, etc.)
- **`builder`** — repo-local Python script that assembles the final PDF (keeps IP in your private repo)
- **`output`** — path verified after build

Use `--skip-pipeline` when exports already exist.

## Markdown compendium only

```bash
pdf-genesis repo /path/to/your-repo --mode compile -o out/compendium.pdf
```

Without a `builder`, `auto` mode compiles:

- Markdown from `include_globs` (default: `README.md`, `docs/**/*.md`, `papers/*.md`)
- Optional `exports/*.json` summary tables
- Optional `exports/figures/*.png`

Configure globs and excludes under `compile` in the manifest.

## differential-harness

Private repo includes a manifest that reproduces `papers/Black_2026_CHORUS_SGH1_PoC.pdf`:

```bash
pdf-genesis repo ~/projects/differential-harness
```
