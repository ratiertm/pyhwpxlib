# CLAUDE.md — pyhwpxlib

## Project overview
Python library for creating, editing, and previewing HWPX/HWP documents without Hancom Office.

## Key modules
- `pyhwpxlib/api.py` — Public API (create, open, save, extract, fill templates, etc.)
- `pyhwpxlib/hwp2hwpx.py` — HWP 5.x binary → HWPX converter
- `pyhwpxlib/rhwp_bridge.py` — HWP/HWPX → SVG renderer via bundled rhwp WASM
- `pyhwpxlib/preview.py` — Preview module (SVG/PNG rendering, used by MCP server)
- `pyhwpxlib/mcp_server/server.py` — MCP server (`hangul-docs`) for LLM integration
- `pyhwpxlib/json_io/` — JSON roundtrip (encoder/decoder/schema)
- `pyhwpxlib/presets.py` — Document presets for common Korean document types

## Critical: Korean font rendering
**ALWAYS use `embed_fonts=True` when rendering SVG for preview.**

Without font embedding, Korean text appears as □□□ (tofu) on machines that
lack Korean fonts (which is most non-Korean systems, CI environments, and
rasterization tools like cairosvg).

```python
# CORRECT — Korean text renders properly everywhere
svg = doc.render_page_svg(0, embed_fonts=True)

# WRONG — Korean text may appear as □□□
svg = doc.render_page_svg(0)
```

The `pyhwpxlib.preview` module defaults to `embed_fonts=True`.

## SVG rendering accuracy
Rendering accuracy hierarchy (verified 2026-04-13):
- **Hancom editor** = ground truth (most accurate)
- **rhwp WASM SVG** = good for preview, but has known differences:
  - HWPX hanging indent not fully interpreted (HWP direct-load is fine)
  - Font metrics differ by OS (Apple SD Gothic Neo on macOS vs Malgun Gothic on Windows)
- **Whale browser viewer** = least accurate

For final verification, always use Hancom editor. Use SVG preview for
quick LLM-in-the-loop review cycles.

## Build & release
```bash
# Build
python -m build

# Check
twine check dist/*

# Upload to PyPI
twine upload dist/*

# Tag
git tag -a vX.Y.Z -m "vX.Y.Z — description"
git push origin vX.Y.Z
gh release create vX.Y.Z --title "..." --notes "..."
```

## Test
```bash
pytest tests/test_rhwp_bridge.py -q   # WASM bridge tests (requires rhwp WASM)
```

## Third-party components
- `pyhwpxlib/vendor/rhwp_bg.wasm` — rhwp WASM binary (MIT © Edward Kim)
  See `NOTICE.md` and `pyhwpxlib/vendor/LICENSE.rhwp.txt`
