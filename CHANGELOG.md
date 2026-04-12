# Changelog

All notable changes to pyhwpxlib are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-04-13

### Added
- Font embedding in SVG output: `render_page_svg(page, embed_fonts=True)`
  subsets used glyphs via fonttools, base64-encodes them as `@font-face`
  rules, and injects them into the SVG. Cross-platform identical rendering.
- `fonttools>=4.50` added to `[preview-fonts]` optional extras

### Fixed
- `hwp2hwpx.py`: strip UTF-8 surrogate characters before writing section XML
- Merged `feature/gso-converter` branch: GSO shape conversion (Picture,
  Rectangle, Ellipse, Line, Arc, Polygon, Curve, OLE, Container, TextArt,
  Form controls), header/footer + page numbering, tab leader handling,
  landscape orientation fix, BIN_DATA parsing fixes

## [0.2.0] - 2026-04-11

### Added
- `pyhwpxlib.rhwp_bridge` — HWP / HWPX → SVG renderer via bundled rhwp WASM
  - `RhwpEngine` and `RhwpDocument` classes with context-manager support
  - Loads both HWP and HWPX files via `hwpdocument_new`
  - `render_page_svg(page)` and `render_all_svgs()` produce SVG strings
  - Text width measured via Pillow when available, heuristic fallback otherwise
- `pip install pyhwpxlib[preview]` optional extras for zero-config preview
  (installs `wasmtime>=25.0`)
- `pip install pyhwpxlib[preview-fonts]` adds Pillow for accurate Korean
  font measurement on macOS
- Bundled `rhwp_bg.wasm` (3.2 MB, MIT © Edward Kim) at
  `pyhwpxlib/vendor/rhwp_bg.wasm`
- `tests/test_rhwp_bridge.py` — 27 tests covering HWP / HWPX samples and
  document lifecycle

### Changed
- `_find_wasm()` resolution order now prefers the bundled package resource.
  Order: `RHWP_WASM_PATH` env → bundled → VS Code extension → error
- `RhwpWasmNotFoundError` message now suggests `pip install pyhwpxlib[preview]`
- Package description updated to mention preview support

### Notice
- This release bundles a third-party WebAssembly binary from the
  [rhwp project](https://github.com/edwardkim/rhwp). See `NOTICE.md` and
  `pyhwpxlib/vendor/LICENSE.rhwp.txt` for full attribution and license.

## [0.1.1] - earlier

- Fix project URLs in pyproject.toml metadata.

## [0.1.0] - earlier

- Initial release.
