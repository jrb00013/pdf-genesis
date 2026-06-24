from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from pdf_genesis.config import ReportConfig
from pdf_genesis.repo.compile import compile_repo_pdf
from pdf_genesis.repo.manifest import RepoManifest
from pdf_genesis.repo.synthesize import build_research_pdf


def run_pipeline(repo: RepoManifest) -> None:
    if not repo.pipeline:
        return
    script = repo.root / repo.pipeline
    if not script.exists():
        raise FileNotFoundError(f"Pipeline not found: {script}")
    if script.suffix == ".sh":
        subprocess.run(["bash", str(script)], cwd=repo.root, check=True, env=os.environ.copy())
    else:
        subprocess.run([sys.executable, str(script)], cwd=repo.root, check=True)


def run_builder(repo: RepoManifest) -> Path:
    if not repo.builder:
        raise ValueError("Manifest has no builder script")
    script = repo.root / repo.builder
    if not script.exists():
        raise FileNotFoundError(f"Builder not found: {script}")
    subprocess.run([sys.executable, str(script)], cwd=repo.root, check=True)
    if repo.output:
        out = (repo.root / repo.output).resolve()
        if not out.exists():
            raise FileNotFoundError(f"Builder finished but output missing: {out}")
        return out
    raise ValueError("Manifest builder has no output path")


def build_repo(
    repo: RepoManifest,
    *,
    mode: str = "auto",
    output: Path | None = None,
    skip_pipeline: bool = False,
    run_benchmark: bool = True,
) -> Path:
    """
    mode:
      auto — pipeline+builder if manifest defines builder; else research or compile
      full — pipeline + builder (requires builder in manifest)
      research — synthesized research paper from repo structure
      compile — markdown compendium only
    """
    if mode == "compile":
        return compile_repo_pdf(repo, output=output)

    if mode == "research":
        cfg = ReportConfig(
            title=repo.title,
            author=repo.author or "pdf-genesis",
            organization=repo.organization,
            footer_text=repo.footer,
        )
        out = output or (repo.root / repo.compile.output if repo.compile.output else None)
        return build_research_pdf(
            repo,
            output=out,
            config=cfg,
            run_benchmark=run_benchmark and not skip_pipeline,
        )

    if mode == "full" or (mode == "auto" and repo.builder):
        if not skip_pipeline and repo.pipeline:
            run_pipeline(repo)
        return run_builder(repo)

    if mode == "auto" and repo.paper_mode == "research":
        cfg = ReportConfig(
            title=repo.title,
            author=repo.author or "pdf-genesis",
            organization=repo.organization,
            footer_text=repo.footer,
        )
        out = output or (repo.root / repo.compile.output if repo.compile.output else None)
        return build_research_pdf(
            repo,
            output=out,
            config=cfg,
            run_benchmark=run_benchmark and not skip_pipeline,
        )

    return compile_repo_pdf(repo, output=output)
