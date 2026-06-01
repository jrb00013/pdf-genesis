from pathlib import Path

import pytest

from pdf_genesis.config import ReportConfig
from pdf_genesis.loaders import load_any
from pdf_genesis.render import render_bench_pdf, render_design_pdf, render_physics_pdf

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"
OUT = Path(__file__).resolve().parent / "_out"


@pytest.fixture(autouse=True)
def _mkdir():
    OUT.mkdir(exist_ok=True)


@pytest.mark.parametrize(
    "name,renderer",
    [
        ("physics_results.sample.json", render_physics_pdf),
        ("design_report.sample.json", render_design_pdf),
        ("bench_report.sample.json", render_bench_pdf),
    ],
)
def test_render_smoke(name: str, renderer):
    data = load_any(EXAMPLES / name)
    cfg = ReportConfig(include_cover=True, include_toc=False)
    out = renderer(data, OUT / f"{Path(name).stem}.pdf", cfg)
    assert out.exists()
    assert out.stat().st_size > 500
