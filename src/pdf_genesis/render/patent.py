from __future__ import annotations

from pathlib import Path

from reportlab.platypus import Paragraph, Spacer

from pdf_genesis.components.cover import build_cover_flowables
from pdf_genesis.components.toc import toc_flowables
from pdf_genesis.config import ReportConfig
from pdf_genesis.render.base import body_styles, make_doc, on_page, resolve_theme
from pdf_genesis.schema import PatentMemoExport


def render_patent_pdf(
    data: PatentMemoExport,
    output: Path,
    config: ReportConfig | None = None,
) -> Path:
    config = config or ReportConfig(title=data.title, footer_text="Attorney work product — draft")
    theme = resolve_theme(config)
    styles = body_styles(theme)
    doc = make_doc(output, config)
    story: list = []

    if config.include_cover:
        story.extend(
            build_cover_flowables(
                data.title,
                "Patent strategy memo — SGH-1 / CHORUS-Skid",
                config,
                theme,
                meta_lines=[("Inventor", data.inventor or "—")],
            )
        )
        story.append(Spacer(1, 0.25))

    story.append(Paragraph("Independent claims (draft)", styles["h2"]))
    for i, item in enumerate(data.claims_list, 1):
        if isinstance(item, str):
            text = item
            num = i
        else:
            text = item.text
            num = item.number
        story.append(Paragraph(f"<b>{num}.</b> {text}", styles["body"]))
        story.append(Spacer(1, 0.08))

    if data.prior_art:
        story.append(Paragraph("Prior art anchors", styles["h2"]))
        for ref in data.prior_art:
            story.append(Paragraph(f"• {ref}", styles["body"]))

    if data.notes:
        story.append(Paragraph("Notes", styles["h2"]))
        story.append(Paragraph(data.notes, styles["body"]))

    doc.build(story, onFirstPage=on_page(config), onLaterPages=on_page(config))
    return output.expanduser().resolve()
