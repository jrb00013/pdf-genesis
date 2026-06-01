from __future__ import annotations

from pathlib import Path

from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer

from pdf_genesis.components.cover import build_cover_flowables
from pdf_genesis.components.table import data_table
from pdf_genesis.components.toc import toc_flowables
from pdf_genesis.config import ReportConfig
from pdf_genesis.render.base import body_styles, make_doc, on_page, resolve_theme
from pdf_genesis.schema import DesignExport


def render_design_pdf(
    data: DesignExport,
    output: Path,
    config: ReportConfig | None = None,
) -> Path:
    config = config or ReportConfig(title=data.title)
    if data.title:
        config.title = data.title
    theme = resolve_theme(config)
    styles = body_styles(theme)
    doc = make_doc(output, config)
    story: list = []
    sections = ["Overview", "Sizing", "CAD index", "Paths", "Notes"]

    if config.include_cover:
        story.extend(
            build_cover_flowables(
                data.title,
                data.subtitle or "Hardware / assembly summary",
                config,
                theme,
            )
        )
        story.append(Spacer(1, 0.3))
    if config.include_toc:
        story.extend(toc_flowables(sections, theme))

    story.append(Paragraph("Overview", styles["h2"]))
    story.append(
        Paragraph(
            data.overview or "Design parameters and file references from the export JSON.",
            styles["body"],
        )
    )

    story.append(Paragraph("Sizing", styles["h2"]))
    sz = data.sizing if isinstance(data.sizing, dict) else data.sizing.model_dump()
    rows = [["Parameter", "Value"]] + [[k, str(v)] for k, v in sorted(sz.items())]
    story.append(data_table(rows, theme, col_widths=[3 * inch, 3 * inch]))

    if data.cad_files:
        story.append(Paragraph("CAD index", styles["h2"]))
        for p in data.cad_files:
            story.append(Paragraph(f"• {p}", styles["body"]))

    if data.blueprint_path or data.bom_path:
        story.append(Paragraph("Paths", styles["h2"]))
        if data.blueprint_path:
            story.append(Paragraph(f"<b>Blueprint:</b> {data.blueprint_path}", styles["body"]))
        if data.bom_path:
            story.append(Paragraph(f"<b>BOM:</b> {data.bom_path}", styles["body"]))

    n = data.notes
    note_pairs = [("Note A", n.safest), ("Note B", n.smartest), ("Note C", n.strangest), ("Note D", n.civilization)]
    if any(t for _, t in note_pairs):
        story.append(Paragraph("Notes", styles["h2"]))
        for label, text in note_pairs:
            if text:
                story.append(Paragraph(f"<b>{label}:</b> {text}", styles["body"]))

    doc.build(story, onFirstPage=on_page(config), onLaterPages=on_page(config))
    return output.expanduser().resolve()
