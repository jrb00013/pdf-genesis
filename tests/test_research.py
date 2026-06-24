from pathlib import Path

import pytest

from pdf_genesis.render.math_render import math_image, render_display_equation
from pdf_genesis.repo.discover_project import discover_project
from pdf_genesis.repo.manifest import load_manifest
from pdf_genesis.repo.synthesize import build_research_pdf
from pdf_genesis.themes.base import get_theme

FUSELK = Path("/home/joeblack/Documents/Deepiri/deepiri-fuselk")


def test_math_render_produces_image():
    theme = get_theme("lab_white")
    del theme
    img = math_image(r"\frac{\partial n}{\partial t} = D \nabla^2 n")
    assert img.drawWidth > 0
    assert img.drawHeight > 0


def test_display_equation_flowable():
    flow = render_display_equation(r"E = mc^2")
    assert len(flow) >= 1


@pytest.mark.skipif(not FUSELK.exists(), reason="fuselk repo not present")
def test_discover_fuselk(tmp_path):
    repo = load_manifest(FUSELK)
    profile = discover_project(repo, run_benchmark=False)
    assert "fuselk" in profile.name.lower() or "deepiri" in profile.name.lower()
    assert profile.theory_files
    assert profile.experiments


@pytest.mark.skipif(not FUSELK.exists(), reason="fuselk repo not present")
def test_research_pdf_fuselk(tmp_path):
    repo = load_manifest(FUSELK)
    out = tmp_path / "fuselk_test.pdf"
    path = build_research_pdf(repo, output=out, run_benchmark=False)
    assert path.exists()
    assert path.stat().st_size > 8000
