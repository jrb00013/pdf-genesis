# pdf-genesis

[![CI](https://github.com/jrb00013/pdf-genesis/actions/workflows/ci.yml/badge.svg)](https://github.com/jrb00013/pdf-genesis/actions/workflows/ci.yml)

Generate publication-style PDF reports from **local JSON exports** (e.g. from a private [differential-harness](https://github.com/jrb00013/differential-harness) checkout) — CHORUS physics proofs, SGH-1 hardware design, patent memos, and bench test summaries.

This repo ships **sample JSON only**; it does not include proprietary experiment data, CAD, or filed patent claims.

## Features

- **Four report types**: CHORUS physics, SGH-1 design, patent strategy memo, bench test log
- **Themes**: `lab_white` (default) and `chorus_dark`
- **Components**: cover page, TOC, styled tables, page numbers
- **CLI**: `build`, `validate`, `batch`, `themes`
- **MIT licensed**, pytest smoke tests, GitHub Actions CI

## Install

```bash
cd ~/projects/pdf-genesis
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick start

```bash
# From differential-harness notebook export:
pdf-genesis build ../differential-harness/exports/chorus_results.json -o CHORUS_report.pdf

# Design report with dark theme:
pdf-genesis build ../differential-harness/exports/sgh1_design.json --theme chorus_dark

# Validate JSON only:
pdf-genesis validate examples/chorus_results.sample.json

# Batch build all samples:
pdf-genesis batch examples/*.json -o out/
```

## Report types

| JSON signal | Model | Output |
|-------------|-------|--------|
| `results` + `constants` | `ChorusExport` | Physics proof |
| `sizing` | `Sgh1DesignExport` | Hardware design |
| `claims_list` | `PatentMemoExport` | Patent memo |
| `runs` | `BenchReportExport` | Bench log |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/CLI.md](docs/CLI.md).

## Development

```bash
pytest
pdf-genesis themes
```

## License

MIT — see [LICENSE](LICENSE).
