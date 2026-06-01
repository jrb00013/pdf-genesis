from __future__ import annotations

from pathlib import Path

from reportlab.platypus import Paragraph, Spacer

from pdf_genesis.components.cover import build_cover_flowables
from pdf_genesis.components.table import data_table
from pdf_genesis.components.toc import toc_flowables
from pdf_genesis.config import ReportConfig
from pdf_genesis.render.base import body_styles, make_doc, on_page, resolve_theme
from pdf_genesis.schema import PhysicsExport
from pdf_genesis.utils.formatters import fmt_float, fmt_quantity_key


def render_physics_pdf(
    data: PhysicsExport,
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

    sections = ["Abstract", "Results", "Notes", "Constants", "References"]
    if config.include_cover:
        story.extend(
            build_cover_flowables(
                data.title,
                data.subtitle or "Numerical summary",
                config,
                theme,
                meta_lines=[("Generated", str(data.generated_at) or "—")],
            )
        )
        story.append(Spacer(1, 0.3))
    if config.include_toc:
        story.extend(toc_flowables(sections, theme))

    story.append(Paragraph("Abstract", styles["h2"]))
    story.append(
        Paragraph(
            data.abstract or "Summary of modeled quantities supplied in the export JSON.",
            styles["body"],
        )
    )

    story.append(Paragraph("Results", styles["h2"]))
    rows = [["Quantity", "Value"]]
    for key, val in sorted(data.results.items()):
        display = fmt_float(val) if isinstance(val, float) else str(val)
        rows.append([fmt_quantity_key(key), display])
    story.append(data_table(rows, theme))

    notes = data.notes
    note_pairs = [
        ("Note A", notes.safest),
        ("Note B", notes.smartest),
        ("Note C", notes.strangest),
        ("Note D", notes.civilization),
    ]
    if any(t for _, t in note_pairs):
        story.append(Paragraph("Notes", styles["h2"]))
        for label, text in note_pairs:
            if text:
                story.append(Paragraph(f"<b>{label}:</b> {text}", styles["body"]))
                story.append(Spacer(1, 0.06))

    if data.constants:
        story.append(Paragraph("Constants", styles["h2"]))
        for k, v in data.constants.items():
            story.append(Paragraph(f"<b>{k}</b>: {v}", styles["body"]))

    if data.references:
        story.append(Paragraph("References", styles["h2"]))
        for ref in data.references:
            story.append(Paragraph(f"• {ref}", styles["body"]))

    doc.build(story, onFirstPage=on_page(config), onLaterPages=on_page(config))
    return output.expanduser().resolve()


# Backward-compatible alias
render_chorus_pdf = render_physics_pdf
