from __future__ import annotations

from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, Spacer, Table, TableStyle

from pdf_genesis import fonts
from pdf_genesis.config import ReportConfig
from pdf_genesis.themes.base import ThemePalette


def build_cover_flowables(
    title: str,
    subtitle: str,
    config: ReportConfig,
    theme: ThemePalette,
    meta_lines: list[tuple[str, str]] | None = None,
) -> list:
    fonts.ensure_fonts_registered()
    styles = _cover_styles(theme)
    story: list = [Spacer(1, 1.2 * inch)]
    story.append(Paragraph(title, styles["title"]))
    story.append(
        HRFlowable(width="30%", thickness=1.2, color=theme.primary, spaceBefore=6, spaceAfter=14)
    )
    story.append(Paragraph(subtitle, styles["subtitle"]))
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph(config.organization, styles["org"]))
    if meta_lines:
        rows = [[k, v] for k, v in meta_lines]
        t = Table(rows, colWidths=[1.8 * inch, 3.5 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("TEXTCOLOR", (0, 0), (-1, -1), theme.text),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(t)
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(f"<i>{config.author}</i>", styles["muted"]))
    return story


def _cover_styles(theme: ThemePalette) -> dict:
    from reportlab.lib.styles import ParagraphStyle

    return {
        "title": ParagraphStyle(
            "CoverTitle",
            fontName=fonts.FONT_SANS_BOLD,
            fontSize=26,
            leading=30,
            textColor=theme.primary,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "CoverSub",
            fontName=fonts.FONT_SANS,
            fontSize=14,
            leading=18,
            textColor=theme.secondary,
            spaceAfter=12,
        ),
        "org": ParagraphStyle(
            "CoverOrg", fontName=fonts.FONT_SERIF, fontSize=11, textColor=theme.text
        ),
        "muted": ParagraphStyle(
            "CoverMuted", fontName=fonts.FONT_SERIF_ITALIC, fontSize=9, textColor=theme.muted
        ),
    }
