from __future__ import annotations

from reportlab.lib.units import inch


def page_number_canvas(canvas, doc, footer_text: str) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawString(0.85 * inch, 0.5 * inch, footer_text)
    canvas.drawRightString(7.65 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()
