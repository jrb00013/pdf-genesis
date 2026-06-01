from __future__ import annotations

from pathlib import Path


def resolve_output(path: Path | str, default_name: str = "report.pdf") -> Path:
    p = Path(path).expanduser().resolve()
    if p.is_dir():
        return p / default_name
    return p


def ensure_parent(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
