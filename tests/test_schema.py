from pathlib import Path

import json

from pdf_genesis.loaders import detect_report_type, load_any
from pdf_genesis.schema import BenchReportExport, DesignExport, PhysicsExport

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_physics_sample():
    data = load_any(EXAMPLES / "physics_results.sample.json")
    assert isinstance(data, PhysicsExport)
    assert data.results["power_W"] == 12.5


def test_design_sample():
    data = load_any(EXAMPLES / "design_report.sample.json")
    assert isinstance(data, DesignExport)
    assert len(data.cad_files) == 3


def test_bench_sample():
    data = load_any(EXAMPLES / "bench_report.sample.json")
    assert isinstance(data, BenchReportExport)
    assert len(data.runs) == 2


def test_detect_types():
    physics = json.loads((EXAMPLES / "physics_results.sample.json").read_text())
    assert detect_report_type(physics) == "physics"
    design = json.loads((EXAMPLES / "design_report.sample.json").read_text())
    assert detect_report_type(design) == "design"
