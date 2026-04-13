# Changelog

All notable changes to pyhwpxlib are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3] - 2026-04-14

### Added
- **`substitute_fonts` parameter** on `render_page_svg()` and
  `render_all_svgs()`. Replaces SVG `font-family` chains with an installed
  Korean system font (Apple SD Gothic Neo on macOS, Malgun Gothic on
  Windows). This is the most reliable way to make Korean render correctly
  in SVG rasterizers like cairosvg.
- `pyhwpxlib.preview.render_svg/render_pages` now default to
  `substitute_fonts=True`, so PNG conversions always show Korean correctly.

### Fixed
- **Korean text rendered as □□□ in PNG output** even with
  `embed_fonts=True`. Root cause: cairosvg cannot load TTC-embedded fonts
  (Apple SD Gothic Neo is a TTC collection). Font substitution sidesteps
  this by referencing installed system fonts by name.
- **`fonttools` moved into `[preview]` extras.** In 0.3.x it was only in
  `[preview-fonts]`, so `pip install pyhwpxlib[preview]` had
  `embed_fonts=True` silently no-op'ing.
- `_embed_fonts_in_svg` now emits a RuntimeWarning when fonttools is
  missing instead of silently returning unmodified SVG.

### Changed
- `[preview]` extras: `wasmtime + fonttools`
- `[preview-fonts]` extras: `wasmtime + fonttools + Pillow` (Pillow adds
  accurate text width measurement; optional)

### Recommended usage
For Korean text in PNG output:
```python
from pyhwpxlib.preview import render_pages
render_pages("doc.hwpx", "/tmp")  # substitute_fonts=True by default
```

For pure browser viewing, `embed_fonts=True` still works.

## [0.3.2] - 2026-04-14

### Added
- `pyhwpxlib.form_pipeline` — label-based form filling with cellAddr navigation
  - `extract_form(path)` — parse all tables and cells
  - `find_cell_by_label(form, label, direction)` — locate cell adjacent to a label
  - `fill_by_labels(template, mappings, output)` — batch-fill via `"label>direction"` syntax
- MCP tool `hwpx_fill_form` and `hwpx_analyze_form` now work (previously broken)

### Fixed
- MCP server imports `templates.form_pipeline` — module didn't exist in the
  package, breaking two tools. Now uses `pyhwpxlib.form_pipeline`.

## [0.3.1] - 2026-04-14

### Added
- `pyhwpxlib/preview.py` — canonical preview module with `embed_fonts=True` default
- `CLAUDE.md` — project conventions, Korean font rendering guide for AI agents

### Fixed
- MCP server: `scripts.preview` import was broken (module didn't exist).
  Now uses `pyhwpxlib.preview` which properly embeds Korean fonts in SVG
- README: added `embed_fonts=True` to all SVG examples with Korean text warning

## [0.3.0] - 2026-04-14

### Added
- `pyhwpxlib.json_io` — JSON roundtrip for HWPX documents (encoder/decoder/schema)
- `pyhwpxlib.mcp_server` — MCP server (`hangul-docs`) for LLM integration
- `pyhwpxlib.presets` — document presets for common Korean document types

### Fixed
- `hwp2hwpx.py`: fwSpace/nbSpace/hyphen 뒤 텍스트가 누락되는 버그 수정

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
