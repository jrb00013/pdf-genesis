from reportlab.lib import colors

from pdf_genesis.themes.base import ThemePalette, register

register(
    ThemePalette(
        name="lab_white",
        primary=colors.HexColor("#1a365d"),
        secondary=colors.HexColor("#2c5282"),
        accent=colors.HexColor("#38a169"),
        text=colors.HexColor("#1a202c"),
        muted=colors.HexColor("#718096"),
        table_header_bg=colors.HexColor("#1a365d"),
        table_header_fg=colors.white,
        table_row_alt=colors.HexColor("#f7fafc"),
        cover_bg=colors.HexColor("#edf2f7"),
    )
)
