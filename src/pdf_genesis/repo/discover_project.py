from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from pdf_genesis.repo.manifest import RepoManifest


@dataclass
class ExperimentEntry:
    id: str
    name: str
    category: str
    status: str
    description: str


@dataclass
class ProjectProfile:
    name: str
    version: str
    description: str
    authors: list[str]
    keywords: list[str]
    repository: str
    readme_summary: str
    vision_summary: str
    modules: list[str]
    experiments: list[ExperimentEntry]
    theory_files: list[Path]
    doc_files: list[Path]
    benchmark_script: Path | None
    benchmark_data: dict = field(default_factory=dict)
    changelog_highlights: list[str] = field(default_factory=list)
    root: Path | None = None


def _read_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        import tomllib

        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _first_paragraphs(md_path: Path, max_chars: int = 900) -> str:
    if not md_path.exists():
        return ""
    lines: list[str] = []
    for line in md_path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        if s.startswith("```") or s.startswith("|") or s.startswith("!["):
            continue
        if not s:
            if lines:
                break
            continue
        lines.append(s)
    text = " ".join(lines)
    return text[:max_chars] + ("…" if len(text) > max_chars else "")


def _discover_modules(root: Path) -> list[str]:
    modules: list[str] = []
    for base in (root / "src", root):
        if not base.is_dir():
            continue
        for init in sorted(base.rglob("__init__.py")):
            rel = init.parent.relative_to(base)
            if rel.parts and rel.parts[0] != ".":
                modules.append(".".join(rel.parts))
    return sorted(set(modules))[:24]


def _load_experiments(root: Path) -> list[ExperimentEntry]:
    reg = root / "experiments" / "registry.yaml"
    if not reg.exists():
        return []
    out: list[ExperimentEntry] = []
    current: dict[str, str] = {}
    for line in reg.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\s+-\s+id:\s+(.+)$", line)
        if m:
            if current.get("id"):
                out.append(_experiment_from_dict(current))
            current = {"id": m.group(1).strip()}
            continue
        for key in ("name", "category", "status", "description", "module"):
            km = re.match(rf"^\s+{key}:\s+(.+)$", line)
            if km and current:
                current[key] = km.group(1).strip()
    if current.get("id"):
        out.append(_experiment_from_dict(current))
    return out


def _experiment_from_dict(d: dict[str, str]) -> ExperimentEntry:
    return ExperimentEntry(
        id=d.get("id", ""),
        name=d.get("name", ""),
        category=d.get("category", ""),
        status=d.get("status", ""),
        description=d.get("description", ""),
    )


def _changelog_highlights(root: Path, limit: int = 6) -> list[str]:
    path = root / "CHANGELOG.md"
    if not path.exists():
        return []
    bullets: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip().startswith("- "):
            bullets.append(line.strip()[2:].strip())
        if len(bullets) >= limit:
            break
    return bullets


def _try_benchmark(script: Path, root: Path) -> dict:
    if not script.exists():
        return _load_export_benchmarks(root)
    rel = script.relative_to(root)
    commands = [
        ["poetry", "run", "python", str(rel), "--all", "--rl-steps", "1000"],
        [sys.executable, str(rel), "--all", "--rl-steps", "1000"],
    ]
    for cmd in commands:
        try:
            proc = subprocess.run(
                cmd,
                cwd=root,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if proc.returncode == 0 and proc.stdout.strip().startswith("{"):
                return json.loads(proc.stdout)
        except Exception:
            continue
    return _load_export_benchmarks(root)


def _load_export_benchmarks(root: Path) -> dict:
    exp = root / "exports"
    if not exp.is_dir():
        return {}
    for name in ("benchmark_raw.json", "fuselk_bench.json"):
        p = exp / name
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass
    return {}


def discover_project(repo: RepoManifest, *, run_benchmark: bool = True) -> ProjectProfile:
    root = repo.root
    pyproject = _read_toml(root / "pyproject.toml")
    poetry = pyproject.get("tool", {}).get("poetry", {})
    project = pyproject.get("project", {})

    name = (
        poetry.get("name")
        or project.get("name")
        or repo.title
        or root.name
    )
    version = poetry.get("version") or project.get("version") or "0.0.0"
    description = poetry.get("description") or project.get("description") or repo.subtitle or ""

    authors_raw = poetry.get("authors") or project.get("authors") or []
    authors: list[str] = []
    for a in authors_raw:
        if isinstance(a, str):
            authors.append(a)
        elif isinstance(a, dict):
            authors.append(a.get("name", ""))

    keywords = list(poetry.get("keywords") or project.get("keywords") or [])
    repository = str(poetry.get("repository") or project.get("urls", {}).get("Repository", ""))

    theory = sorted((root / "docs" / "theory").glob("*.md")) if (root / "docs" / "theory").is_dir() else []
    docs = sorted((root / "docs").glob("**/*.md")) if (root / "docs").is_dir() else []

    bench = root / "scripts" / "benchmark.py"
    if not bench.exists():
        bench = root / "benchmark.py"

    benchmark_data = _try_benchmark(bench, root) if run_benchmark else {}

    return ProjectProfile(
        name=name,
        version=version,
        description=description,
        authors=authors or ([repo.author] if repo.author else []),
        keywords=keywords,
        repository=repository,
        readme_summary=_first_paragraphs(root / "README.md"),
        vision_summary=_first_paragraphs(root / "VISION.md", max_chars=1200),
        modules=_discover_modules(root),
        experiments=_load_experiments(root),
        theory_files=theory,
        doc_files=[p for p in docs if p not in theory],
        benchmark_script=bench if bench.exists() else None,
        benchmark_data=benchmark_data,
        changelog_highlights=_changelog_highlights(root),
        root=root,
    )


def flatten_benchmark(bench: dict, prefix: str = "") -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []

    def walk(obj, pfx: str) -> None:
        if isinstance(obj, dict):
            for k, v in sorted(obj.items()):
                walk(v, f"{pfx}.{k}" if pfx else k)
        elif isinstance(obj, (list, tuple)):
            rows.append((pfx, f"[{len(obj)} items]"))
        else:
            rows.append((pfx, str(obj)))

    walk(bench, prefix)
    return rows[:32]
