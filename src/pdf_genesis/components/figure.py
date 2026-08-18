from __future__ import annotations

from pathlib import Path

from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, Spacer

from pdf_genesis import fonts
from pdf_genesis.themes.base import ThemePalette


def figure_flowable(
    path: Path,
    caption: str,
    theme: ThemePalette,
    max_width: float = 5.5 * inch,
    max_height: float = 4 * inch,
) -> list:
    from reportlab.lib.styles import ParagraphStyle

    fonts.ensure_fonts_registered()

    if not path.exists():
        cap = ParagraphStyle(
            "Cap", fontName=fonts.FONT_SERIF_ITALIC, fontSize=9, textColor=theme.muted
        )
        return [Paragraph(f"<i>[Missing figure: {path.name}]</i>", cap)]

    img = Image(str(path))
    iw, ih = img.imageWidth, img.imageHeight
    scale = min(max_width / iw, max_height / ih, 1.0)
    img.drawWidth = iw * scale
    img.drawHeight = ih * scale
    cap_style = ParagraphStyle(
        "FigCap",
        fontName=fonts.FONT_SERIF_ITALIC,
        fontSize=9,
        textColor=theme.muted,
        alignment=1,
        spaceBefore=2,
    )
    return [img, Spacer(1, 0.1 * inch), Paragraph(caption, cap_style), Spacer(1, 0.18 * inch)]
