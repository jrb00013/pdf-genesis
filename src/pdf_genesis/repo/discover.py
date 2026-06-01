from __future__ import annotations

from pathlib import Path

from pdf_genesis.repo.manifest import CompileConfig, RepoManifest


def _matches_exclude(rel: str, exclude: list[str]) -> bool:
    rel_posix = rel.replace("\\", "/")
    for pat in exclude:
        pat = pat.replace("\\", "/")
        if pat.endswith("/") and rel_posix.startswith(pat):
            return True
        if pat in rel_posix or rel_posix == pat or rel_posix.endswith("/" + pat):
            return True
    return False


def collect_markdown(repo: RepoManifest) -> list[Path]:
    cfg = repo.compile
    seen: set[Path] = set()
    ordered: list[Path] = []
    for pattern in cfg.include_globs:
        for path in sorted(repo.root.glob(pattern)):
            if not path.is_file() or path.suffix.lower() not in {".md", ".markdown"}:
                continue
            rel = str(path.relative_to(repo.root))
            if _matches_exclude(rel, cfg.exclude):
                continue
            key = path.resolve()
            if key not in seen:
                seen.add(key)
                ordered.append(path)
    return ordered


def collect_figures(repo: RepoManifest) -> list[Path]:
    return sorted(repo.root.glob(repo.compile.figures_glob))


def collect_exports(repo: RepoManifest) -> list[Path]:
    paths: list[Path] = []
    for rel in repo.compile.exports:
        p = repo.root / rel
        if p.is_file():
            paths.append(p)
    if not paths:
        exp = repo.root / "exports"
        if exp.is_dir():
            paths = sorted(exp.glob("*.json"))
    return paths
