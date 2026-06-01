from __future__ import annotations

from pathlib import Path

from pdf_genesis.config import ReportConfig
from pdf_genesis.render import render_bench_pdf, render_design_pdf, render_physics_pdf
from pdf_genesis.schema import BenchReportExport, DesignExport, PhysicsExport


def build_pdf(
    data: PhysicsExport,
    output: Path,
    config: ReportConfig | None = None,
) -> Path:
    return render_physics_pdf(data, output, config)


def build_design_pdf(
    data: DesignExport,
    output: Path,
    config: ReportConfig | None = None,
) -> Path:
    return render_design_pdf(data, output, config)


def build_bench_pdf(
    data: BenchReportExport,
    output: Path,
    config: ReportConfig | None = None,
) -> Path:
    return render_bench_pdf(data, output, config)
