from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, Spacer

from pdf_genesis.components.cover import build_cover_flowables
from pdf_genesis.components.table import data_table
from pdf_genesis.components.toc import toc_flowables
from pdf_genesis.config import ReportConfig
from pdf_genesis.repo.discover import collect_exports, collect_figures, collect_markdown
from pdf_genesis.repo.manifest import RepoManifest
from pdf_genesis.repo.markdown import markdown_to_flowables
from pdf_genesis.render.base import body_styles, make_doc, on_page, resolve_theme
from pdf_genesis.utils.paths import ensure_parent


def _json_summary_table(data: dict, max_rows: int = 24) -> list[list[str]]:
    rows = [["Key", "Value"]]

    def walk(prefix: str, obj, depth: int) -> None:
        if len(rows) > max_rows:
            return
        if isinstance(obj, dict):
            for k in sorted(obj.keys())[:12]:
                walk(f"{prefix}.{k}" if prefix else k, obj[k], depth + 1)
        elif isinstance(obj, list):
            rows.append([prefix, f"[list len={len(obj)}]"])
        else:
            rows.append([prefix, str(obj)[:80]])

    for k in sorted(data.keys())[:8]:
        walk(k, data[k], 0)
    return rows[: max_rows + 1]


def compile_repo_pdf(
    repo: RepoManifest,
    output: Path | None = None,
    config: ReportConfig | None = None,
) -> Path:
    out = output or (repo.root / repo.compile.output)
    out = ensure_parent(out.expanduser().resolve())
    config = config or ReportConfig(
        title=repo.title,
        author=repo.author or "pdf-genesis",
        organization=repo.organization,
        footer_text=repo.footer,
    )
    theme = resolve_theme(config)
    styles = body_styles(theme)
    doc = make_doc(out, config)
    story: list = []

    if config.include_cover:
        story.extend(
            build_cover_flowables(
                repo.title,
                repo.subtitle or "Compiled from repository markdown and exports",
                config,
                theme,
                meta_lines=[("Root", str(repo.root))],
            )
        )
        story.append(PageBreak())

    md_files = collect_markdown(repo)

    def _section_title(path: Path) -> str:
        try:
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[:60]:
                s = line.strip()
                if s.startswith("# ") and not s.startswith("## "):
                    return s[2:].strip().rstrip(":")
                if s.startswith("## ") and not s.startswith("### "):
                    # prefer first H2 only if no H1
                    return s[3:].strip()
        except OSError:
            pass
        return path.stem.replace("-", " ").replace("_", " ").title()

    def _toc_entries(path: Path) -> list[str]:
        """For a single manuscript, TOC = numbered H2 sections (not the filename)."""
        entries: list[str] = []
        try:
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                s = line.strip()
                if s.startswith("## ") and not s.startswith("### "):
                    title = s[3:].strip()
                    # skip subtitle-only H2s that are part of the title block
                    if title.lower() in {"abstract", "keywords"}:
                        continue
                    if title.startswith("CRANKL —") or title.startswith("Deepiri"):
                        continue
                    entries.append(title)
        except OSError:
            pass
        return entries or [_section_title(path)]

    section_names: list[str] = []
    if len(md_files) == 1:
        section_names = _toc_entries(md_files[0])
    else:
        section_names = [_section_title(p) for p in md_files]

    if config.include_toc and section_names:
        story.extend(toc_flowables(section_names, theme))
    else:
        story.append(Paragraph("Document index", styles["h2"]))
        for name in section_names:
            story.append(Paragraph(f"• {name}", styles["body"]))
        story.append(PageBreak())

    for md in md_files:
        skip = len(md_files) == 1 or md.name in {"source.md", "paper.md", "main.md"}
        story.extend(
            markdown_to_flowables(
                md,
                theme,
                section_prefix=None if skip else _section_title(md),
                skip_title=skip,
            )
        )
        story.append(PageBreak())

    exports = collect_exports(repo)
    if exports:
        story.append(Paragraph("Export summaries", styles["h2"]))
        for exp in exports:
            rel = exp.relative_to(repo.root)
            story.append(Paragraph(f"<b>{rel}</b>", styles["body"]))
            try:
                data = json.loads(exp.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    story.append(data_table(_json_summary_table(data), theme))
            except json.JSONDecodeError:
                story.append(Paragraph("<i>Invalid JSON — skipped</i>", styles["muted"]))
            story.append(Spacer(1, 12))

    figures = collect_figures(repo)
    if figures:
        story.append(Paragraph("Figures", styles["h2"]))
        for i, fig in enumerate(figures, 1):
            rel = fig.relative_to(repo.root)
            try:
                img = Image(str(fig), width=5.2 * inch, height=3.0 * inch)
                story.append(img)
                story.append(Paragraph(f"<b>Figure {i}.</b> {rel}", styles["muted"]))
                story.append(Spacer(1, 12))
            except Exception:
                story.append(Paragraph(f"<i>Could not embed {rel}</i>", styles["muted"]))

    doc.build(story, onFirstPage=on_page(config), onLaterPages=on_page(config))
    return out
