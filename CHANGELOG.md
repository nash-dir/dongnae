# Changelog

All notable changes to **dongnae** are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Test suite (`tests/`) covering the full public API — `where`, `nearest`,
  `within`, `resolve`, `search`, `get`, `howfar` — plus the encoding
  auto-detection fallback boundary (`utf-8-sig → cp949 → utf-8` and exhaustion).
- GitHub Actions CI: `ruff` lint and `pytest` across Python 3.8–3.12.
- CI badge and a prominent "Try it live" demo link in the README.
- `CHANGELOG.md` (this file).

### Fixed
- `load()` now validates the required columns from the CSV header itself, so a
  file with a wrong schema fails with a clear `ValueError` even when it has no
  data rows. Previously such a file loaded silently as an empty engine. A
  well-formed header with zero rows still loads as a legitimately empty dataset.

### Changed
- `requires-python` corrected to `>=3.8` (the engine relies on `typing.TypedDict`,
  which was added in 3.8).
- JavaScript port (`@dongnae-js/data-kr`) README now clearly labelled
  **experimental / unpublished** rather than left empty.

> Still zero runtime dependencies — the loader change is standard-library only.

## [0.2.0] — 2025-12-02

The "service-availability" release: distance from a neighbourhood's *edge*, a
ready-to-use Korean dataset, and a first benchmark.

### Added
- `howfar(lat, lon, dnid)` — boundary distance from a coordinate to a specific
  dongnae by id (negative inside, positive outside, `None` for unknown ids).
- Korean dataset-included distribution (`dongnae-kr`) so the engine can be used
  without supplying your own CSV.
- Benchmark against the VWorld geocoding API (~15–20× faster; 97.3% top-3
  neighbourhood hit rate on random Korean coordinates).
- Experimental JavaScript port (`@dongnae-js/data-kr`) for browser/edge use.

### Changed
- Documentation revised around the new boundary-distance workflow and benchmark
  numbers.

## [0.1.0] — 2025-11-19

Initial pre-release of the pure-Python core engine.

### Added
- `DongnaeEngine` with reverse geocoding (`where`), K-nearest (`nearest`),
  radius search (`within`), soft geofencing (`resolve`), text search (`search`),
  and O(1) id lookup (`get`).
- CSV loading with automatic encoding detection and latitude-based
  auto-calibration of distance coefficients.
- Zero runtime dependencies — standard-library `csv` and `math` only.

[Unreleased]: https://github.com/nash-dir/dongnae/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/nash-dir/dongnae/releases/tag/v0.2.0
[0.1.0]: https://github.com/nash-dir/dongnae/releases/tag/v0.1.0
