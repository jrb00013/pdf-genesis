from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Preformatted, Spacer, Table, TableStyle

from pdf_genesis.render.base import body_styles
from pdf_genesis.render.math_render import (
    extract_display_math_blocks,
    render_display_equation,
    render_inline_math_paragraph,
)
from pdf_genesis.themes.base import ThemePalette

_HEADING = re.compile(r"^(#{1,6})\s+(.+)$")
_BULLET = re.compile(r"^[-*]\s+(.+)$")
_ORDERED = re.compile(r"^\d+\.\s+(.+)$")
_TABLE_SEP = re.compile(r"^\|?[\s:-]+\|[\s|:-]+\|?$")


def _inline_md(text: str) -> str:
    """Markdown inline → ReportLab markup.

    Math ($...$ / \\(...\\)) is stashed *before* underscore italics so
    subscripts like $H_C$ and $\\dim H^0$ render as math, not as ``H<i>C</i>``.
    """
    text = text.strip()

    math_spans: list[str] = []

    def _stash_math(m: re.Match) -> str:
        body = m.group(1) or m.group(2) or ""
        math_spans.append(body)
        return f"\x00MATH{len(math_spans) - 1}\x00"

    # Stash math first (raw, before html.escape) so '_' in latex is preserved.
    text = re.sub(
        r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)|\\\((.+?)\\\)",
        _stash_math,
        text,
        flags=re.S,
    )

    text = html.escape(text)

    code_spans: list[str] = []

    def _stash_code(m: re.Match) -> str:
        code_spans.append(m.group(1))
        return f"\x00CODE{len(code_spans) - 1}\x00"

    text = re.sub(r"`([^`]+)`", _stash_code, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    # Do NOT treat '_' as italics — conflicts with snake_case and leftover latex.
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<link href="\2" color="blue">\1</link>', text)
    for i, code in enumerate(code_spans):
        text = text.replace(
            f"\x00CODE{i}\x00",
            f"<font name='Courier' size='9' color='#2d3748'>{code}</font>",
        )
    # Restore math as §MATH§ markers for render_inline_math_paragraph
    for i, body in enumerate(math_spans):
        text = text.replace(f"\x00MATH{i}\x00", f"§MATH§{body}§/MATH§")
    return text


def _heading_style(level: int, styles: dict):
    if level == 1:
        return styles["h1"]
    if level == 2:
        return styles["h2"]
    if level == 3:
        return styles["h3"]
    return styles["body"]


def _parse_table_row(line: str) -> list[str]:
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def _table_flowable(rows: list[list[str]], theme: ThemePalette) -> Table:
    from pdf_genesis.components.table import data_table

    if not rows:
        return data_table([["", ""]], theme)
    styled = data_table(rows, theme, col_widths=[5.8 * inch / max(len(rows[0]), 1)] * len(rows[0]))
    return styled


def markdown_to_flowables(
    md_path: Path,
    theme: ThemePalette,
    *,
    section_prefix: str | None = None,
    skip_title: bool = False,
) -> list:
    styles = body_styles(theme)
    story: list = []
    raw = md_path.read_text(encoding="utf-8", errors="replace")

    if section_prefix and not skip_title:
        story.append(Paragraph(_inline_md(section_prefix), styles["h1"]))
        story.append(Spacer(1, 8))

    lines = raw.splitlines()
    in_code = False
    in_display_math = False
    code_buf: list[str] = []
    math_buf: list[str] = []
    table_buf: list[list[str]] = []
    para_buf: list[str] = []

    def flush_para() -> None:
        nonlocal para_buf
        if not para_buf:
            return
        text = " ".join(para_buf).strip()
        para_buf = []
        if not text:
            return
        for block in extract_display_math_blocks(text):
            if isinstance(block, tuple) and block[0] == "math":
                story.extend(render_display_equation(block[1]))
            else:
                marked = _inline_md(str(block))
                if "§MATH§" in marked:
                    story.extend(render_inline_math_paragraph(marked, styles["body"]))
                else:
                    story.append(Paragraph(marked, styles["body"]))
                    story.append(Spacer(1, 4))

    def flush_code() -> None:
        nonlocal code_buf
        if code_buf:
            story.append(
                Preformatted(
                    "\n".join(code_buf),
                    styles["code"],
                    maxLineLength=100,
                )
            )
            story.append(Spacer(1, 8))
            code_buf = []

    def flush_table() -> None:
        nonlocal table_buf
        if table_buf:
            story.append(_table_flowable(table_buf, theme))
            story.append(Spacer(1, 10))
            table_buf = []

    for raw_line in lines:
        line = raw_line.rstrip()

        # Multi-line $$ ... $$ display math
        if in_display_math:
            if "$$" in line.strip():
                before, _, after = line.strip().partition("$$")
                if before.strip():
                    math_buf.append(before.strip())
                story.extend(render_display_equation(" ".join(math_buf)))
                math_buf = []
                in_display_math = False
                if after.strip():
                    para_buf.append(after.strip())
            else:
                math_buf.append(line.strip())
            continue

        if line.strip().startswith("```"):
            flush_para()
            flush_table()
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_buf.append(line)
            continue

        # Figure placeholders: ![Figure N. caption](figures/...)
        fig_m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line.strip())
        if fig_m:
            flush_para()
            flush_table()
            caption, rel = fig_m.group(1), fig_m.group(2)
            fig_path = (md_path.parent / rel).resolve()
            if fig_path.is_file():
                try:
                    from reportlab.platypus import Image as RLImage

                    story.append(RLImage(str(fig_path), width=5.2 * inch, height=3.0 * inch))
                except Exception:
                    story.append(
                        Paragraph(
                            f"<i>[Figure asset failed to load: {html.escape(rel)}]</i>",
                            styles["muted"],
                        )
                    )
            else:
                # Box placeholder so the paper still looks like a finished draft
                box = Table(
                    [[Paragraph(f"<b>FIGURE PLACEHOLDER</b><br/>{html.escape(caption or rel)}", styles["body"])]],
                    colWidths=[5.5 * inch],
                )
                box.setStyle(
                    TableStyle(
                        [
                            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#718096")),
                            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#edf2f7")),
                            ("TOPPADDING", (0, 0), (-1, -1), 28),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 28),
                            ("LEFTPADDING", (0, 0), (-1, -1), 12),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                        ]
                    )
                )
                story.append(box)
            if caption:
                story.append(Paragraph(f"<b>{html.escape(caption)}</b>", styles["muted"]))
            story.append(Spacer(1, 10))
            continue

        if line.strip().startswith("|") and "|" in line[1:]:
            flush_para()
            if _TABLE_SEP.match(line.strip()):
                continue
            table_buf.append(_parse_table_row(line))
            continue
        elif table_buf:
            flush_table()

        hm = _HEADING.match(line)
        if hm:
            flush_para()
            level = len(hm.group(1))
            text = _inline_md(hm.group(2))
            style = _heading_style(level, styles)
            if "§MATH§" in text:
                story.extend(render_inline_math_paragraph(text, style))
            else:
                story.append(Paragraph(text, style))
            story.append(Spacer(1, 6))
            continue

        bm = _BULLET.match(line) or _ORDERED.match(line)
        if bm:
            flush_para()
            bullet_text = _inline_md(bm.group(1))
            if "§MATH§" in bullet_text:
                story.extend(render_inline_math_paragraph(f"• {bullet_text}", styles["body"]))
            else:
                story.append(Paragraph(f"• {bullet_text}", styles["body"]))
            story.append(Spacer(1, 3))
            continue

        if not line.strip():
            flush_para()
            story.append(Spacer(1, 6))
            continue

        if line.strip() == "---":
            flush_para()
            story.append(Spacer(1, 12))
            continue

        stripped = line.strip()
        if stripped.startswith("$$") and stripped.endswith("$$") and stripped.count("$$") >= 2:
            flush_para()
            latex = stripped[2:-2].strip()
            story.extend(render_display_equation(latex))
            continue

        if stripped.startswith("$$"):
            flush_para()
            rest = stripped[2:].strip()
            if rest:
                math_buf.append(rest)
            in_display_math = True
            continue

        para_buf.append(line)

    flush_para()
    flush_table()
    flush_code()
    story.append(Spacer(1, 12))
    return story
