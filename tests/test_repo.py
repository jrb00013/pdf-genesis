from pathlib import Path

import pytest

from pdf_genesis.repo import build_repo, compile_repo_pdf, load_manifest

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "sample_repo"


def test_load_default_manifest():
    m = load_manifest(FIXTURE)
    assert m.root == FIXTURE.resolve()
    assert "Sample" in m.title or m.title == "sample_repo — Research Compendium"


def test_compile_fixture_repo(tmp_path):
    out = tmp_path / "compendium.pdf"
    m = load_manifest(FIXTURE)
    path = compile_repo_pdf(m, output=out)
    assert path.exists()
    assert path.stat().st_size > 2000


@pytest.mark.skipif(
    not (Path.home() / "projects" / "differential-harness" / "scripts" / "build_research_paper.py").exists()
    and not Path("/home/josep/projects/differential-harness/scripts/build_research_paper.py").exists(),
    reason="differential-harness not present",
)
def test_differential_harness_manifest_load():
    dh = Path("/home/josep/projects/differential-harness")
    if not dh.exists():
        pytest.skip("differential-harness not found")
    m = load_manifest(dh)
    assert m.builder == "scripts/build_research_paper.py"
    assert m.pipeline == "scripts/run_paper_pipeline.sh"
