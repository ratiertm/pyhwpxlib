---
template: design
version: 1.2
feature: pypi-preview-bundle
---

# pypi-preview-bundle Design Document

> **Summary**: rhwp WASM 번들 + PyPI 배포를 위한 패키징 설계
>
> **Project**: pyhwpxlib
> **Version**: 0.2.0 (target)
> **Author**: ratiertm
> **Date**: 2026-04-11
> **Status**: Draft
> **Planning Doc**: [pypi-preview-bundle.plan.md](../../01-plan/features/pypi-preview-bundle.plan.md)

---

## 1. Overview

### 1.1 Design Goals

- **Zero-config 설치**: PyPI 사용자가 `pip install pyhwpxlib[preview]` 한 줄 이후 추가 설정 없이 `RhwpEngine()` 동작
- **설치 방식 독립**: wheel/sdist/editable install 어디서든 WASM 경로 해결
- **라이선스 법적 준수**: rhwp MIT License 원문과 NOTICE 재배포 의무 이행
- **기존 호환성**: 개발 환경(VS Code extension) 경로도 fallback으로 유지하여 기존 27개 테스트 무결성 보장
- **최소 침투**: `rhwp_bridge.py`의 공개 API 변경 없음 (`_find_wasm()` 내부만 변경)

### 1.2 Design Principles

- **Single Source of Resolution**: WASM 경로 결정 로직을 `_find_wasm()` 한 곳에만 유지
- **Fail Fast with Clear Guidance**: `RhwpWasmNotFoundError` 발생 시 `pip install pyhwpxlib[preview]` 명령을 메시지에 포함
- **Package Resource over Hardcoded Path**: `importlib.resources`로 패키지 내부 파일 접근 → 설치 방식 독립
- **Opt-in Heavy Dependency**: `wasmtime`은 `[preview]` extras에만, 기본 설치에는 포함 안 함

---

## 2. Architecture

### 2.1 파일 배치 (변경 후)

```
pyhwpxlib/                          (Python package root)
├── __init__.py
├── api.py
├── rhwp_bridge.py                  [MOD] _find_wasm() 재작성
├── hwp2hwpx.py
├── ... (기존 파일들)
├── tools/
│   ├── *.hwpx
│   └── *.xml
└── vendor/                         [NEW]
    ├── __init__.py                 [NEW] 빈 파일 (importable subpackage)
    ├── rhwp_bg.wasm                [NEW] 3.2MB, MIT © Edward Kim
    ├── LICENSE.rhwp.txt            [NEW] rhwp 원본 LICENSE 전문
    └── NOTICE.md                   [NEW] 번들 고지 내용

(project root)
├── pyproject.toml                  [MOD] version, extras, package-data
├── MANIFEST.in                     [NEW] sdist 보조
├── NOTICE.md                       [NEW] 루트 고지 파일 (README 참조용)
├── README.md                       [MOD] Preview 섹션 추가
├── README_KO.md                    [MOD] Preview 섹션 한국어 추가
└── CHANGELOG.md                    [NEW or MOD] 0.2.0 릴리스 노트
```

### 2.2 WASM 탐색 흐름 (Data Flow)

```
RhwpEngine.__init__()
   │
   ▼
_find_wasm()
   │
   ├─ Step 1: RHWP_WASM_PATH env var
   │             │
   │             ├─ exists & is file? ──► return
   │             └─ set but invalid?  ──► raise (loud failure)
   │
   ├─ Step 2: Bundled resource
   │             │
   │             ├─ importlib.resources.files("pyhwpxlib.vendor") /
   │             │  "rhwp_bg.wasm"
   │             │             │
   │             │             ├─ exists? ──► return
   │             │             └─ missing? ──► fallthrough
   │
   ├─ Step 3: VS Code extension (dev fallback)
   │             │
   │             ├─ ~/.vscode/extensions/edwardkim.rhwp-vscode-*/
   │             │  dist/media/rhwp_bg.wasm
   │             │             │
   │             │             ├─ exists? ──► return
   │             │             └─ missing? ──► fallthrough
   │
   └─ raise RhwpWasmNotFoundError(
         "rhwp WASM binary not found. "
         "Install with: pip install pyhwpxlib[preview]"
      )
```

### 2.3 Dependencies

| Component | Depends On | Purpose |
|-----------|-----------|---------|
| `pyhwpxlib.rhwp_bridge` | `wasmtime` (optional) | WASM runtime |
| `pyhwpxlib.rhwp_bridge` | `pyhwpxlib.vendor.rhwp_bg.wasm` (bundled) | Default binary |
| `pyhwpxlib.rhwp_bridge._TextMeasurer` | `PIL.ImageFont` (optional) | Accurate text measurement |
| `pyhwpxlib.vendor` | — | Pure resource subpackage (no code) |

---

## 3. Detailed Design

### 3.1 `_find_wasm()` 구현 상세

```python
import os
import sys
from pathlib import Path
from typing import Optional

# importlib.resources: 3.9부터 files() 사용 가능
if sys.version_info >= (3, 9):
    from importlib.resources import files as _resource_files
else:  # 3.8 호환 (backport)
    try:
        from importlib_resources import files as _resource_files  # type: ignore
    except ImportError:
        _resource_files = None  # type: ignore


def _find_wasm() -> Path:
    """Resolve the rhwp WASM binary path.

    Resolution order:
    1. RHWP_WASM_PATH environment variable (explicit override)
    2. Bundled package resource (pyhwpxlib/vendor/rhwp_bg.wasm)
    3. VS Code extension installation (development fallback)
    4. Raise RhwpWasmNotFoundError with install hint
    """
    # Step 1: explicit env var
    env = os.environ.get("RHWP_WASM_PATH")
    if env:
        p = Path(env).expanduser()
        if p.is_file():
            return p
        raise RhwpWasmNotFoundError(
            f"RHWP_WASM_PATH is set but not a file: {p}"
        )

    # Step 2: bundled resource (the normal case for PyPI installs)
    if _resource_files is not None:
        try:
            resource = _resource_files("pyhwpxlib.vendor") / "rhwp_bg.wasm"
            # importlib.resources returns a Traversable; use as_file for zip safety
            from importlib.resources import as_file
            with as_file(resource) as real_path:
                if real_path.is_file():
                    return Path(real_path)
        except (ModuleNotFoundError, FileNotFoundError):
            pass

    # Step 3: VS Code extension fallback (development)
    ext_root = Path.home() / ".vscode/extensions"
    if ext_root.is_dir():
        candidates = sorted(
            ext_root.glob("edwardkim.rhwp-vscode-*/dist/media/rhwp_bg.wasm")
        )
        if candidates:
            return candidates[-1]

    # Step 4: nothing found
    raise RhwpWasmNotFoundError(
        "rhwp WASM binary not found. "
        "Install with: pip install pyhwpxlib[preview]\n"
        "Or set RHWP_WASM_PATH to a valid rhwp_bg.wasm file."
    )
```

**Notes**:
- `importlib.resources.files()` + `as_file()` 조합은 zipfile-installed 패키지에서도 안전하게 실경로 획득
- Python 3.8 호환성: `importlib_resources` backport 우선, 없으면 Step 2 skip (fallback 가능)
- `ModuleNotFoundError` 캐치: `pyhwpxlib.vendor` subpackage가 개발 중 없을 수 있음

### 3.2 `pyhwpxlib/vendor/__init__.py`

빈 파일 (크기 0). 목적은 `pyhwpxlib.vendor`를 importable subpackage로 인식시키는 것.

```python
"""Vendored third-party binaries and license notices.

This subpackage contains only data files; it has no Python code.
See NOTICE.md for attribution and license information.
"""
```

### 3.3 `pyhwpxlib/vendor/NOTICE.md` (번들 내부 고지)

```markdown
# pyhwpxlib - Bundled Third-Party Components

## rhwp (WebAssembly binary)

- **File**: `rhwp_bg.wasm`
- **Source**: https://github.com/edwardkim/rhwp
- **License**: MIT License
- **Copyright**: (c) 2025-2026 Edward Kim
- **Version**: 0.6.0 (matching edwardkim.rhwp-vscode 0.6.0)

Full license text: `LICENSE.rhwp.txt` (in this directory)

pyhwpxlib bundles a pre-built WebAssembly binary from the rhwp project
to provide HWP/HWPX to SVG rendering in the `pyhwpxlib.rhwp_bridge` module.
The binary is redistributed unmodified.
```

### 3.4 `pyhwpxlib/vendor/LICENSE.rhwp.txt`

rhwp 원본 LICENSE.txt 전문 복사 (MIT License).
출처: `~/.vscode/extensions/edwardkim.rhwp-vscode-0.6.0/LICENSE.txt`

### 3.5 루트 `NOTICE.md` (요약본)

프로젝트 루트의 고지 파일. 사용자가 GitHub 리포에서 바로 확인 가능.

```markdown
# NOTICE

This project includes third-party components. See the licenses below.

## Bundled Binaries

### rhwp (WebAssembly)

- Location: `pyhwpxlib/vendor/rhwp_bg.wasm`
- Source: https://github.com/edwardkim/rhwp
- License: MIT License
- Copyright: (c) 2025-2026 Edward Kim
- Full license: `pyhwpxlib/vendor/LICENSE.rhwp.txt`
```

### 3.6 `pyproject.toml` 변경 diff

```diff
 [project]
 name = "pyhwpxlib"
-version = "0.1.1"
+version = "0.2.0"
 description = "Python library for creating and editing HWPX (Hancom Office) documents without Hancom Office"
 readme = "README.md"
 license = "BUSL-1.1 AND Apache-2.0"
 requires-python = ">=3.8"
 keywords = ["hwpx", "hwp", "hancom", "korean", "document", "llm"]
 classifiers = [
     ...
 ]
 dependencies = []

 [project.optional-dependencies]
+preview = ["wasmtime>=25.0"]
+preview-fonts = ["wasmtime>=25.0", "Pillow>=9.0"]
 images = ["Pillow>=9.0"]
 lxml = ["lxml>=4.9"]
 hwp = ["olefile>=0.46"]
-all = ["Pillow>=9.0", "lxml>=4.9", "olefile>=0.46"]
+all = [
+    "Pillow>=9.0",
+    "lxml>=4.9",
+    "olefile>=0.46",
+    "wasmtime>=25.0",
+]

 [tool.setuptools.packages.find]
 where = ["."]
 include = ["pyhwpxlib*"]

 [tool.setuptools.package-data]
 pyhwpxlib = [
     "tools/*.hwpx",
     "tools/*.xml",
+    "vendor/*.wasm",
+    "vendor/LICENSE*",
+    "vendor/NOTICE*",
 ]
```

### 3.7 `MANIFEST.in`

```
# Include root-level legal and changelog files
include LICENSE
include NOTICE.md
include CHANGELOG.md
include README.md
include README_KO.md

# Include bundled vendor files in sdist
recursive-include pyhwpxlib/vendor *

# Exclude caches and build artifacts
global-exclude __pycache__
global-exclude *.py[cod]
global-exclude .DS_Store
```

### 3.8 README 추가 섹션 (스펙)

`README.md`와 `README_KO.md`에 각각 한 섹션 추가:

**English section (README.md)**:
```markdown
## Preview (HWP/HWPX → SVG)

Render HWP or HWPX documents to SVG for visual inspection or LLM review:

    pip install pyhwpxlib[preview]

    from pyhwpxlib.rhwp_bridge import RhwpEngine
    engine = RhwpEngine()
    with engine.load("sample.hwp") as doc:
        print(doc.page_count)
        svg = doc.render_page_svg(0)

For accurate Korean text measurement on macOS, install Pillow as well:

    pip install pyhwpxlib[preview-fonts]

### Third-Party Notice

The preview feature bundles a pre-built WebAssembly binary from the
[rhwp project](https://github.com/edwardkim/rhwp) (MIT License,
© 2025-2026 Edward Kim). See `pyhwpxlib/vendor/NOTICE.md` for details.
```

**한국어 섹션 (README_KO.md)**: 동일 내용 한국어 번역.

### 3.9 CHANGELOG 추가 (0.2.0 항목)

```markdown
## [0.2.0] - 2026-04-11

### Added
- `pyhwpxlib.rhwp_bridge` — HWP/HWPX → SVG renderer via bundled rhwp WASM
- `pip install pyhwpxlib[preview]` optional extras for zero-config preview
- `pip install pyhwpxlib[preview-fonts]` for accurate Korean font measurement
- Bundled `rhwp_bg.wasm` (3.2MB, MIT © Edward Kim) under `pyhwpxlib/vendor/`
- `tests/test_rhwp_bridge.py` — 27 tests for bridge and rendering

### Notice
- This release includes a third-party WebAssembly binary from the rhwp
  project (https://github.com/edwardkim/rhwp). See `NOTICE.md` for full
  attribution and license information.
```

---

## 4. Testing Strategy

### 4.1 기존 테스트 재사용

`tests/test_rhwp_bridge.py`의 27개 테스트는 **그대로** 통과해야 한다. `_find_wasm()`의 탐색 우선순위가 바뀌어도 결국 동일한 WASM 바이너리를 찾아 동일한 결과를 내야 함.

### 4.2 신규 빌드 검증 스크립트

`scripts/verify_build.sh` (또는 shell one-liner):

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Clean build
rm -rf dist build *.egg-info
.venv/bin/python -m build

# 2. twine metadata check
.venv/bin/twine check dist/*

# 3. Verify WASM in wheel
echo "=== wheel contents ==="
unzip -l dist/*.whl | grep -E "(wasm|LICENSE|NOTICE)"

# 4. Verify WASM in sdist
echo "=== sdist contents ==="
tar -tzf dist/*.tar.gz | grep -E "(wasm|LICENSE|NOTICE)"

# 5. Install in clean venv
uv venv /tmp/pyhwpxlib_verify --force
/tmp/pyhwpxlib_verify/bin/pip install dist/*.whl[preview]

# 6. Smoke test
/tmp/pyhwpxlib_verify/bin/python -c "
from pyhwpxlib.rhwp_bridge import RhwpEngine
engine = RhwpEngine()
print(f'WASM resolved: {engine._wasm_path}')
with engine.load('hwp_samples/자기소개서_양식.hwp') as doc:
    svg = doc.render_page_svg(0)
    assert svg.startswith('<svg'), 'Invalid SVG output'
    print(f'Pages: {doc.page_count}, SVG length: {len(svg)}')
print('OK')
"
```

### 4.3 Matrix of install modes

| Install Mode | Expected Result | Test Method |
|--------------|-----------------|-------------|
| `pip install pyhwpxlib` (no extras) | `ImportError` on `from pyhwpxlib.rhwp_bridge import RhwpEngine` | manual |
| `pip install pyhwpxlib[preview]` | Works with bundled WASM | verify_build.sh smoke test |
| `pip install pyhwpxlib[preview-fonts]` | Works + accurate font metrics | manual check |
| `pip install -e .` (editable) | Works (bundled WASM still resolves) | pytest |
| `RHWP_WASM_PATH=/tmp/bad pip install pyhwpxlib[preview]` | `RhwpWasmNotFoundError` at `RhwpEngine()` | manual check |

---

## 5. Rollback Plan

만약 빌드/테스트 실패 시:

1. `pyhwpxlib/vendor/` 디렉토리 삭제
2. `pyproject.toml`의 `version` → 0.1.1 복원
3. `pyproject.toml`의 `preview*` extras 제거
4. `pyproject.toml`의 `package-data`에서 vendor 항목 제거
5. `MANIFEST.in` 삭제
6. `_find_wasm()`을 원래 로직으로 되돌림
7. `git diff` 확인 후 commit 취소

모든 변경이 단일 commit이므로 `git revert` 가능.

---

## 6. Open Questions / Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| preview-fonts를 별도 extras로? | Yes | Pillow는 선택적, 3MB 추가 |
| Python 3.8 지원 유지? | Yes (best-effort) | 기존 classifier 유지, importlib_resources fallback |
| NOTICE.md 루트 vs vendor 둘 다? | Both | 루트는 참조용, vendor는 sdist/wheel 내장 |
| CHANGELOG.md 신규 생성? | Yes | 0.2.0이 첫 정식 CHANGELOG |
| rhwp 버전 고정 표기? | Yes (NOTICE.md에 0.6.0) | 업그레이드 추적 명확화 |
| `all` extras에 `preview` 포함? | Yes | 사용자 편의 |
| `twine upload`까지 자동화? | No (scope out) | 사용자 수동 실행 |

---

## 7. Next Steps (Do Phase)

구현 순서는 Plan 문서 §7과 동일:

1. 파일 준비 → 2. 코드 수정 → 3. 메타데이터 → 4. 빌드 → 5. 격리 테스트 → 6. 회귀 → 7. 문서

**Do 단계 시작**: `/pdca do pypi-preview-bundle`

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-04-11 | Initial design | ratiertm |
