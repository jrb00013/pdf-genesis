from __future__ import annotations

from pathlib import Path
from typing import Callable

from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate

from pdf_genesis import fonts
from pdf_genesis.components.header_footer import header_footer_canvas
from pdf_genesis.config import ReportConfig
from pdf_genesis.themes.base import ThemePalette, get_theme
from pdf_genesis.utils.paths import ensure_parent


def page_size(name: str):
    return A4 if name == "a4" else letter


def make_doc(
    output: Path,
    config: ReportConfig,
) -> SimpleDocTemplate:
    output = ensure_parent(output.expanduser().resolve())
    m = config.margin_inch
    return SimpleDocTemplate(
        str(output),
        pagesize=page_size(config.page_size),
        rightMargin=m * 72,
        leftMargin=m * 72,
        topMargin=m * 72,
        bottomMargin=m * 72,
    )


def on_page(config: ReportConfig) -> Callable:
    theme = resolve_theme(config)

    def _canvas(canvas, doc):
        if config.include_page_numbers:
            header_footer_canvas(canvas, doc, config, theme)

    return _canvas


def resolve_theme(config: ReportConfig) -> ThemePalette:
    return get_theme(config.theme)


def body_styles(theme: ThemePalette) -> dict:
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

    fonts.ensure_fonts_registered()
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "DocTitle",
            parent=base["Title"],
            fontName=fonts.FONT_SANS_BOLD,
            fontSize=22,
            leading=26,
            textColor=theme.primary,
            spaceAfter=14,
        ),
        "h1": ParagraphStyle(
            "DocH1",
            parent=base["Heading1"],
            fontName=fonts.FONT_SANS_BOLD,
            fontSize=16,
            leading=20,
            textColor=theme.primary,
            spaceBefore=6,
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "DocH2",
            parent=base["Heading2"],
            fontName=fonts.FONT_SANS_BOLD,
            fontSize=13,
            leading=17,
            textColor=theme.secondary,
            spaceBefore=12,
            spaceAfter=6,
        ),
        "h3": ParagraphStyle(
            "DocH3",
            parent=base["Heading3"],
            fontName=fonts.FONT_SANS_BOLD,
            fontSize=11,
            leading=14,
            textColor=theme.secondary,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "DocBody",
            parent=base["BodyText"],
            fontName=fonts.FONT_SERIF,
            textColor=theme.text,
            fontSize=10.5,
            leading=15,
            spaceAfter=4,
        ),
        "code": ParagraphStyle(
            "DocCode",
            parent=base["Code"],
            fontSize=8.5,
            leading=11,
            fontName=fonts.FONT_MONO,
            backColor=theme.table_row_alt,
            leftIndent=8,
            rightIndent=8,
        ),
        "muted": ParagraphStyle(
            "DocMuted",
            parent=base["BodyText"],
            fontName=fonts.FONT_SERIF_ITALIC,
            fontSize=9,
            textColor=theme.muted,
            leading=12,
        ),
    }
