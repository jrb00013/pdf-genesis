from __future__ import annotations

from reportlab.lib.units import inch

from pdf_genesis import fonts
from pdf_genesis.config import ReportConfig
from pdf_genesis.themes.base import ThemePalette


def header_footer_canvas(
    canvas,
    doc,
    config: ReportConfig,
    theme: ThemePalette,
) -> None:
    """Draw a running header (title + org) and a footer with a page number.

    Skipped on the title page (page 1) so the cover stays clean.
    """

    fonts.ensure_fonts_registered()
    if doc.page <= 1 and config.include_cover:
        return

    canvas.saveState()

    page_w = doc.pagesize[0]
    left = doc.leftMargin
    right = page_w - doc.rightMargin

    # --- running header ---
    header_y = doc.pagesize[1] - doc.topMargin + 0.32 * inch
    canvas.setStrokeColor(theme.muted)
    canvas.setLineWidth(0.5)
    canvas.line(left, header_y - 0.08 * inch, right, header_y - 0.08 * inch)
    canvas.setFont(fonts.FONT_SANS, 8)
    canvas.setFillColor(theme.muted)
    canvas.drawString(left, header_y, config.title)
    if config.organization:
        canvas.drawRightString(right, header_y, config.organization)

    # --- footer ---
    footer_y = 0.5 * inch
    canvas.setStrokeColor(theme.muted)
    canvas.setLineWidth(0.5)
    canvas.line(left, footer_y + 0.18 * inch, right, footer_y + 0.18 * inch)
    canvas.setFont(fonts.FONT_SERIF, 8)
    canvas.setFillColor(theme.muted)
    canvas.drawString(left, footer_y, config.footer_text)
    canvas.drawRightString(right, footer_y, f"Page {doc.page}")

    canvas.restoreState()


def page_number_canvas(canvas, doc, footer_text: str) -> None:
    """Backwards-compatible footer-only variant (no theme/header available)."""

    fonts.ensure_fonts_registered()
    canvas.saveState()
    canvas.setFont(fonts.FONT_SERIF, 8)
    canvas.drawString(0.85 * inch, 0.5 * inch, footer_text)
    canvas.drawRightString(7.65 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()
