# pdf-genesis

[![CI](https://github.com/jrb00013/pdf-genesis/actions/workflows/ci.yml/badge.svg)](https://github.com/jrb00013/pdf-genesis/actions/workflows/ci.yml)

**Generic** research PDF builder: turn **your local JSON exports** into styled reports (physics summary, hardware design, bench log).

This repository contains **only placeholder sample JSON** — no proprietary IP, patent drafts, CAD, or experiment data.

## Features

- **Three report types**: `physics`, `design`, `bench`
- **Themes**: `lab_white` (default), `dark`
- **CLI**: `build`, `validate`, `batch`, `themes`
- **MIT licensed**, pytest + GitHub Actions

## Install

```bash
cd ~/projects/pdf-genesis
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick start

```bash
pdf-genesis build examples/physics_results.sample.json -o out/report.pdf
pdf-genesis build examples/design_report.sample.json --theme dark
pdf-genesis validate examples/bench_report.sample.json
pdf-genesis batch examples/*.json -o out/
```

## Report types

| `report_type` | Model | Typical JSON fields |
|---------------|-------|---------------------|
| `physics` | `PhysicsExport` | `results`, `constants`, `abstract`, `references` |
| `design` | `DesignExport` | `sizing`, `cad_files`, `blueprint_path`, `bom_path` |
| `bench` | `BenchReportExport` | `runs`, `protocol`, `pass_fail` |

Legacy `report_type: "chorus"` is accepted and mapped to `physics`. **Patent / IP memos are not supported** in this public toolkit — keep those in a private repo.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/CLI.md](docs/CLI.md).

## Development

```bash
pytest
pdf-genesis themes
```

## License

MIT — see [LICENSE](LICENSE).
