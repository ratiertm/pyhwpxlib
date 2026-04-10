---
template: plan
version: 1.2
feature: pypi-preview-bundle
---

# pypi-preview-bundle Planning Document

> **Summary**: rhwp WASM 기반 HWP/HWPX→SVG 미리보기 기능을 번들하여 PyPI 배포
>
> **Project**: pyhwpxlib
> **Version**: 0.1.1 → 0.2.0 (MINOR bump — 신규 `preview` extras 추가)
> **Author**: ratiertm
> **Date**: 2026-04-11
> **Status**: Draft

---

## 1. Overview

### 1.1 Purpose

`pyhwpxlib.rhwp_bridge` 모듈이 의존하는 `rhwp_bg.wasm` 바이너리를 패키지에 번들하여, 사용자가 `pip install pyhwpxlib[preview]` 한 줄로 HWP/HWPX→SVG 미리보기를 즉시 사용할 수 있게 한다.

### 1.2 Background

- 이미 구현된 `pyhwpxlib/rhwp_bridge.py` (273줄) + 27개 pytest 전부 통과
- 현재는 WASM 경로를 `RHWP_WASM_PATH` env 또는 VS Code extension 경로로 해결 → PyPI 사용자에게는 동작 불가
- 경쟁 포인트: 국내 HWP 파이썬 생태계에서 "설치 즉시 SVG 미리보기 가능"한 라이브러리는 전무
- LLM-in-the-loop 검토 워크플로를 위한 핵심 기능 (생성한 HWPX를 LLM이 시각적으로 확인)

### 1.3 Related Documents

- rhwp 프로젝트: https://github.com/edwardkim/rhwp (MIT License, © Edward Kim)
- 기존 구현: `pyhwpxlib/rhwp_bridge.py`
- 기존 테스트: `tests/test_rhwp_bridge.py` (27 tests)

---

## 2. Scope

### 2.1 In Scope

- [ ] `rhwp_bg.wasm` (3.2MB)를 `pyhwpxlib/vendor/`에 포함
- [ ] rhwp의 MIT `LICENSE.txt` 원문을 `pyhwpxlib/vendor/LICENSE.rhwp.txt`에 복사
- [ ] `NOTICE.md` 생성 (rhwp 출처 및 라이선스 고지)
- [ ] `_find_wasm()` 우선순위 재정렬: env → 번들 → VS Code extension (fallback)
- [ ] `pyproject.toml`에 `preview` / `preview-fonts` optional-dependencies 추가
- [ ] `package-data`에 `vendor/*.wasm`, `vendor/LICENSE*`, `vendor/NOTICE*` 추가
- [ ] `MANIFEST.in` 생성 (sdist에도 vendor 포함 확인)
- [ ] 로컬에서 `python -m build` 성공
- [ ] 생성된 wheel / sdist에 WASM 파일 포함 검증
- [ ] 깨끗한 venv에서 `pip install dist/*.whl[preview]` 후 `RhwpEngine()` 동작 확인
- [ ] `README.md`에 번들 고지 + 사용 예시 한 섹션 추가
- [ ] `README_KO.md`에 동일 내용 한국어 추가
- [ ] CHANGELOG 추가 (또는 release notes)
- [ ] 버전 0.1.1 → 0.2.0 bump

### 2.2 Out of Scope

- PyPI 실제 업로드 (사용자가 직접 `twine upload` 실행)
- `hwp2hwpx.py`의 hanging indent 버그 수정 (별도 PDCA 사이클)
- API 확장 (`render_page_html`, `render_page_canvas` 등 다른 rhwp 기능 노출)
- WASM 바이너리 자동 업데이트 메커니즘
- Windows / Linux 고유 폰트 매핑 추가 (현재는 macOS만)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-01 | `pip install pyhwpxlib[preview]`로 preview 기능 설치 가능 | High | Pending |
| FR-02 | 설치 후 `RhwpEngine()` 호출 시 번들된 WASM 자동 탐지 | High | Pending |
| FR-03 | rhwp MIT 라이선스 원문이 wheel/sdist에 포함 | High | Pending |
| FR-04 | 기존 27개 rhwp_bridge 테스트가 번들 기반으로도 전부 통과 | High | Pending |
| FR-05 | `RHWP_WASM_PATH` env var는 번들보다 우선 (override 가능) | Medium | Pending |
| FR-06 | VS Code extension 경로는 번들이 없을 때만 fallback | Low | Pending |
| FR-07 | README에 번들 고지 + 사용 예시 포함 | Medium | Pending |

### 3.2 Non-Functional Requirements

| Category | Criteria | Measurement Method |
|----------|----------|-------------------|
| Package Size | wheel 총 크기 ≤ 6MB | `ls -lh dist/*.whl` |
| Install Time | 깨끗한 venv 기준 ≤ 10초 (wasmtime 다운로드 제외) | `time pip install ...` |
| License | rhwp MIT 준수 — 원문 라이선스 텍스트 재배포 포함 | `unzip -l` 로 LICENSE 존재 확인 |
| Backwards Compat | 기존 27개 `tests/test_rhwp_bridge.py` 모두 pass | `pytest` |
| Platform | `py3-none-any` 단일 wheel (wasmtime이 플랫폼 분기 담당) | `twine check` |

---

## 4. Success Criteria

### 4.1 Definition of Done

- [ ] `python -m build` 성공 (sdist + wheel)
- [ ] `twine check dist/*` 통과
- [ ] wheel에 `pyhwpxlib/vendor/rhwp_bg.wasm` 포함 확인
- [ ] sdist에 동일 파일 포함 확인
- [ ] 깨끗한 venv (`uv venv _verify`)에서 `pip install dist/*.whl[preview]` 성공
- [ ] 그 venv에서 `from pyhwpxlib.rhwp_bridge import RhwpEngine; RhwpEngine()` 에러 없이 동작
- [ ] 27개 `test_rhwp_bridge.py` 테스트 전부 pass (번들 경로 사용)
- [ ] `README.md` 업데이트 반영

### 4.2 Quality Criteria

- [ ] Import 에러 없음 (`wasmtime` 미설치 시 `rhwp_bridge` import가 명확한 에러 메시지)
- [ ] `RhwpWasmNotFoundError` 메시지에 설치 방법(`pip install pyhwpxlib[preview]`) 안내
- [ ] wheel 크기 baseline 대비 증가 ≤ 3.5MB

---

## 5. Risks and Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| rhwp 라이선스 재배포 위반 | High | Low | 원본 LICENSE.txt를 `vendor/LICENSE.rhwp.txt`로 복사 + `NOTICE.md`에 출처 명시 |
| wheel 크기 > PyPI 파일 제한 | High | Very Low | 3.2MB는 PyPI 파일당 100MB 제한 대비 무시 가능 |
| `wasmtime` 버전 호환성 | Medium | Medium | `wasmtime>=25.0` 최소 버전 고정, 테스트로 검증 |
| 번들 경로 탐색 실패 (설치 방식 차이) | Medium | Low | `importlib.resources` 사용해 경로 독립적으로 해결 |
| 기존 개발 환경 (VS Code extension 경로)에서 regression | Low | Low | fallback 순서 유지 — env → bundled → vscode-ext |
| rhwp 업스트림 변경 시 WASM 재번들 필요 | Low | Medium | 버전 고정 + 업그레이드 절차를 CHANGELOG에 기록 |
| macOS 외 시스템에서 폰트 폴백 실패 | Medium | High | 현재 Scope 밖 — 휴리스틱 폴백 동작 보장으로 에러 방지 |

---

## 6. Technical Approach

### 6.1 파일 배치

```
pyhwpxlib/
├── rhwp_bridge.py        # 기존 (수정: _find_wasm)
├── vendor/               # 신규
│   ├── __init__.py       # 빈 파일 (package 인식용)
│   ├── rhwp_bg.wasm      # 3.2MB
│   ├── LICENSE.rhwp.txt  # rhwp 원본 MIT 라이선스
│   └── NOTICE.md         # 번들 고지
└── ...
```

### 6.2 `_find_wasm()` 로직 변경

```python
def _find_wasm() -> Path:
    # 1. 환경변수 (override)
    if env := os.environ.get("RHWP_WASM_PATH"):
        p = Path(env).expanduser()
        if p.is_file():
            return p
        raise RhwpWasmNotFoundError(f"RHWP_WASM_PATH does not point to a file: {p}")

    # 2. 번들된 WASM (기본)
    try:
        from importlib.resources import files
        bundled = files("pyhwpxlib.vendor").joinpath("rhwp_bg.wasm")
        if bundled.is_file():
            return Path(str(bundled))
    except (ImportError, FileNotFoundError, AttributeError):
        pass

    # 3. 개발 환경 fallback — VS Code extension
    ext_root = Path.home() / ".vscode/extensions"
    if ext_root.is_dir():
        candidates = sorted(ext_root.glob("edwardkim.rhwp-vscode-*/dist/media/rhwp_bg.wasm"))
        if candidates:
            return candidates[-1]

    raise RhwpWasmNotFoundError(
        "rhwp WASM binary not found. Install with: pip install pyhwpxlib[preview]"
    )
```

### 6.3 `pyproject.toml` 변경

```toml
[project]
version = "0.2.0"  # 0.1.1 → 0.2.0

[project.optional-dependencies]
preview = ["wasmtime>=25.0"]
preview-fonts = ["wasmtime>=25.0", "Pillow>=9.0"]
images = ["Pillow>=9.0"]
lxml = ["lxml>=4.9"]
hwp = ["olefile>=0.46"]
all = [
    "Pillow>=9.0",
    "lxml>=4.9",
    "olefile>=0.46",
    "wasmtime>=25.0",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["pyhwpxlib*"]

[tool.setuptools.package-data]
pyhwpxlib = [
    "tools/*.hwpx",
    "tools/*.xml",
    "vendor/*.wasm",
    "vendor/LICENSE*",
    "vendor/NOTICE*",
]
```

### 6.4 `MANIFEST.in`

```
recursive-include pyhwpxlib/vendor *
include NOTICE.md
```

### 6.5 라이선스 고지 (NOTICE.md, 번들 파일)

```markdown
# pyhwpxlib — Third-Party Components

## rhwp (WebAssembly binary)

Path: `pyhwpxlib/vendor/rhwp_bg.wasm`
Source: https://github.com/edwardkim/rhwp
License: MIT License
Copyright: © 2025-2026 Edward Kim

Full license text: `pyhwpxlib/vendor/LICENSE.rhwp.txt`

pyhwpxlib bundles a pre-built WebAssembly binary from the rhwp project
to provide HWP/HWPX → SVG rendering in the `pyhwpxlib.rhwp_bridge` module.
No modifications are made to the binary.
```

---

## 7. Implementation Order

1. **파일 준비** (5분)
   - `pyhwpxlib/vendor/` 디렉토리 생성 + `__init__.py`
   - `rhwp_bg.wasm` 복사 (VS Code extension → vendor)
   - rhwp GitHub LICENSE.txt 다운로드 → `vendor/LICENSE.rhwp.txt`
   - `vendor/NOTICE.md` 작성

2. **코드 수정** (10분)
   - `rhwp_bridge.py`의 `_find_wasm()` 재작성 (importlib.resources 우선)
   - 에러 메시지 업데이트

3. **패키징 메타데이터** (10분)
   - `pyproject.toml`: version 0.2.0, preview extras, package-data
   - `MANIFEST.in` 생성
   - 프로젝트 루트에 `NOTICE.md` 생성 (README 참조용 축약본)

4. **빌드 검증** (10분)
   - `uv pip install --python .venv/bin/python build twine`
   - `python -m build`
   - `twine check dist/*`
   - `unzip -l dist/*.whl | grep -E "(wasm|LICENSE)"` 확인
   - `tar -tzf dist/*.tar.gz | grep -E "(wasm|LICENSE)"` 확인

5. **격리 환경 테스트** (10분)
   - `uv venv _verify`
   - `_verify/bin/pip install dist/*.whl[preview]`
   - smoke test: `RhwpEngine()` + `load("hwp_samples/*.hwp")` + `render_page_svg(0)`

6. **회귀 테스트** (5분)
   - 기존 venv (`.venv`)에서 `pytest tests/test_rhwp_bridge.py -q`
   - 모든 27개 pass 확인

7. **문서화** (15분)
   - `README.md`: "Preview (HWP/HWPX → SVG)" 섹션 + 번들 고지
   - `README_KO.md`: 동일 한국어 섹션
   - CHANGELOG 또는 release notes

---

## 8. Next Steps (after Plan)

1. [ ] `/pdca design pypi-preview-bundle` — Design 문서 작성 (코드 구조 세부)
2. [ ] `/pdca do pypi-preview-bundle` — 구현 시작
3. [ ] `/pdca analyze pypi-preview-bundle` — 구현 후 gap 분석
4. [ ] `/pdca report pypi-preview-bundle` — 완료 보고서

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-04-11 | Initial draft | ratiertm |
