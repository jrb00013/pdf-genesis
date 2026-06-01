from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from pdf_genesis.schema import ChorusExport, Sgh1DesignExport


def build_design_pdf(data: Sgh1DesignExport, output: Path) -> Path:
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output), pagesize=letter)
    styles = getSampleStyleSheet()
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], spaceBefore=10, spaceAfter=4)
    body = styles["BodyText"]
    story: list = [
        Paragraph(data.title, styles["Title"]),
        Spacer(1, 0.15 * inch),
        Paragraph(
            "Hardware design report for CHORUS-Skid SGH-1 (PRO salinity core) + AEH acoustic module. "
            "CAD: OpenSCAD in differential-harness/hardware/openscad/.",
            body,
        ),
        Paragraph("Skid sizing", h2),
    ]
    sz = data.sizing if isinstance(data.sizing, dict) else data.sizing.model_dump()
    rows = [["Parameter", "Value"]] + [[k, str(v)] for k, v in sorted(sz.items())]
    story.append(Table(rows, colWidths=[3 * inch, 3 * inch]))
    story.append(Paragraph("CAD components", h2))
    parts = [
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
    for p in parts:
        story.append(Paragraph(f"• {p}", body))
    story.append(Paragraph("Build", h2))
    story.append(Paragraph("See differential-harness/hardware/BUILD_BLUEPRINT.md", body))
    story.append(Paragraph("Ranked concepts", h2))
    c = data.claims
    for label, text in [("Safest", c.safest), ("Smartest", c.smartest), ("Strangest", c.strangest), ("Civilization", c.civilization)]:
        story.append(Paragraph(f"<b>{label}:</b> {text}", body))
    doc.build(story)
    return output


def build_pdf(data: ChorusExport, output: Path) -> Path:
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output),
        pagesize=letter,
        rightMargin=0.85 * inch,
        leftMargin=0.85 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontSize=20,
        spaceAfter=14,
    )
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], spaceBefore=12, spaceAfter=6)
    body = styles["BodyText"]

    story: list = []
    story.append(Paragraph(data.title, title_style))
    story.append(
        Paragraph(
            f"<i>Generated:</i> {data.generated_at}",
            body,
        )
    )
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Abstract", h2))
    story.append(
        Paragraph(
            "This report summarizes physics-based modeling of CHORUS — a combinatorial "
            "coastal energy column (osmotic, rhizospheric, orographic, solar). "
            "All power claims are bounded by thermodynamic and electrochemical limits "
            "derived in <i>differential-harness</i>.",
            body,
        )
    )

    story.append(Paragraph("Key numerical results", h2))
    rows = [["Quantity", "Value"]]
    for key, val in sorted(data.results.items()):
        if isinstance(val, float):
            display = f"{val:.4g}"
        else:
            display = str(val)
        rows.append([key.replace("_", " "), display])

    table = Table(rows, colWidths=[3.2 * inch, 2.8 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)

    story.append(Paragraph("Ranked concepts", h2))
    claims = data.claims
    for label, text in [
        ("Safest", claims.safest),
        ("Smartest", claims.smartest),
        ("Strangest", claims.strangest),
        ("Civilization-scale", claims.civilization),
    ]:
        story.append(Paragraph(f"<b>{label}:</b> {text}", body))
        story.append(Spacer(1, 0.08 * inch))

    if data.constants:
        story.append(Paragraph("Model constants", h2))
        for k, v in data.constants.items():
            story.append(Paragraph(f"<b>{k}</b>: {v}", body))

    story.append(Spacer(1, 0.2 * inch))
    story.append(
        Paragraph(
            "<b>References (anchors):</b> Teng et al., Nat. Energy 2026 (blue energy); "
            "Fang et al., Energy Environ. Sci. 2026 (PV–MHD); "
            "Virgo et al., Glob. Chall. 2020 (atmospheric circuit). "
            "Full derivations: differential-harness/docs/CHORUS_MATH_PLAN.md",
            body,
        )
    )

    doc.build(story)
    return output
