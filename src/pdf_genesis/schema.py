from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class NarrativeNotes(BaseModel):
    """Optional labeled bullets — content comes from your JSON only."""

    safest: str = ""
    smartest: str = ""
    strangest: str = ""
    civilization: str = ""


class PhysicsExport(BaseModel):
    report_type: Literal["physics"] = "physics"
    title: str = "Physics Summary Report"
    subtitle: str = ""
    generated_at: datetime | str = ""
    abstract: str = ""
    constants: dict[str, Any] = Field(default_factory=dict)
    results: dict[str, float | int | str] = Field(default_factory=dict)
    notes: NarrativeNotes = Field(default_factory=NarrativeNotes)
    references: list[str] = Field(default_factory=list)


class SizingExport(BaseModel):
    P_target_W: float = 0
    A_mem_m2: float = 0
    n_plates: int = 0
    delta_pi_MPa: float = 0
    delta_P_star_bar: float = 0
    frame_L_mm: float = 0
    frame_W_mm: float = 0
    housing_od_mm: float = 0


class DesignExport(BaseModel):
    report_type: Literal["design"] = "design"
    title: str = "Hardware Design Report"
    subtitle: str = ""
    overview: str = ""
    sizing: SizingExport | dict[str, Any] = Field(default_factory=dict)
    notes: NarrativeNotes = Field(default_factory=NarrativeNotes)
    cad_files: list[str] = Field(default_factory=list)
    blueprint_path: str = ""
    bom_path: str = ""


class BenchRun(BaseModel):
    label: str
    timestamp: str = ""
    metrics: dict[str, float | int | str] = Field(default_factory=dict)


class BenchReportExport(BaseModel):
    report_type: Literal["bench"] = "bench"
    title: str = "Bench Test Report"
    protocol: str = ""
    runs: list[BenchRun] = Field(default_factory=list)
    pass_fail: str = ""


# Deprecated aliases (do not use in new exports)
ChorusClaims = NarrativeNotes
ChorusExport = PhysicsExport
Sgh1DesignExport = DesignExport
SkidSizingExport = SizingExport


def load_export(path: str) -> PhysicsExport | DesignExport:
    import json
    from pathlib import Path

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    kind = data.get("report_type", "physics")
    if kind in ("design", "hardware"):
        return DesignExport.model_validate(_normalize_design(data))
    return PhysicsExport.model_validate(_normalize_physics(data))


def _normalize_physics(data: dict[str, Any]) -> dict[str, Any]:
    out = dict(data)
    if out.get("report_type") == "chorus":
        out["report_type"] = "physics"
    if "claims" in out and "notes" not in out:
        out["notes"] = out.pop("claims")
    return out


def _normalize_design(data: dict[str, Any]) -> dict[str, Any]:
    out = dict(data)
    if "claims" in out and "notes" not in out:
        out["notes"] = out.pop("claims")
    return out
