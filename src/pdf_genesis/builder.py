from __future__ import annotations

from pathlib import Path

from pdf_genesis.config import ReportConfig
from pdf_genesis.render import (
    render_bench_pdf,
    render_chorus_pdf,
    render_design_pdf,
    render_patent_pdf,
)
from pdf_genesis.schema import (
    BenchReportExport,
    ChorusExport,
    PatentMemoExport,
    Sgh1DesignExport,
)


def build_pdf(
    data: ChorusExport,
    output: Path,
    config: ReportConfig | None = None,
) -> Path:
    return render_chorus_pdf(data, output, config)


def build_design_pdf(
    data: Sgh1DesignExport,
    output: Path,
    config: ReportConfig | None = None,
) -> Path:
    return render_design_pdf(data, output, config)


def build_patent_pdf(
    data: PatentMemoExport,
    output: Path,
    config: ReportConfig | None = None,
) -> Path:
    return render_patent_pdf(data, output, config)


def build_bench_pdf(
    data: BenchReportExport,
    output: Path,
    config: ReportConfig | None = None,
) -> Path:
    return render_bench_pdf(data, output, config)
