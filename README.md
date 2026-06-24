# pdf-genesis

[![CI](https://github.com/jrb00013/pdf-genesis/actions/workflows/ci.yml/badge.svg)](https://github.com/jrb00013/pdf-genesis/actions/workflows/ci.yml)

Research PDF toolkit:

1. **Research mode** (default) — synthesize a structured paper from repo metadata, theory docs, experiments, and benchmarks.
2. **Repo compile mode** — stitch markdown + exports into a compendium.
3. **JSON mode** — single-export PDFs (`physics`, `design`, `bench`).

LaTeX equations in markdown (`$...$`, `$$...$$`) render via matplotlib mathtext.

## Install

```bash
pip install -e ".[dev]"
```

## Repository → PDF (primary use)

```bash
# Synthesized research paper (default):
pdf-genesis repo /path/to/your-research-repo

# Markdown compendium only:
pdf-genesis repo /path/to/your-research-repo --mode compile

# Skip live benchmark run (use cached exports):
pdf-genesis repo /path/to/your-repo --skip-benchmark
```

Add `.pdf-genesis/manifest.json` for title, author, and output path — see [docs/REPO.md](docs/REPO.md).

## JSON export → PDF

```bash
pdf-genesis build examples/physics_results.sample.json -o out/report.pdf
pdf-genesis batch examples/*.json -o out/
```

## Report types (JSON)

| `report_type` | Model |
|---------------|-------|
| `physics` | `PhysicsExport` |
| `design` | `DesignExport` |
| `bench` | `BenchReportExport` |

## Development

```bash
pytest
```

## License

MIT — see [LICENSE](LICENSE).
