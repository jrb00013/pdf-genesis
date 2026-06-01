from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pdf_genesis.schema import (
    BenchReportExport,
    DesignExport,
    PhysicsExport,
    _normalize_design,
    _normalize_physics,
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def detect_report_type(data: dict[str, Any]) -> str:
    rt = data.get("report_type")
    if rt in ("physics", "chorus"):
        return "physics"
    if rt in ("design", "hardware"):
        return "design"
    if rt == "bench":
        return "bench"
    if "sizing" in data:
        return "design"
    if "runs" in data:
        return "bench"
    if "results" in data:
        return "physics"
    return "physics"


def load_any(path: Path) -> PhysicsExport | DesignExport | BenchReportExport:
    data = load_json(path)
    kind = detect_report_type(data)
    if kind == "design":
        return DesignExport.model_validate(_normalize_design(data))
    if kind == "bench":
        return BenchReportExport.model_validate(data)
    return PhysicsExport.model_validate(_normalize_physics(data))
