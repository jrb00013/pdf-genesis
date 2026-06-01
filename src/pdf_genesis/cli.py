from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pdf_genesis.builder import build_bench_pdf, build_design_pdf, build_pdf
from pdf_genesis.config import ReportConfig, THEME_CHOICES
from pdf_genesis.loaders import detect_report_type, load_any
from pdf_genesis.schema import BenchReportExport, DesignExport, PhysicsExport


def cmd_build(args: argparse.Namespace) -> int:
    data = load_any(args.input)
    config = ReportConfig(
        title=args.title or getattr(data, "title", "Report"),
        theme=args.theme,
        include_cover=not args.no_cover,
        include_toc=not args.no_toc,
        footer_text=args.footer or ReportConfig().footer_text,
    )
    out = args.output or _default_output(data)
    if isinstance(data, DesignExport):
        path = build_design_pdf(data, out, config)
    elif isinstance(data, BenchReportExport):
        path = build_bench_pdf(data, out, config)
    else:
        path = build_pdf(data, out, config)
    print(f"Wrote {path}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    data = load_any(args.input)
    print(f"OK: {type(data).__name__} ({detect_report_type(json.loads(args.input.read_text()))})")
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    count = 0
    for path in sorted(args.inputs):
        out_dir = args.output_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / f"{path.stem}.pdf"
        ns = argparse.Namespace(
            input=path,
            output=out,
            title=None,
            theme=args.theme,
            no_cover=args.no_cover,
            no_toc=args.no_toc,
            footer=None,
        )
        cmd_build(ns)
        count += 1
    print(f"Built {count} PDF(s) in {out_dir}")
    return 0


def cmd_themes(_: argparse.Namespace) -> int:
    from pdf_genesis.themes.base import THEMES
    from pdf_genesis.themes import dark, lab_white  # noqa: F401

    for name in sorted(THEMES):
        print(name)
    return 0


def _default_output(data) -> Path:
    if isinstance(data, DesignExport):
        return Path("design_report.pdf")
    if isinstance(data, BenchReportExport):
        return Path("bench_report.pdf")
    return Path("physics_report.pdf")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build styled PDF reports from local JSON exports"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="Build a single PDF from JSON export")
    p_build.add_argument("input", type=Path)
    p_build.add_argument("-o", "--output", type=Path, default=None)
    p_build.add_argument("--title", type=str, default=None)
    p_build.add_argument("--theme", choices=THEME_CHOICES, default="lab_white")
    p_build.add_argument("--no-cover", action="store_true")
    p_build.add_argument("--no-toc", action="store_true")
    p_build.add_argument("--footer", type=str, default=None)
    p_build.set_defaults(func=cmd_build)

    p_val = sub.add_parser("validate", help="Validate export JSON against schema")
    p_val.add_argument("input", type=Path)
    p_val.set_defaults(func=cmd_validate)

    p_batch = sub.add_parser("batch", help="Build PDFs for multiple JSON files")
    p_batch.add_argument("inputs", type=Path, nargs="+")
    p_batch.add_argument("-o", "--output-dir", type=Path, default=Path("out"))
    p_batch.add_argument("--theme", choices=THEME_CHOICES, default="lab_white")
    p_batch.add_argument("--no-cover", action="store_true")
    p_batch.add_argument("--no-toc", action="store_true")
    p_batch.set_defaults(func=cmd_batch)

    sub.add_parser("themes", help="List available themes").set_defaults(func=cmd_themes)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
