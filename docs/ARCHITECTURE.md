# Architecture

`pdf-genesis` is a small ReportLab-based library that renders **local JSON** into PDFs.

| Module | Role |
|--------|------|
| `schema.py` | Pydantic models: `PhysicsExport`, `DesignExport`, `BenchReportExport` |
| `loaders.py` | Type detection + JSON load |
| `render/` | One renderer per report type |
| `themes/` | Color palettes (`lab_white`, `dark`) |
| `cli.py` | `build`, `validate`, `batch`, `themes` |

All narrative text in PDFs comes from the JSON you pass in. Built-in renderers do not embed product-specific or patent content.
