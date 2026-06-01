from pathlib import Path

import pytest

from pdf_genesis.loaders import detect_report_type, load_any
from pdf_genesis.schema import BenchReportExport, ChorusExport, PatentMemoExport, Sgh1DesignExport

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_chorus_sample():
    data = load_any(EXAMPLES / "chorus_results.sample.json")
    assert isinstance(data, ChorusExport)
    assert data.results["P_blue_W_m2"] == 15.0


def test_design_sample():
    data = load_any(EXAMPLES / "sgh1_design.sample.json")
    assert isinstance(data, Sgh1DesignExport)


def test_patent_sample():
    data = load_any(EXAMPLES / "patent_memo.sample.json")
    assert isinstance(data, PatentMemoExport)
    assert len(data.claims_list) == 2


def test_bench_sample():
    data = load_any(EXAMPLES / "bench_report.sample.json")
    assert isinstance(data, BenchReportExport)
    assert len(data.runs) == 2


def test_detect_types():
    import json

    chorus = json.loads((EXAMPLES / "chorus_results.sample.json").read_text())
    assert detect_report_type(chorus) == "chorus"
    patent = json.loads((EXAMPLES / "patent_memo.sample.json").read_text())
    assert detect_report_type(patent) == "patent"
