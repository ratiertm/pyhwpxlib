"""HWPX/HWP → SVG/PNG preview rendering.

Uses rhwp_bridge (WASM) for SVG rendering, with optional font embedding
for cross-platform Korean text support.

This module is the canonical entry point for all preview functionality,
including the MCP server's ``hwpx_preview`` tool.

Usage
-----
>>> from pyhwpxlib.preview import render_pages, render_svg
>>> pages = render_pages("doc.hwpx", "/tmp/previews")
>>> svg = render_svg("doc.hwpx", page=0, embed_fonts=True)

IMPORTANT: Always use ``embed_fonts=True`` when the SVG will be
rasterized (e.g., cairosvg → PNG) or viewed on a machine that may
lack Korean fonts. Without it, all Korean text renders as □ (tofu).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def _get_engine():
    """Lazily import and return a shared RhwpEngine instance."""
    from pyhwpxlib.rhwp_bridge import RhwpEngine
    if not hasattr(_get_engine, "_instance"):
        _get_engine._instance = RhwpEngine()
    return _get_engine._instance


def render_svg(
    hwpx_path: str,
    page: int = 0,
    embed_fonts: bool = True,
) -> str:
    """Render a single page to an SVG string.

    Parameters
    ----------
    hwpx_path : str
        Path to HWP or HWPX file.
    page : int
        Zero-based page index.
    embed_fonts : bool
        If True (default), subset and embed Korean fonts into the SVG
        so it renders correctly on any platform. **Set this to True
        whenever the SVG will be converted to PNG or displayed on a
        machine without Korean fonts installed.**
    """
    engine = _get_engine()
    with engine.load(hwpx_path) as doc:
        return doc.render_page_svg(page, embed_fonts=embed_fonts)


def render_pages(
    hwpx_path: str,
    out_dir: str,
    *,
    max_pages: Optional[int] = None,
    embed_fonts: bool = True,
    fmt: str = "svg",
) -> list[dict]:
    """Render all (or some) pages to files.

    Parameters
    ----------
    hwpx_path : str
        Path to HWP or HWPX file.
    out_dir : str
        Directory for output files.
    max_pages : int, optional
        Maximum number of pages to render. None = all.
    embed_fonts : bool
        Embed Korean fonts into SVG. Default True.
    fmt : str
        Output format: ``"svg"`` (default) or ``"png"``.
        PNG requires ``cairosvg`` (``pip install cairosvg``).

    Returns
    -------
    list[dict]
        Each entry: ``{"page": int, "svg": str_path}``
        or ``{"page": int, "svg": str_path, "png": str_path}``
    """
    os.makedirs(out_dir, exist_ok=True)
    engine = _get_engine()
    stem = Path(hwpx_path).stem
    results = []

    with engine.load(hwpx_path) as doc:
        n = doc.page_count
        if max_pages is not None:
            n = min(n, max_pages)

        for i in range(n):
            svg_str = doc.render_page_svg(i, embed_fonts=embed_fonts)
            svg_path = os.path.join(out_dir, f"{stem}_p{i+1:02d}.svg")
            with open(svg_path, "w", encoding="utf-8") as f:
                f.write(svg_str)

            entry = {"page": i, "svg": svg_path}

            if fmt == "png":
                png_path = os.path.join(out_dir, f"{stem}_p{i+1:02d}.png")
                _svg_to_png(svg_str, png_path)
                entry["png"] = png_path

            results.append(entry)

    return results


def _svg_to_png(svg_str: str, png_path: str, width: int = 1200) -> None:
    """Convert SVG string to PNG file.

    Uses cairosvg if available, falls back to macOS qlmanage.
    Note: cairosvg may not render Korean text correctly even with
    embedded fonts. For best results, view SVGs directly in a browser.
    """
    try:
        import cairosvg
        cairosvg.svg2png(
            bytestring=svg_str.encode("utf-8"),
            write_to=png_path,
            output_width=width,
        )
        return
    except ImportError:
        pass

    # macOS fallback: save SVG to temp, use qlmanage
    import subprocess
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False, mode="w") as tmp:
        tmp.write(svg_str)
        tmp_path = tmp.name
    try:
        subprocess.run(
            ["qlmanage", "-t", "-s", str(width), "-o", os.path.dirname(png_path), tmp_path],
            capture_output=True, timeout=15,
        )
        ql_output = tmp_path + ".png"
        if os.path.exists(ql_output):
            os.rename(ql_output, png_path)
    finally:
        os.unlink(tmp_path)
