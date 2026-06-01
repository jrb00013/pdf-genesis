from __future__ import annotations

from pathlib import Path
from typing import Callable

from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate

from pdf_genesis.components.header_footer import page_number_canvas
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
    def _canvas(canvas, doc):
        if config.include_page_numbers:
            page_number_canvas(canvas, doc, config.footer_text)

    return _canvas


def resolve_theme(config: ReportConfig) -> ThemePalette:
    return get_theme(config.theme)


def body_styles(theme: ThemePalette) -> dict:
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "DocTitle",
            parent=base["Title"],
            fontSize=20,
            textColor=theme.primary,
            spaceAfter=12,
        ),
        "h2": ParagraphStyle(
            "DocH2",
            parent=base["Heading2"],
            fontSize=13,
            textColor=theme.secondary,
            spaceBefore=12,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "DocBody",
            parent=base["BodyText"],
            fontSize=10,
            textColor=theme.text,
            leading=14,
        ),
        "muted": ParagraphStyle(
            "DocMuted",
            parent=base["BodyText"],
            fontSize=9,
            textColor=theme.muted,
        ),
    }
