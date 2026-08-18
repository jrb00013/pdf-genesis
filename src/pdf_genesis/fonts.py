"""Font registration for professional, academic-quality PDF typography.

Body text uses DejaVu Serif (a Bitstream Vera-derived, permissively licensed
serif face bundled with matplotlib) so that prose visually matches the
equation rendering already produced by matplotlib mathtext, instead of the
reportlab default (Helvetica/Times core fonts, which never embed and don't
match the equation raster fonts at all).

Headings use DejaVu Sans (bold weight) for a clean, modern sans-serif
contrast against the serif body -- a standard academic-report pairing.

Fonts are embedded TrueType fonts registered with reportlab's pdfmetrics, so
the resulting PDF is portable and renders identically everywhere, unlike the
reportlab "core" fonts which rely on a fixed 14-font PDF base set.
"""

from __future__ import annotations

import os
from functools import lru_cache

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Logical names used throughout pdf-genesis. These fall back to reportlab's
# built-in core fonts if the TTF files can't be located, so rendering never
# hard-fails even in a stripped-down environment.
FONT_SERIF = "DejaVuSerif"
FONT_SERIF_BOLD = "DejaVuSerif-Bold"
FONT_SERIF_ITALIC = "DejaVuSerif-Italic"
FONT_SERIF_BOLD_ITALIC = "DejaVuSerif-BoldItalic"

FONT_SANS = "DejaVuSans"
FONT_SANS_BOLD = "DejaVuSans-Bold"
FONT_SANS_ITALIC = "DejaVuSans-Oblique"
FONT_SANS_BOLD_ITALIC = "DejaVuSans-BoldOblique"

FONT_MONO = "Courier"


def _mpl_ttf_dir() -> str | None:
    try:
        import matplotlib

        d = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
        return d if os.path.isdir(d) else None
    except Exception:
        return None


@lru_cache(maxsize=1)
def ensure_fonts_registered() -> bool:
    """Register the DejaVu Serif/Sans families with reportlab.

    Returns True if the embeddable TTF families were registered, False if we
    fell back to reportlab's core (non-embedded) fonts. Safe to call many
    times; the actual registration only happens once per process.
    """

    ttf_dir = _mpl_ttf_dir()
    if not ttf_dir:
        _register_fallback()
        return False

    files = {
        FONT_SERIF: "DejaVuSerif.ttf",
        FONT_SERIF_BOLD: "DejaVuSerif-Bold.ttf",
        FONT_SERIF_ITALIC: "DejaVuSerif-Italic.ttf",
        FONT_SERIF_BOLD_ITALIC: "DejaVuSerif-BoldItalic.ttf",
        FONT_SANS: "DejaVuSans.ttf",
        FONT_SANS_BOLD: "DejaVuSans-Bold.ttf",
        FONT_SANS_ITALIC: "DejaVuSans-Oblique.ttf",
        FONT_SANS_BOLD_ITALIC: "DejaVuSans-BoldOblique.ttf",
    }

    try:
        for name, fname in files.items():
            path = os.path.join(ttf_dir, fname)
            if not os.path.exists(path):
                raise FileNotFoundError(path)
            pdfmetrics.registerFont(TTFont(name, path))

        # Register families so <b>/<i>/<b><i> markup inside reportlab
        # Paragraph text resolves to the right embedded weight/style
        # automatically instead of silently falling back to Helvetica.
        pdfmetrics.registerFontFamily(
            FONT_SERIF,
            normal=FONT_SERIF,
            bold=FONT_SERIF_BOLD,
            italic=FONT_SERIF_ITALIC,
            boldItalic=FONT_SERIF_BOLD_ITALIC,
        )
        pdfmetrics.registerFontFamily(
            FONT_SANS,
            normal=FONT_SANS,
            bold=FONT_SANS_BOLD,
            italic=FONT_SANS_ITALIC,
            boldItalic=FONT_SANS_BOLD_ITALIC,
        )
        return True
    except Exception:
        _register_fallback()
        return False


def _register_fallback() -> None:
    """Point the logical font names at reportlab's built-in core fonts.

    This keeps every call site working (they only ever reference the
    logical FONT_* names) even if the DejaVu TTFs aren't present.
    """

    global FONT_SERIF, FONT_SERIF_BOLD, FONT_SERIF_ITALIC, FONT_SERIF_BOLD_ITALIC
    global FONT_SANS, FONT_SANS_BOLD, FONT_SANS_ITALIC, FONT_SANS_BOLD_ITALIC

    FONT_SERIF = "Times-Roman"
    FONT_SERIF_BOLD = "Times-Bold"
    FONT_SERIF_ITALIC = "Times-Italic"
    FONT_SERIF_BOLD_ITALIC = "Times-BoldItalic"

    FONT_SANS = "Helvetica"
    FONT_SANS_BOLD = "Helvetica-Bold"
    FONT_SANS_ITALIC = "Helvetica-Oblique"
    FONT_SANS_BOLD_ITALIC = "Helvetica-BoldOblique"
