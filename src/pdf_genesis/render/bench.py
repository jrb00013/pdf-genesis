from __future__ import annotations

from pathlib import Path

from reportlab.platypus import Paragraph, Spacer

from pdf_genesis.components.cover import build_cover_flowables
from pdf_genesis.components.table import data_table
from pdf_genesis.config import ReportConfig
from pdf_genesis.render.base import body_styles, make_doc, on_page, resolve_theme
from pdf_genesis.schema import BenchReportExport
from pdf_genesis.utils.formatters import fmt_float


def render_bench_pdf(
    data: BenchReportExport,
    output: Path,
    config: ReportConfig | None = None,
) -> Path:
    config = config or ReportConfig(title=data.title, footer_text="Bench data — SGH-1 test cell")
    theme = resolve_theme(config)
    styles = body_styles(theme)
    doc = make_doc(output, config)
    story: list = []

    if config.include_cover:
        story.extend(
            build_cover_flowables(
                data.title,
                data.protocol or "SGH-1 bench protocol",
                config,
                theme,
                meta_lines=[("Result", data.pass_fail or "—")],
            )
        )
        story.append(Spacer(1, 0.25))

    for run in data.runs:
        story.append(Paragraph(f"Run: {run.label}", styles["h2"]))
        if run.timestamp:
            story.append(Paragraph(f"<i>{run.timestamp}</i>", styles["muted"]))
        rows = [["Metric", "Value"]]
        for k, v in sorted(run.metrics.items()):
            display = fmt_float(v) if isinstance(v, float) else str(v)
            rows.append([k, display])
        story.append(data_table(rows, theme))
        story.append(Spacer(1, 0.15))

    doc.build(story, onFirstPage=on_page(config), onLaterPages=on_page(config))
    return output.expanduser().resolve()
