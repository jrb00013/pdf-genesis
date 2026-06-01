# Changelog

## [0.2.0] — 2026-06-01

### Added
- Theme system (`lab_white`, `chorus_dark`) and `ReportConfig`
- Reusable components: cover, tables, TOC, figures, page numbers
- Renderers for CHORUS, SGH-1 design, patent memo, and bench reports
- CLI subcommands: `validate`, `batch`, `themes`
- Example JSON fixtures and pytest smoke tests
- Documentation: ARCHITECTURE, CLI reference, CONTRIBUTING
- GitHub Actions CI
- MIT LICENSE

### Changed
- `build` command now uses subcommand syntax (`pdf-genesis build <json>`)
- Builder delegates to `render/` package

## [0.1.0] — 2026-06-01

- Initial scaffold: CHORUS and design PDF builders
