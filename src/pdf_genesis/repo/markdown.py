from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.platypus import Paragraph, Preformatted, Spacer

from pdf_genesis.render.base import body_styles
from pdf_genesis.themes.base import ThemePalette


_HEADING = re.compile(r"^(#{1,6})\s+(.+)$")
_BULLET = re.compile(r"^[-*]\s+(.+)$")
_ORDERED = re.compile(r"^\d+\.\s+(.+)$")
_HTML_TAG = re.compile(r"<(/?)([bi])>")


def _inline_md(text: str) -> str:
    text = html.escape(text.strip())
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    text = re.sub(r"_([^_]+)_", r"<i>\1</i>", text)
    return text


def markdown_to_flowables(
    md_path: Path,
    theme: ThemePalette,
    *,
    section_prefix: str | None = None,
) -> list:
    styles = body_styles(theme)
    story: list = []
    rel = md_path.name
    try:
        rel = str(md_path.relative_to(md_path.parents[2]))
    except (ValueError, IndexError):
        rel = str(md_path)

    title = section_prefix or rel
    story.append(Paragraph(_inline_md(title), styles["h2"]))
    story.append(Spacer(1, 6))

    lines = md_path.read_text(encoding="utf-8", errors="replace").splitlines()
    in_code = False
    code_buf: list[str] = []

    def flush_code() -> None:
        nonlocal code_buf
        if code_buf:
            story.append(
                Preformatted(
                    "\n".join(code_buf),
                    styles["body"],
                    maxLineLength=120,
                )
            )
            story.append(Spacer(1, 6))
            code_buf = []

    for raw in lines:
        line = raw.rstrip()
        if line.strip().startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                flush_code()
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue

        hm = _HEADING.match(line)
        if hm:
            level = len(hm.group(1))
            text = _inline_md(hm.group(2))
            style = styles["h2"] if level <= 2 else styles["body"]
            if level >= 3:
                text = f"<b>{text}</b>"
            story.append(Paragraph(text, style))
            story.append(Spacer(1, 4))
            continue

        bm = _BULLET.match(line) or _ORDERED.match(line)
        if bm:
            story.append(Paragraph(f"• {_inline_md(bm.group(1))}", styles["body"]))
            continue

        if not line.strip():
            story.append(Spacer(1, 6))
            continue

        if line.strip() == "---":
            story.append(Spacer(1, 10))
            continue

        story.append(Paragraph(_inline_md(line), styles["body"]))
        story.append(Spacer(1, 3))

    flush_code()
    story.append(Spacer(1, 12))
    return story
