from __future__ import annotations


def fmt_float(val: float, precision: int = 4) -> str:
    if abs(val) >= 1e6 or (abs(val) < 0.01 and val != 0):
        return f"{val:.4e}"
    return f"{val:.{precision}f}"


def fmt_quantity_key(key: str) -> str:
    return key.replace("_", " ").replace("MPa", " MPa").replace("W m2", " W/m²")
