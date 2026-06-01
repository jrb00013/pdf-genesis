# Architecture

`pdf-genesis` turns JSON exports from **differential-harness** into styled research PDFs using ReportLab.

## Layers

| Layer | Role |
|-------|------|
| `schema.py` | Pydantic models: CHORUS physics, SGH-1 design, patent memo, bench report |
| `loaders.py` | JSON load + `detect_report_type()` |
| `config.py` | `ReportConfig` — theme, margins, cover/TOC toggles |
| `themes/` | Color palettes (`lab_white`, `chorus_dark`) |
| `components/` | Reusable flowables: cover, tables, TOC, figures, page numbers |
| `render/` | Report-specific story builders |
| `builder.py` | Thin facade over `render/` |
| `cli.py` | `build`, `validate`, `batch`, `themes` |

## Data flow

```
export.json → load_any() → render_*_pdf() → SimpleDocTemplate.build() → report.pdf
```

## Adding a report type

1. Extend `schema.py` with a model and `report_type` literal.
2. Add `render/new_type.py` and register in `render/__init__.py`.
3. Wire `loaders.detect_report_type()` and `cli.cmd_build()`.
