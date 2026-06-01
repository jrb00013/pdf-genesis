from reportlab.lib import colors

from pdf_genesis.themes.base import ThemePalette, register

register(
    ThemePalette(
        name="chorus_dark",
        primary=colors.HexColor("#0d9488"),
        secondary=colors.HexColor("#115e59"),
        accent=colors.HexColor("#fbbf24"),
        text=colors.HexColor("#e2e8f0"),
        muted=colors.HexColor("#94a3b8"),
        table_header_bg=colors.HexColor("#134e4a"),
        table_header_fg=colors.white,
        table_row_alt=colors.HexColor("#1e293b"),
        cover_bg=colors.HexColor("#0f172a"),
    )
)
