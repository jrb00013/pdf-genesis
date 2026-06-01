# pdf-genesis

[![CI](https://github.com/jrb00013/pdf-genesis/actions/workflows/ci.yml/badge.svg)](https://github.com/jrb00013/pdf-genesis/actions/workflows/ci.yml)

Research PDF toolkit:

1. **Repo mode** — point at a project; compile markdown + exports, or run a manifest **pipeline + builder** for a deterministic full report.
2. **JSON mode** — single-export PDFs (`physics`, `design`, `bench`).

Public repo ships **generic samples only** — no proprietary IP.

## Install

```bash
pip install -e ".[dev]"
```

## Repository → PDF (primary use)

```bash
# Full paper (manifest runs pipeline + repo-local builder):
pdf-genesis repo /path/to/your-research-repo

# Markdown + figures + export summaries only:
pdf-genesis repo /path/to/your-research-repo --mode compile -o out/compendium.pdf

# Rebuild PDF without re-running simulation:
pdf-genesis repo /path/to/your-research-repo --skip-pipeline
```

Add `.pdf-genesis/manifest.json` to your repo — see [docs/REPO.md](docs/REPO.md).

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
