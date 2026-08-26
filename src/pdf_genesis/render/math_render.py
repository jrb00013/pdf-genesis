"""LaTeX math rendering for pdf-genesis (matplotlib mathtext → PNG).

Generic helpers only — no project-specific paper content.
"""

from __future__ import annotations

import io
import re
from functools import lru_cache

from reportlab.lib.units import inch
from reportlab.platypus import Flowable, Image, Paragraph, Spacer

_DISPLAY_DELIMS = (
    ("$$", "$$"),
    (r"\[", r"\]"),
)
_INLINE_PATTERN = re.compile(
    r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)|\\\((.+?)\\\)"
)


@lru_cache(maxsize=512)
def _render_mathtext(latex: str, fontsize: float, dpi: int) -> tuple[bytes, float, float]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Computer Modern mathtext — closest to real LaTeX in a pure-Python stack.
    matplotlib.rcParams["mathtext.fontset"] = "cm"
    matplotlib.rcParams["mathtext.default"] = "it"
    matplotlib.rcParams["figure.max_open_warning"] = 100

    clean = latex.strip()
    if not clean:
        raise ValueError("empty equation")

    fig = plt.figure(figsize=(0.01, 0.01))
    fig.patch.set_alpha(0.0)
    text = fig.text(0, 0, f"${clean}$", fontsize=fontsize, color="#1a202c")
    fig.canvas.draw()
    bbox = text.get_window_extent(fig.canvas.get_renderer())
    # Convert pixel bbox → inches with a small pad so glyphs are not clipped.
    width_in = (bbox.width + 8) / dpi
    height_in = (bbox.height + 6) / dpi
    width_in = max(width_in, 12 / dpi)
    height_in = max(height_in, 10 / dpi)

    fig.set_size_inches(width_in, height_in)
    text.set_position((0.04, 0.08))
    buf = io.BytesIO()
    fig.savefig(
        buf,
        format="png",
        dpi=dpi,
        transparent=True,
        bbox_inches="tight",
        pad_inches=0.02,
    )
    plt.close(fig)
    buf.seek(0)
    return buf.read(), width_in * inch, height_in * inch


def math_image(latex: str, *, display: bool = True, fontsize: float = 13.0) -> Image:
    dpi = 300 if display else 280
    png, w, h = _render_mathtext(latex, fontsize, dpi=dpi)
    max_w = 6.2 * inch if display else 5.8 * inch
    if w > max_w:
        scale = max_w / w
        w, h = w * scale, h * scale
    # Slight optical upscale for tiny inline glyphs
    if not display and h < 9:
        scale = 9 / h
        w, h = w * scale, h * scale
    img = Image(io.BytesIO(png), width=w, height=h)
    img.hAlign = "CENTER" if display else "LEFT"
    return img


def inline_math_to_markup(text: str) -> str:
    """Replace inline $...$ with placeholder markers for post-processing."""

    def repl(m: re.Match) -> str:
        body = m.group(1) or m.group(2) or ""
        return f"§MATH§{body}§/MATH§"

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


def _sanitize_mathtext(latex: str) -> str:
    """Normalize LaTeX toward the matplotlib mathtext subset."""
    s = latex.strip()
    s = re.sub(r"\\begin\{(?:aligned|align\*?|equation\*?|gather\*?|cases)\}", "", s)
    s = re.sub(r"\\end\{(?:aligned|align\*?|equation\*?|gather\*?|cases)\}", "", s)
    s = s.replace(r"\lVert", r"\|").replace(r"\rVert", r"\|")
    s = s.replace(r"\lvert", "|").replace(r"\rvert", "|")
    s = s.replace(r"\bigl", "").replace(r"\bigr", "")
    s = s.replace(r"\Bigl", "").replace(r"\Bigr", "")
    s = s.replace(r"\biggl", "").replace(r"\biggr", "")
    s = s.replace(r"\left", "").replace(r"\right", "")
    s = re.sub(
        r"\\binom\{([^{}]+)\}\{([^{}]+)\}",
        lambda m: f"C({m.group(1)},{m.group(2)})",
        s,
    )
    s = re.sub(r"\\operatorname\*?\{([^{}]+)\}", r"\\mathrm{\1}", s)
    s = re.sub(r"\\text\{([^{}]+)\}", r"\\mathrm{\1}", s)
    s = re.sub(r"\\boldsymbol\{([^{}]+)\}", r"\\mathbf{\1}", s)
    s = re.sub(r"\\textbf\{([^{}]+)\}", r"\\mathbf{\1}", s)
    s = s.replace(r"\lt ", r"\lt ").replace(r"\gt ", r"\gt ")
    # Raw < > break ReportLab if we ever fall back to HTML; mathtext wants \lt/\gt
    s = re.sub(r"(?<!\\)<(?!t )", r"\\lt ", s)
    s = re.sub(r"(?<!\\)>(?!t )", r"\\gt ", s)
    s = s.replace(r"\\", r"\; ")
    s = s.replace("&", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def render_display_equation(latex: str) -> list:
    import html as _html

    clean = _sanitize_mathtext(latex)
    try:
        return [Spacer(1, 4), math_image(clean, display=True, fontsize=14), Spacer(1, 8)]
    except Exception:
        return [
            Paragraph(f"<i>{_html.escape(clean)}</i>", _fallback_style()),
            Spacer(1, 6),
        ]


class _InlineMathProps:
    """Track bold/italic carry across math-split prose fragments."""

    __slots__ = ("tags",)

    def __init__(self) -> None:
        self.tags: list[str] = []

    def wrap(self, seg: str) -> str:
        prefixed = "".join(f"<{t}>" for t in self.tags) + seg
        stack: list[str] = []
        for m in re.finditer(r"</?(b|i|u)>", prefixed):
            tok, name = m.group(0), m.group(1)
            if tok.startswith("</"):
                if stack and stack[-1] == name:
                    stack.pop()
            else:
                stack.append(name)
        self.tags = stack
        return prefixed + "".join(f"</{t}>" for t in reversed(stack))


class MathAwareParagraph(Flowable):
    """Wrap prose + matplotlib math images onto lines within a frame width."""

    def __init__(self, pieces: list, style, gap: float = 3.0):
        super().__init__()
        self.pieces = pieces
        self.style = style
        self.gap = gap
        self._lines: list[list] = []
        self._heights: list[float] = []
        self.width = 0
        self.height = 0

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        lines: list[list] = []
        heights: list[float] = []
        row: list = []
        row_w = 0.0
        row_h = 0.0

        def flush():
            nonlocal row, row_w, row_h
            if not row:
                return
            lines.append(row)
            heights.append(row_h)
            row, row_w, row_h = [], 0.0, 0.0

        for piece in self.pieces:
            if isinstance(piece, str):
                if not piece:
                    continue
                # Split long prose on spaces so wrapping works
                words = piece.split(" ")
                buf = ""
                for i, w in enumerate(words):
                    chunk = w if i == len(words) - 1 else w + " "
                    trial = buf + chunk
                    p = Paragraph(trial, self.style)
                    tw, th = p.wrap(availWidth, availHeight)
                    # measure just the new word against remaining space
                    pw = Paragraph(chunk, self.style)
                    ww, wh = pw.wrap(availWidth, availHeight)
                    need = ww if not buf else Paragraph(buf + chunk, self.style).wrap(availWidth, availHeight)[0]
                    # simpler: if adding chunk exceeds remaining, flush buf first
                    test = Paragraph((buf + chunk).strip() or " ", self.style)
                    tw, th = test.wrap(min(availWidth, max(availWidth - row_w, 20)), availHeight)
                    # Use string width estimate via Paragraph on full buf+chunk limited to remaining
                    remaining = availWidth - row_w
                    if row and remaining < 18:
                        if buf:
                            bp = Paragraph(buf, self.style)
                            bw, bh = bp.wrap(availWidth, availHeight)
                            row.append(bp)
                            row_w += bw + self.gap
                            row_h = max(row_h, bh)
                            buf = ""
                        flush()
                        remaining = availWidth
                    cand = buf + chunk
                    cp = Paragraph(cand.strip() or " ", self.style)
                    cw, ch = cp.wrap(remaining if row else availWidth, availHeight)
                    if row and cw > remaining and buf:
                        bp = Paragraph(buf, self.style)
                        bw, bh = bp.wrap(availWidth, availHeight)
                        row.append(bp)
                        row_w += bw + self.gap
                        row_h = max(row_h, bh)
                        flush()
                        buf = chunk
                    elif row and cw > remaining and not buf:
                        flush()
                        buf = chunk
                    else:
                        buf = cand
                if buf.strip():
                    bp = Paragraph(buf, self.style)
                    bw, bh = bp.wrap(availWidth - row_w if row else availWidth, availHeight)
                    if row and bw > availWidth - row_w:
                        flush()
                        bw, bh = bp.wrap(availWidth, availHeight)
                    row.append(bp)
                    row_w += bw + self.gap
                    row_h = max(row_h, bh)
            else:
                # Image / flowable math
                mw, mh = piece.wrap(availWidth, availHeight)
                if row and row_w + mw > availWidth:
                    flush()
                row.append(piece)
                row_w += mw + self.gap
                row_h = max(row_h, mh)
        flush()
        self._lines = lines
        self._heights = heights
        self.height = sum(heights) + max(0, len(heights) - 1) * 2
        return self.width, self.height

    def draw(self):
        y = self.height
        for line, h in zip(self._lines, self._heights):
            y -= h
            x = 0.0
            for item in line:
                w, ih = item.wrap(self.width, h)
                # vertically center math images on the text line
                dy = (h - ih) / 2.0 if ih < h else 0.0
                item.drawOn(self.canv, x, y + dy)
                x += w + self.gap
            y -= 2
def render_inline_math_paragraph(text: str, style) -> list:
    """Render prose with CM math images (subscripts as math, not underscores).

    Returns a *flat, page-breakable* list of flowables so long abstracts cannot
    create a Table cell taller than the frame.
    """
    import html as _html

    segments = re.split(r"§MATH§(.+?)§/MATH§", text)
    if len(segments) == 1:
        return [Paragraph(text, style)]

    props = _InlineMathProps()
    out: list = []
    for idx, seg in enumerate(segments):
        if idx % 2 == 1:
            clean = _sanitize_mathtext(seg)
            try:
                out.append(math_image(clean, display=False, fontsize=11))
            except Exception:
                out.append(
                    Paragraph(
                        f"<font name='Courier' size='9'><i>{_html.escape(clean)}</i></font>",
                        style,
                    )
                )
            out.append(Spacer(1, 2))
            continue
        if not seg:
            continue
        out.append(Paragraph(props.wrap(seg), style))
        out.append(Spacer(1, 2))
    return out


def _fallback_style():
    from reportlab.lib.styles import ParagraphStyle

    return ParagraphStyle("EqFallback", fontSize=10, leading=13)
