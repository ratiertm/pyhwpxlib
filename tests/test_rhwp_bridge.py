"""Tests for pyhwpxlib.rhwp_bridge — HWP/HWPX → SVG via rhwp WASM.

Skipped entirely when the rhwp WASM binary cannot be located.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

try:
    import wasmtime  # noqa: F401
    from pyhwpxlib.rhwp_bridge import (
        RhwpEngine,
        RhwpWasmNotFoundError,
        RhwpError,
    )
    _BRIDGE_AVAILABLE = True
except ImportError:
    _BRIDGE_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _BRIDGE_AVAILABLE, reason="wasmtime not installed"
)


REPO_ROOT = Path(__file__).resolve().parent.parent
HWP_SAMPLES = sorted((REPO_ROOT / "hwp_samples").glob("*.hwp"))
HWPX_SAMPLES = sorted((REPO_ROOT / "tests/output/hwp2hwpx").glob("*.hwpx"))


@pytest.fixture(scope="module")
def engine():
    try:
        return RhwpEngine()
    except RhwpWasmNotFoundError as e:
        pytest.skip(str(e))


def _assert_valid_svg(svg: str):
    assert svg.startswith("<svg") or "<svg" in svg[:200]
    root = ET.fromstring(svg)
    tag = root.tag.split("}")[-1]
    assert tag == "svg", f"root is not <svg>: {tag}"


class TestEngineBasics:
    def test_engine_loads(self, engine):
        assert engine._wasm_path.is_file()

    def test_load_bytes_rejects_garbage(self, engine):
        with pytest.raises(RhwpError):
            engine.load_bytes(b"not a hwp file")


@pytest.mark.skipif(not HWP_SAMPLES, reason="no hwp_samples found")
class TestHwpDirect:
    @pytest.mark.parametrize("sample", HWP_SAMPLES, ids=lambda p: p.name)
    def test_render_first_page(self, engine, sample):
        with engine.load(sample) as doc:
            assert doc.page_count >= 1
            svg = doc.render_page_svg(0)
            _assert_valid_svg(svg)
            # At least one <text> element for a non-empty doc
            assert "<text" in svg


@pytest.mark.skipif(not HWPX_SAMPLES, reason="no converted HWPX samples found")
class TestHwpxConverted:
    @pytest.mark.parametrize("sample", HWPX_SAMPLES, ids=lambda p: p.name)
    def test_render_first_page(self, engine, sample):
        with engine.load(sample) as doc:
            assert doc.page_count >= 1
            svg = doc.render_page_svg(0)
            _assert_valid_svg(svg)


class TestDocumentLifecycle:
    def test_context_manager_closes(self, engine):
        if not HWP_SAMPLES:
            pytest.skip("no samples")
        doc = engine.load(HWP_SAMPLES[0])
        _ = doc.render_page_svg(0)
        doc.close()
        with pytest.raises(RhwpError):
            doc.render_page_svg(0)

    def test_page_index_out_of_range(self, engine):
        if not HWP_SAMPLES:
            pytest.skip("no samples")
        with engine.load(HWP_SAMPLES[0]) as doc:
            with pytest.raises(IndexError):
                doc.render_page_svg(doc.page_count)

    def test_render_all_svgs_small(self, engine):
        # Pick a small sample for speed
        small = min(
            (p for p in HWPX_SAMPLES if p.stat().st_size < 10_000),
            key=lambda p: p.stat().st_size,
            default=None,
        )
        if small is None:
            pytest.skip("no small hwpx sample")
        with engine.load(small) as doc:
            svgs = doc.render_all_svgs()
            assert len(svgs) == doc.page_count
            for s in svgs:
                _assert_valid_svg(s)
