from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pdf_genesis.schema import (
    BenchReportExport,
    ChorusExport,
    PatentMemoExport,
    Sgh1DesignExport,
    load_export,
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def detect_report_type(data: dict[str, Any]) -> str:
    if data.get("report_type"):
        return str(data["report_type"])
    if "sizing" in data and "claims" in data:
        return "design"
    if "results" in data and "constants" in data:
        return "chorus"
    if "claims_list" in data:
        return "patent"
    if "runs" in data:
        return "bench"
    return "chorus"


def load_any(path: Path) -> ChorusExport | Sgh1DesignExport | PatentMemoExport | BenchReportExport:
    data = load_json(path)
    kind = detect_report_type(data)
    if kind == "design":
        return Sgh1DesignExport.model_validate(data)
    if kind == "patent":
        return PatentMemoExport.model_validate(data)
    if kind == "bench":
        return BenchReportExport.model_validate(data)
    return ChorusExport.model_validate(data)
