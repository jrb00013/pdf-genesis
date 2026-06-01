from __future__ import annotations

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer

from pdf_genesis.themes.base import ThemePalette


def toc_flowables(sections: list[str], theme: ThemePalette) -> list:
    h = ParagraphStyle("TOCHead", fontSize=16, textColor=theme.primary, spaceAfter=12)
    item = ParagraphStyle("TOCItem", fontSize=11, textColor=theme.text, leftIndent=20, spaceAfter=6)
    story: list = [Paragraph("Table of Contents", h), Spacer(1, 0.1 * inch)]
    for i, sec in enumerate(sections, 1):
        story.append(Paragraph(f"{i}. {sec}", item))
    story.append(Spacer(1, 0.25 * inch))
    return story
