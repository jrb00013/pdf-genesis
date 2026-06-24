from __future__ import annotations

from pathlib import Path

from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, Spacer

from pdf_genesis.components.cover import build_cover_flowables
from pdf_genesis.components.table import data_table
from pdf_genesis.components.toc import toc_flowables
from pdf_genesis.config import ReportConfig
from pdf_genesis.repo.discover_project import ProjectProfile, discover_project, flatten_benchmark
from pdf_genesis.repo.manifest import RepoManifest
from pdf_genesis.repo.markdown import markdown_to_flowables
from pdf_genesis.render.base import body_styles, make_doc, on_page, resolve_theme
from pdf_genesis.utils.paths import ensure_parent


def _section_title(text: str, styles: dict) -> list:
    return [Paragraph(text, styles["h1"]), Spacer(1, 10)]


def _body(text: str, styles: dict) -> list:
    if not text.strip():
        return []
    return [Paragraph(text, styles["body"]), Spacer(1, 8)]


def _abstract(profile: ProjectProfile) -> str:
    parts = [profile.description]
    if profile.vision_summary:
        parts.append(profile.vision_summary)
    if profile.readme_summary and profile.readme_summary not in parts[0]:
        parts.append(profile.readme_summary)
    return " ".join(p for p in parts if p).strip()


def _introduction(profile: ProjectProfile) -> str:
    intro = profile.readme_summary or profile.description
    if profile.keywords:
            intro += f" Key topics: {', '.join(profile.keywords[:8])}."
    if profile.repository:
        intro += f" Source: {profile.repository}."
    return intro


def _architecture_section(profile: ProjectProfile, styles: dict, theme) -> list:
    story: list = []
    story.extend(_section_title("System Architecture", styles))
    arch = next((p for p in profile.doc_files if p.name == "architecture.md"), None)
    if arch:
        story.extend(markdown_to_flowables(arch, theme, skip_title=True))
    elif profile.modules:
        story.extend(
            _body(
                "The codebase is organized into the following Python packages, "
                "discovered automatically from the repository layout.",
                styles,
            )
        )
    if profile.modules:
        rows = [["Package", "Role"]]
        for mod in profile.modules:
            role = mod.split(".")[-1].replace("_", " ").title()
            rows.append([mod, role])
        story.append(data_table(rows, theme, col_widths=[3.2 * inch, 2.6 * inch]))
        story.append(Spacer(1, 12))
    return story


def _experiments_section(profile: ProjectProfile, styles: dict, theme) -> list:
    story: list = []
    if not profile.experiments:
        return story
    story.extend(_section_title("Experiments", styles))
    rows = [["ID", "Category", "Status", "Description"]]
    for exp in profile.experiments:
        rows.append([exp.id, exp.category, exp.status, exp.description[:80]])
    story.append(data_table(rows, theme, col_widths=[1.3 * inch, 1.0 * inch, 0.9 * inch, 2.6 * inch]))
    story.append(Spacer(1, 12))
    return story


def _results_section(profile: ProjectProfile, styles: dict, theme) -> list:
    story: list = []
    bench = profile.benchmark_data
    if not bench:
        return story
    story.extend(_section_title("Results", styles))
    protocol = "scripts/benchmark.py"
    if profile.benchmark_script and profile.root:
        try:
            protocol = str(profile.benchmark_script.relative_to(profile.root))
        except ValueError:
            protocol = profile.benchmark_script.name
    story.extend(
        _body(
            f"Benchmark metrics below were collected from <b>{protocol}</b> "
            f"at paper generation time.",
            styles,
        )
    )
    rows = [["Metric", "Value"]]
    for key, val in flatten_benchmark(bench):
        rows.append([key.replace("_", " "), val])
    story.append(data_table(rows, theme))
    story.append(Spacer(1, 12))
    return story


def _roadmap_section(profile: ProjectProfile, styles: dict) -> list:
    story: list = []
    if profile.changelog_highlights:
        story.extend(_section_title("Recent Development", styles))
        for item in profile.changelog_highlights:
            story.append(Paragraph(f"• {item}", styles["body"]))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 8))
    return story


def _theory_section(profile: ProjectProfile, theme, styles: dict) -> list:
    story: list = []
    if not profile.theory_files:
        return story
    story.extend(_section_title("Theoretical Foundation", styles))
    for tf in profile.theory_files:
        title = tf.stem.replace("_", " ").title()
        story.append(Paragraph(title, styles["h2"]))
        story.append(Spacer(1, 6))
        story.extend(markdown_to_flowables(tf, theme, skip_title=True))
    return story


def _references(profile: ProjectProfile, styles: dict) -> list:
    story: list = []
    story.extend(_section_title("References", styles))
    refs: list[str] = []
    if profile.repository:
        refs.append(f"{profile.name} source repository. {profile.repository}")
    refs.append("pdf-genesis research paper synthesizer.")
    for i, ref in enumerate(refs, 1):
        story.append(Paragraph(f"[{i}] {ref}", styles["body"]))
        story.append(Spacer(1, 4))
    return story


def build_research_pdf(
    repo: RepoManifest,
    output: Path | None = None,
    config: ReportConfig | None = None,
    *,
    run_benchmark: bool = True,
) -> Path:
    out = output or (repo.root / repo.compile.output)
    out = ensure_parent(out.expanduser().resolve())

    profile = discover_project(repo, run_benchmark=run_benchmark)

    config = config or ReportConfig(
        title=repo.title or profile.name,
        author=repo.author or (profile.authors[0] if profile.authors else "pdf-genesis"),
        organization=repo.organization,
        footer_text=repo.footer,
    )
    if not config.title:
        config.title = profile.name

    theme = resolve_theme(config)
    styles = body_styles(theme)
    doc = make_doc(out, config)

    section_names = [
        "Abstract",
        "Introduction",
        "System Architecture",
        "Theoretical Foundation",
        "Experiments",
        "Results",
        "Recent Development",
        "References",
    ]
    story: list = []

    if config.include_cover:
        meta = [
            ("Version", profile.version),
            ("Generated from", str(repo.root.name)),
        ]
        if profile.keywords:
            meta.append(("Keywords", ", ".join(profile.keywords[:6])))
        story.extend(
            build_cover_flowables(
                config.title,
                repo.subtitle or profile.description or "Research Paper",
                config,
                theme,
                meta_lines=meta,
            )
        )
        story.append(PageBreak())

    if config.include_toc:
        story.extend(toc_flowables([s for s in section_names if _section_enabled(s, profile)], theme))
        story.append(PageBreak())

    story.extend(_section_title("Abstract", styles))
    story.extend(_body(_abstract(profile), styles))
    story.append(PageBreak())

    story.extend(_section_title("Introduction", styles))
    story.extend(_body(_introduction(profile), styles))
    if profile.vision_summary:
        story.extend(_body(profile.vision_summary, styles))
    story.append(PageBreak())

    story.extend(_architecture_section(profile, styles, theme))
    story.append(PageBreak())

    theory = _theory_section(profile, theme, styles)
    if theory:
        story.extend(theory)
        story.append(PageBreak())

    exp = _experiments_section(profile, styles, theme)
    if exp:
        story.extend(exp)
        story.append(PageBreak())

    res = _results_section(profile, styles, theme)
    if res:
        story.extend(res)
        story.append(PageBreak())

    road = _roadmap_section(profile, styles)
    if road:
        story.extend(road)
        story.append(PageBreak())

    story.extend(_references(profile, styles))

    doc.build(story, onFirstPage=on_page(config), onLaterPages=on_page(config))
    return out


def _section_enabled(name: str, profile: ProjectProfile) -> bool:
    if name == "Theoretical Foundation":
        return bool(profile.theory_files)
    if name == "Experiments":
        return bool(profile.experiments)
    if name == "Results":
        return bool(profile.benchmark_data)
    if name == "Recent Development":
        return bool(profile.changelog_highlights)
    return True
