from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle

from pdf_genesis.themes.base import ThemePalette


def data_table(
    rows: list[list[str]],
    theme: ThemePalette,
    col_widths: list[float] | None = None,
) -> Table:
    if col_widths is None:
        col_widths = [3.2 * inch, 2.8 * inch]
    table = Table(rows, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), theme.table_header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), theme.table_header_fg),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, theme.table_row_alt]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    table.setStyle(TableStyle(style))
    return table
