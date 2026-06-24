from __future__ import annotations

import io
import re
from functools import lru_cache

from reportlab.lib.units import inch
from reportlab.platypus import Image, Spacer

_DISPLAY_DELIMS = (
    ("$$", "$$"),
    (r"\[", r"\]"),
)
_INLINE_PATTERN = re.compile(
    r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)|\\\((.+?)\\\)"
)


@lru_cache(maxsize=256)
def _render_mathtext(latex: str, fontsize: float, dpi: int) -> tuple[bytes, float, float]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    clean = latex.strip()
    if not clean:
        raise ValueError("empty equation")

    fig = plt.figure(figsize=(0.01, 0.01))
    fig.patch.set_alpha(0.0)
    text = fig.text(0, 0, f"${clean}$", fontsize=fontsize)
    fig.canvas.draw()
    bbox = text.get_window_extent(fig.canvas.get_renderer())
    width_in = max(bbox.width / dpi, 24) / dpi + 0.15
    height_in = max(bbox.height / dpi, 16) / dpi + 0.12

    fig.set_size_inches(width_in, height_in)
    text.set_position((0.05, 0.05))
    buf = io.BytesIO()
    fig.savefig(
        buf,
        format="png",
        dpi=dpi,
        transparent=True,
        bbox_inches="tight",
        pad_inches=0.04,
    )
    plt.close(fig)
    buf.seek(0)
    return buf.read(), width_in * inch, height_in * inch


def math_image(latex: str, *, display: bool = True, fontsize: float = 13.0) -> Image:
    png, w, h = _render_mathtext(latex, fontsize, dpi=200)
    max_w = 6.2 * inch
    if w > max_w:
        scale = max_w / w
        w, h = w * scale, h * scale
    img = Image(io.BytesIO(png), width=w, height=h)
    img.hAlign = "CENTER" if display else "LEFT"
    return img


def inline_math_to_markup(text: str) -> str:
    """Replace inline $...$ with placeholder markers for post-processing."""

    def repl(m: re.Match) -> str:
        body = m.group(1) or m.group(2) or ""
        token = f"§MATH§{body}§/MATH§"
        return token

    return _INLINE_PATTERN.sub(repl, text)


def extract_display_math_blocks(text: str) -> list[str | tuple[str, str]]:
    """Split text into prose segments and display-math latex strings."""
    parts: list[str | tuple[str, str]] = []
    i = 0
    while i < len(text):
        matched = False
        for open_d, close_d in _DISPLAY_DELIMS:
            if text.startswith(open_d, i):
                end = text.find(close_d, i + len(open_d))
                if end == -1:
                    continue
                if i > 0 and text[:i].strip():
                    parts.append(text[:i])
                parts.append(("math", text[i + len(open_d) : end].strip()))
                text = text[end + len(close_d) :]
                i = 0
                matched = True
                break
        if not matched:
            i += 1
    if text.strip():
        parts.append(text)
    return parts


def render_display_equation(latex: str) -> list:
    try:
        return [math_image(latex, display=True), Spacer(1, 8)]
    except Exception:
        from reportlab.platypus import Paragraph

        return [Paragraph(f"<i>{latex}</i>", _fallback_style()), Spacer(1, 6)]


def render_inline_math_paragraph(text: str, style) -> list:
    from reportlab.platypus import Paragraph

    segments = re.split(r"§MATH§(.+?)§/MATH§", text)
    if len(segments) == 1:
        return [Paragraph(text, style)]

    flow: list = []
    row: list = []
    for idx, seg in enumerate(segments):
        if idx % 2 == 1:
            try:
                row.append(math_image(seg, display=False, fontsize=10))
            except Exception:
                row.append(Paragraph(f"<i>{seg}</i>", style))
        elif seg:
            row.append(Paragraph(seg, style))
    if row:
        from reportlab.platypus import Table

        t = Table([row], hAlign="LEFT")
        flow.append(t)
    return flow


def _fallback_style():
    from reportlab.lib.styles import ParagraphStyle

    return ParagraphStyle("EqFallback", fontSize=10, leading=13)
