from reportlab.lib import colors

from pdf_genesis.themes.base import ThemePalette, register

_palette = ThemePalette(
    name="dark",
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
register(_palette)
register(
    ThemePalette(
        name="chorus_dark",
        primary=_palette.primary,
        secondary=_palette.secondary,
        accent=_palette.accent,
        text=_palette.text,
        muted=_palette.muted,
        table_header_bg=_palette.table_header_bg,
        table_header_fg=_palette.table_header_fg,
        table_row_alt=_palette.table_row_alt,
        cover_bg=_palette.cover_bg,
    )
)
