#!/usr/bin/env bash
# Incremental commit history for pdf-genesis beef-up
set -euo pipefail
cd "$(dirname "$0")/.."

commit() {
  local msg="$1"
  shift
  git add "$@"
  git commit -m "$msg"
}

commit "Add MIT license." LICENSE
commit "Add ReportConfig for themes, margins, and cover options." src/pdf_genesis/config.py
commit "Add theme palette registry and base colors." src/pdf_genesis/themes/base.py src/pdf_genesis/themes/__init__.py
commit "Add lab_white theme for print-friendly reports." src/pdf_genesis/themes/lab_white.py
commit "Add chorus_dark theme for presentation-style PDFs." src/pdf_genesis/themes/chorus_dark.py
commit "Add formatters and path helpers." src/pdf_genesis/utils/
commit "Add cover page component." src/pdf_genesis/components/__init__.py src/pdf_genesis/components/cover.py
commit "Add styled data table component." src/pdf_genesis/components/table.py
commit "Add page numbers and table of contents components." src/pdf_genesis/components/header_footer.py src/pdf_genesis/components/toc.py
commit "Add figure flowable with caption support." src/pdf_genesis/components/figure.py
commit "Extend schemas for patent memo and bench report exports." src/pdf_genesis/schema.py
commit "Add JSON loaders with automatic report type detection." src/pdf_genesis/loaders.py
commit "Add shared document builder utilities for renderers." src/pdf_genesis/render/base.py
commit "Add CHORUS physics proof PDF renderer." src/pdf_genesis/render/chorus.py
commit "Add SGH-1 hardware design PDF renderer." src/pdf_genesis/render/design.py
commit "Add patent strategy memo PDF renderer." src/pdf_genesis/render/patent.py
commit "Add bench test log PDF renderer." src/pdf_genesis/render/bench.py
commit "Export render package public API." src/pdf_genesis/render/__init__.py
commit "Refactor builder to delegate to render package." src/pdf_genesis/builder.py
commit "Expand CLI with build, validate, batch, and themes subcommands." src/pdf_genesis/cli.py
commit "Expose package version 0.2.0." src/pdf_genesis/__init__.py
commit "Add sample JSON fixtures for all report types." examples/
commit "Add pytest schema validation and PDF smoke tests." tests/
commit "Bump to v0.2.0 and add dev optional dependencies." pyproject.toml
commit "Ignore venv, build artifacts, and generated PDFs." .gitignore
commit "Document package architecture and extension points." docs/ARCHITECTURE.md
commit "Add CLI reference for build, validate, and batch." docs/CLI.md
commit "Add changelog and contributing guide." CHANGELOG.md CONTRIBUTING.md
commit "Overhaul README with features, badges, and usage." README.md
commit "Add GitHub Actions CI for pytest and CLI smoke." .github/workflows/ci.yml

echo "Done. Total commits: $(git rev-list --count HEAD)"
