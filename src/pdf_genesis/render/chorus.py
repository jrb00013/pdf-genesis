from __future__ import annotations

from pathlib import Path

from reportlab.platypus import Paragraph, Spacer

from pdf_genesis.components.cover import build_cover_flowables
from pdf_genesis.components.table import data_table
from pdf_genesis.components.toc import toc_flowables
from pdf_genesis.config import ReportConfig
from pdf_genesis.render.base import body_styles, make_doc, on_page, resolve_theme
from pdf_genesis.schema import ChorusExport
from pdf_genesis.utils.formatters import fmt_float, fmt_quantity_key


def render_chorus_pdf(
    data: ChorusExport,
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

    sections = ["Abstract", "Key numerical results", "Ranked concepts", "Model constants", "References"]
    if config.include_cover:
        story.extend(
            build_cover_flowables(
                data.title,
                "Physics proof export — differential-harness",
                config,
                theme,
                meta_lines=[("Generated", str(data.generated_at))],
            )
        )
        story.append(Spacer(1, 0.3))
    if config.include_toc:
        story.extend(toc_flowables(sections, theme))

    story.append(Paragraph("Abstract", styles["h2"]))
    story.append(
        Paragraph(
            "This report summarizes physics-based modeling of CHORUS — a combinatorial "
            "coastal energy column (osmotic, rhizospheric, orographic, solar). "
            "All power claims are bounded by thermodynamic and electrochemical limits "
            "derived in <i>differential-harness</i>.",
            styles["body"],
        )
    )

    story.append(Paragraph("Key numerical results", styles["h2"]))
    rows = [["Quantity", "Value"]]
    for key, val in sorted(data.results.items()):
        if isinstance(val, float):
            display = fmt_float(val)
        else:
            display = str(val)
        rows.append([fmt_quantity_key(key), display])
    story.append(data_table(rows, theme))

    story.append(Paragraph("Ranked concepts", styles["h2"]))
    claims = data.claims
    for label, text in [
        ("Safest", claims.safest),
        ("Smartest", claims.smartest),
        ("Strangest", claims.strangest),
        ("Civilization-scale", claims.civilization),
    ]:
        story.append(Paragraph(f"<b>{label}:</b> {text}", styles["body"]))
        story.append(Spacer(1, 0.06))

    if data.constants:
        story.append(Paragraph("Model constants", styles["h2"]))
        for k, v in data.constants.items():
            story.append(Paragraph(f"<b>{k}</b>: {v}", styles["body"]))

    story.append(Paragraph("References", styles["h2"]))
    story.append(
        Paragraph(
            "Teng et al., Nat. Energy 2026 (blue energy); Fang et al., Energy Environ. Sci. 2026 "
            "(PV–MHD); Virgo et al., Glob. Chall. 2020 (atmospheric circuit). "
            "Full derivations: differential-harness/docs/CHORUS_MATH_PLAN.md",
            styles["body"],
        )
    )

    doc.build(story, onFirstPage=on_page(config), onLaterPages=on_page(config))
    return output.expanduser().resolve()
