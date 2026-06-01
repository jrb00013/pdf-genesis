# Contributing

Thanks for helping improve pdf-genesis.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Commits

Use focused commits: one logical change per commit (schema, renderer, docs, tests).

## Pull requests

- Run `pytest` before opening a PR
- Add an example JSON if you introduce a new report type
- Update `docs/CLI.md` for CLI changes
