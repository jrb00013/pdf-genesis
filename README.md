# pdf-genesis

Generate a research-style PDF from **`differential-harness`** notebook exports.

## Install

```bash
cd ~/projects/pdf-genesis
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
# After running CHORUS_physics_proof.ipynb (last cell writes JSON):
pdf-genesis build ../differential-harness/exports/chorus_results.json -o CHORUS_report.pdf
```

Optional title override:

```bash
pdf-genesis build path/to/chorus_results.json -o out.pdf --title "CHORUS Feasibility"
```
