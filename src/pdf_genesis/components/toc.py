from __future__ import annotations

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, PageBreak, Paragraph, Spacer

from pdf_genesis import fonts
from pdf_genesis.themes.base import ThemePalette


def toc_flowables(sections: list[str], theme: ThemePalette) -> list:
    fonts.ensure_fonts_registered()
    h = ParagraphStyle(
        "TOCHead",
        fontName=fonts.FONT_SANS_BOLD,
        fontSize=17,
        textColor=theme.primary,
        spaceAfter=4,
    )
    item = ParagraphStyle(
        "TOCItem",
        fontName=fonts.FONT_SERIF,
        fontSize=11,
        textColor=theme.text,
        leftIndent=18,
        spaceAfter=7,
        leading=14,
    )
    story: list = [
        Paragraph("Table of Contents", h),
        HRFlowable(width="100%", thickness=0.75, color=theme.muted, spaceAfter=12),
    ]
    for i, sec in enumerate(sections, 1):
        # Dotted leader between the section title and its number gives the
        # entry a real typeset-TOC look instead of a bare bullet list.
        leader = "." * max(4, 90 - len(sec))
        story.append(Paragraph(f"{i}.&nbsp;&nbsp;{sec} <font color='#999999'>{leader}</font>", item))
    story.append(Spacer(1, 0.25 * inch))
    story.append(PageBreak())
    return story
