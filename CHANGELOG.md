# Changelog

All notable changes to **dongnae** are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Test suite (`tests/`) covering the full public API — `where`, `nearest`,
  `within`, `resolve`, `search`, `get`, `howfar` — plus the encoding
  auto-detection fallback boundary (`utf-8-sig → cp949 → utf-8` and exhaustion),
  and regression tests for the large-radius bbox bug.
- GitHub Actions CI: `ruff` lint and `pytest` across Python 3.8–3.12.
- CI badge and a prominent "Try it live" demo link in the README.
- Zero-dependency `node --test` smoke/regression suite for the JS port.
- `CHANGELOG.md` (this file); `benchmark/requirements.txt`; missing `README.md`
  and `LICENSE.txt` for the `dongnae-kr` package (its build referenced both).

### Fixed
- **Large-radius nodes were silently dropped from spatial queries.** The
  bounding-box pre-filter used a fixed 5 km radius buffer, so any node whose
  radius exceeded it could be excluded from `where` / `nearest` / `within` /
  `resolve` even when the query sat inside it — while `howfar` (a direct id
  lookup) reported it as inside. The KR dataset has 1,359 such nodes (max
  ~53.8 km). The buffer now tracks the dataset's largest radius, so `where`
  and `howfar` agree. (Engine + JS port.)
- `load()` now validates required columns from the CSV header itself, so a
  wrong-schema file fails with a clear `ValueError` even with no data rows
  (previously it loaded silently as an empty engine). A well-formed header with
  zero rows still loads as a legitimately empty dataset.
- `within(..., limit=0)` now returns `[]` instead of all results, and
  `radius_km=0` is treated as a real zero range (was swallowed as falsy).
  (Engine + JS port.)
- `resolve()` no longer divides by zero when a node's radius (or the
  `threshold`) is 0 and the query sits on its centre — such a point scores a
  perfect `0.0` (Python raised `ZeroDivisionError`; JS returned `NaN`).
- **JS port** parity with the Python core:
  - `search("")` / whitespace queries now return `null` / `[]` instead of
    matching every node.
  - auto-calibration scans all latitudes (was sampling every 100th, which could
    miss the true min/max and diverge from Python).
  - `howfar` returns a raw (unrounded) value, like the core.
  - `where`/`nearest` fall back to a full scan when the bbox is empty, so they
    stay total (a far-away query returns the nearest node instead of `null`),
    matching the core.
- **Packaging:** shipped TypeScript types now point at the correct, complete
  `src/index.d.ts` (the previous `index.d.ts` declared `dnid: number` — it is a
  string — and omitted `resolve`/`howfar`); the broken `npm test` script now
  runs the new test suite.
- **Converter** (`data/CSVtoJSON.py`) no longer risks duplicating rows on an
  encoding fallback, and catches the same errors as the engine loader.

### Changed
- `requires-python` corrected to `>=3.8` for both `dongnae` and `dongnae-kr`
  (the engine relies on `typing.TypedDict`, added in 3.8).
- Type hints: `Optional[...]` for the nullable-defaulted parameters.
- README claims tightened: "Spatial Indexing" → "Bounding-Box Pre-filtering"
  (it is an O(n) pre-filter, not a persistent index), and the benchmark now
  states the speed figure is a local lookup vs a network API call.
- Benchmark no longer reports fake numbers silently: with no API key it prints a
  loud warning and stamps the report `SIMULATED`; runs are seeded for
  reproducibility.
- Web demo: rendered fields are HTML-escaped; the local demo server binds to
  `127.0.0.1` instead of all interfaces.
- JavaScript port (`@dongnae-js/data-kr`) README labelled **experimental /
  unpublished**; the CSV→JS conversion tooling under `data/` is now tracked in
  VCS so the dataset is reproducible from a clone.

> Still zero runtime dependencies — every change is standard-library / built-in
> only.

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
