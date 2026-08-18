"""Shared matplotlib theme and colorblind-safe palette for pdf-genesis clients.

This mirrors the pattern in ``fonts.py``: a small, dependency-light module
that downstream repos (e.g. differential-harness's research-paper figure
pipeline) import so that every generated chart shares one visual system
instead of each script hand-picking ad hoc matplotlib defaults.

Palette is the 8-color Okabe-Ito set, which remains distinguishable under
the common forms of color-vision deficiency (protanopia/deuteranopia) and
in grayscale print.
"""

from __future__ import annotations

from typing import Any

# Okabe & Ito (2008) colorblind-safe qualitative palette.
PALETTE = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky_blue": "#56B4E9",
    "green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
}

# Ordered cycle for series that need N distinct colors.
PALETTE_CYCLE = [
    PALETTE["blue"],
    PALETTE["vermillion"],
    PALETTE["green"],
    PALETTE["orange"],
    PALETTE["purple"],
    PALETTE["sky_blue"],
    PALETTE["yellow"],
    PALETTE["black"],
]

# Semantic roles used across figures for consistency.
ROLE = {
    "primary": PALETTE["blue"],
    "secondary": PALETTE["vermillion"],
    "tertiary": PALETTE["green"],
    "highlight": PALETTE["orange"],
    "reference": PALETTE["black"],
    "literature": PALETTE["purple"],
    "band": PALETTE["sky_blue"],
}

FIGURE_DPI = 300


def apply_house_style(matplotlib_module: Any) -> None:
    """Apply a consistent rcParams theme to an already-imported matplotlib.

    Call once per process, e.g.::

        import matplotlib
        matplotlib.use("Agg")
        from pdf_genesis.plotstyle import apply_house_style
        apply_house_style(matplotlib)
        import matplotlib.pyplot as plt
    """

    plt = matplotlib_module.pyplot if hasattr(matplotlib_module, "pyplot") else None
    rc = matplotlib_module.rcParams
    rc.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": FIGURE_DPI,
            "font.size": 10,
            "font.family": "DejaVu Sans",
            "axes.titlesize": 11,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "axes.edgecolor": "#333333",
            "axes.linewidth": 0.8,
            "axes.grid": True,
            "grid.alpha": 0.3,
            "grid.linewidth": 0.5,
            "legend.fontsize": 8,
            "legend.frameon": True,
            "legend.framealpha": 0.9,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "axes.prop_cycle": matplotlib_module.cycler(color=PALETTE_CYCLE),
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.05,
        }
    )
    if plt is not None:
        pass


def provenance_caption(ax: Any, text: str, *, kind: str = "simulated") -> None:
    """Stamp a small provenance footnote on a figure axis.

    ``kind`` is one of "simulated", "measured", "literature", or "mixed" and
    is prefixed automatically so every figure is honest about what it shows.
    """

    prefix = {
        "simulated": "Simulated (model output)",
        "measured": "Measured (bench data)",
        "literature": "Literature-cited",
        "mixed": "Simulated + literature-cited",
        "point_estimate": "Point estimate (no repeated-trial uncertainty data available)",
    }.get(kind, kind)
    ax.annotate(
        f"{prefix}: {text}",
        xy=(0.0, -0.28),
        xycoords="axes fraction",
        fontsize=6.5,
        color="#555555",
        ha="left",
        va="top",
        style="italic",
    )
