from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib import colors


@dataclass(frozen=True)
class ThemePalette:
    name: str
    primary: colors.Color
    secondary: colors.Color
    accent: colors.Color
    text: colors.Color
    muted: colors.Color
    table_header_bg: colors.Color
    table_header_fg: colors.Color
    table_row_alt: colors.Color
    cover_bg: colors.Color


THEMES: dict[str, ThemePalette] = {}


def register(theme: ThemePalette) -> ThemePalette:
    THEMES[theme.name] = theme
    return theme


def get_theme(name: str) -> ThemePalette:
    from pdf_genesis.themes import chorus_dark, lab_white  # noqa: F401

    if name not in THEMES:
        raise KeyError(f"Unknown theme {name!r}; choose from {list(THEMES)}")
    return THEMES[name]
