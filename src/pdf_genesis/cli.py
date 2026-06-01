from __future__ import annotations

import argparse
import json
from pathlib import Path

from pdf_genesis.builder import build_design_pdf, build_pdf
from pdf_genesis.schema import ChorusExport, Sgh1DesignExport, load_export


def main() -> None:
    parser = argparse.ArgumentParser(description="Build research PDF from CHORUS export JSON")
    parser.add_argument("input", type=Path, help="Path to export JSON")
    parser.add_argument("-o", "--output", type=Path, default=None)
    parser.add_argument("--title", type=str, default=None, help="Override document title")
    args = parser.parse_args()

    data = load_export(str(args.input))
    if args.title:
        data.title = args.title

    if isinstance(data, Sgh1DesignExport):
        out_path = args.output or Path("SGH1_Design_Report.pdf")
        out = build_design_pdf(data, out_path)
    else:
        out_path = args.output or Path("CHORUS_report.pdf")
        out = build_pdf(data, out_path)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
