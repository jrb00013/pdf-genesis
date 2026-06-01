# CLI

```bash
pdf-genesis build examples/physics_results.sample.json -o out/report.pdf
pdf-genesis build my_export.json --theme dark --no-toc
pdf-genesis validate my_export.json
pdf-genesis batch examples/*.json -o out/
pdf-genesis themes
```

| Flag | Description |
|------|-------------|
| `--theme` | `lab_white` (default), `dark`, or deprecated `chorus_dark` |
| `--no-cover` | Skip cover page |
| `--no-toc` | Skip table of contents |
| `--footer` | Custom footer string |
