from __future__ import annotations

from pathlib import Path

from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer

from pdf_genesis.components.cover import build_cover_flowables
from pdf_genesis.components.table import data_table
from pdf_genesis.components.toc import toc_flowables
from pdf_genesis.config import ReportConfig
from pdf_genesis.render.base import body_styles, make_doc, on_page, resolve_theme
from pdf_genesis.schema import Sgh1DesignExport


CAD_PARTS = [
    "sgh1_assembly.scad",
    "sgh1_membrane_housing.scad",
    "sgh1_manifold_feed.scad",
    "sgh1_manifold_draw.scad",
    "sgh1_skid_frame.scad",
    "chorus_skid_enclosure.scad",
    "chorus_aeh_panel.scad",
    "sgh1_membrane_plate.scad",
    "sgh1_end_cap.scad",
    "sgh1_pump_mount.scad",
    "sgh1_sensor_bracket.scad",
]


def render_design_pdf(
    data: Sgh1DesignExport,
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
    sections = ["Overview", "Skid sizing", "CAD components", "Build references", "Ranked concepts"]

    if config.include_cover:
        story.extend(
            build_cover_flowables(
                data.title,
                "CHORUS-Skid SGH-1 — PRO core + AEH acoustic module",
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
            "Hardware design report for CHORUS-Skid SGH-1 (PRO salinity-gradient core) "
            "with optional AEH ultrasonic membrane enhancement. "
            "CAD sources live in <i>differential-harness/hardware/openscad/</i>.",
            styles["body"],
        )
    )

    story.append(Paragraph("Skid sizing", styles["h2"]))
    sz = data.sizing if isinstance(data.sizing, dict) else data.sizing.model_dump()
    rows = [["Parameter", "Value"]] + [[k, str(v)] for k, v in sorted(sz.items())]
    story.append(data_table(rows, theme, col_widths=[3 * inch, 3 * inch]))

    story.append(Paragraph("CAD components", styles["h2"]))
    for p in CAD_PARTS:
        story.append(Paragraph(f"• {p}", styles["body"]))

    story.append(Paragraph("Build references", styles["h2"]))
    bp = data.blueprint_path or "differential-harness/hardware/BUILD_BLUEPRINT.md"
    bom = data.bom_path or "differential-harness/hardware/bom/SGH1_BOM.csv"
    story.append(Paragraph(f"<b>Blueprint:</b> {bp}", styles["body"]))
    story.append(Paragraph(f"<b>BOM:</b> {bom}", styles["body"]))

    story.append(Paragraph("Ranked concepts", styles["h2"]))
    c = data.claims
    for label, text in [
        ("Safest", c.safest),
        ("Smartest", c.smartest),
        ("Strangest", c.strangest),
        ("Civilization", c.civilization),
    ]:
        story.append(Paragraph(f"<b>{label}:</b> {text}", styles["body"]))

    doc.build(story, onFirstPage=on_page(config), onLaterPages=on_page(config))
    return output.expanduser().resolve()
