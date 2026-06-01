# CLI reference

## `pdf-genesis build`

```bash
pdf-genesis build examples/chorus_results.sample.json -o out/CHORUS.pdf
pdf-genesis build exports/sgh1_design.json --theme chorus_dark --no-toc
```

| Flag | Description |
|------|-------------|
| `-o`, `--output` | Output PDF path |
| `--title` | Override document title |
| `--theme` | `lab_white` (default) or `chorus_dark` |
| `--no-cover` | Skip cover page |
| `--no-toc` | Skip table of contents |
| `--footer` | Custom footer string |

## `pdf-genesis validate`

Checks JSON against the correct Pydantic schema without generating a PDF.

## `pdf-genesis batch`

```bash
pdf-genesis batch examples/*.json -o out/
```

## `pdf-genesis themes`

Lists registered theme names.
