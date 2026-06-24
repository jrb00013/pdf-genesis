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
    inline_math_to_markup,
    render_display_equation,
    render_inline_math_paragraph,
)
from pdf_genesis.themes.base import ThemePalette

_HEADING = re.compile(r"^(#{1,6})\s+(.+)$")
_BULLET = re.compile(r"^[-*]\s+(.+)$")
_ORDERED = re.compile(r"^\d+\.\s+(.+)$")
_TABLE_SEP = re.compile(r"^\|?[\s:-]+\|[\s|:-]+\|?$")


def _inline_md(text: str) -> str:
    text = html.escape(text.strip())
    text = re.sub(r"`([^`]+)`", r"<font name='Courier' size='9' color='#2d3748'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    text = re.sub(r"_([^_]+)_", r"<i>\1</i>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<link href="\2" color="blue">\1</link>', text)
    return inline_math_to_markup(text)


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
    code_buf: list[str] = []
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

        if line.strip().startswith("$$") and line.strip().endswith("$$") and line.count("$$") >= 2:
            flush_para()
            latex = line.strip()[2:-2].strip()
            story.extend(render_display_equation(latex))
            continue

        para_buf.append(line)

    flush_para()
    flush_table()
    flush_code()
    story.append(Spacer(1, 12))
    return story
