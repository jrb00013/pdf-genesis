from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChorusClaims(BaseModel):
    safest: str = ""
    smartest: str = ""
    strangest: str = ""
    civilization: str = ""


class ChorusExport(BaseModel):
    title: str = "CHORUS Physics Proof"
    generated_at: datetime | str = ""
    constants: dict[str, Any] = Field(default_factory=dict)
    results: dict[str, float | int | str] = Field(default_factory=dict)
    claims: ChorusClaims = Field(default_factory=ChorusClaims)


class SkidSizingExport(BaseModel):
    P_target_W: float = 0
    A_mem_m2: float = 0
    n_plates: int = 0
    delta_pi_MPa: float = 0
    delta_P_star_bar: float = 0
    frame_L_mm: float = 0
    frame_W_mm: float = 0
    housing_od_mm: float = 0


class Sgh1DesignExport(BaseModel):
    title: str = "CHORUS-SGH-1 Design Report"
    sizing: SkidSizingExport | dict[str, Any] = Field(default_factory=dict)
    claims: ChorusClaims = Field(default_factory=ChorusClaims)
    bom_path: str = ""
    blueprint_path: str = ""


def load_export(path: str) -> ChorusExport | Sgh1DesignExport:
    import json
    from pathlib import Path

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "sizing" in data:
        return Sgh1DesignExport.model_validate(data)
    return ChorusExport.model_validate(data)
