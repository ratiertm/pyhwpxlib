---
template: analysis
feature: pypi-preview-bundle
phase: check
date: 2026-04-11
analyzer: bkit:gap-detector (via /pdca analyze)
---

# pypi-preview-bundle Gap Analysis

> **Verdict**: **PASS** (Match Rate **98%**, ≥ 90% threshold)
> **Design Doc**: [`pypi-preview-bundle.design.md`](../02-design/features/pypi-preview-bundle.design.md)
> **Plan Doc**: [`pypi-preview-bundle.plan.md`](../01-plan/features/pypi-preview-bundle.plan.md)
> **Analysis Date**: 2026-04-11

---

## 1. Summary

`pypi-preview-bundle` 구현은 Design 문서와 거의 완벽히 일치합니다. 7개 기능 요구사항(FR-01 ~ FR-07)이 전부 충족되었고, `pyhwpxlib/vendor/` 파일 배치, `_find_wasm()` 3단계 우선순위 로직, `pyproject.toml` extras + package-data, `MANIFEST.in`, `NOTICE.md`(루트+vendor), `CHANGELOG.md` 0.2.0 엔트리, README 두 언어 버전 전부 스펙대로 작성되어 있습니다.

빌드 산출물 `dist/pyhwpxlib-0.2.0-py3-none-any.whl` (1.55MB)과 `pyhwpxlib-0.2.0.tar.gz` 모두 존재하고 `twine check` 통과, 기존 27개 테스트는 dev venv와 격리 venv 양쪽에서 모두 PASS. **Critical/Major gap 없음**, Minor gap 3개 중 1개(stale docstring)는 즉시 수정 완료.

**다음 단계 권장**: `/pdca report pypi-preview-bundle` — Match Rate 98%로 Act(iterate) 단계 불필요.

---

## 2. Overall Scores

| Category | Score | Status |
|----------|:-----:|:------:|
| Functional Requirements (FR-01 ~ FR-07) | 100% | ✅ PASS |
| Design Spec Match (§2.1, §3.x) | 100% | ✅ PASS |
| Definition of Done | 100% | ✅ PASS |
| Quality Criteria | 95% | ✅ PASS |
| Convention Compliance | 100% (after docstring fix) | ✅ PASS |
| **Overall** | **98%** | **✅ PASS** |

---

## 3. Functional Requirements Coverage

| ID | Requirement | Status | Evidence |
|----|-------------|:------:|----------|
| FR-01 | `pip install pyhwpxlib[preview]` 설치 가능 | ✅ MATCHED | `pyproject.toml:32` — `preview = ["wasmtime>=25.0"]` |
| FR-02 | 설치 후 번들 WASM 자동 탐지 | ✅ MATCHED | `rhwp_bridge.py:92-99` — `importlib.resources.files("pyhwpxlib.vendor") / "rhwp_bg.wasm"` + `as_file()` |
| FR-03 | rhwp MIT 라이선스 원문 wheel/sdist 포함 | ✅ MATCHED | `vendor/LICENSE.rhwp.txt`; `pyproject.toml:57` package-data; `MANIFEST.in:10` sdist |
| FR-04 | 기존 27개 테스트 전부 pass | ✅ MATCHED | 27/27 passed (dev venv + 격리 venv 양쪽) |
| FR-05 | `RHWP_WASM_PATH` env가 번들보다 우선 | ✅ MATCHED | `rhwp_bridge.py:82-90` — Step 1 env 체크 (설정됐는데 파일 아니면 loud failure) |
| FR-06 | VS Code extension은 fallback | ✅ MATCHED | `rhwp_bridge.py:102-108` — Step 3 (env, 번들 실패 후) |
| FR-07 | README 번들 고지 + 사용 예시 | ✅ MATCHED | `README.md:274-306` (English), `README_KO.md:289-322` (한국어) |

**결과**: 7/7 fully matched.

---

## 4. Definition of Done (Design §4.1)

| Item | Status | Evidence |
|------|:------:|----------|
| `python -m build` 성공 | ✅ | `dist/pyhwpxlib-0.2.0-py3-none-any.whl` + `.tar.gz` 생성 |
| `twine check dist/*` PASSED | ✅ | 두 아티팩트 모두 PASSED |
| wheel에 `vendor/rhwp_bg.wasm` 포함 | ✅ | `unzip -l dist/*.whl \| grep wasm` 확인 |
| sdist에 동일 파일 포함 | ✅ | `tar -tzf dist/*.tar.gz \| grep wasm` 확인 |
| 격리 venv install 성공 | ✅ | `uv venv /tmp/pyhwpxlib_verify` + `pip install dist/*.whl[preview]` |
| 격리 venv에서 `RhwpEngine()` 동작 | ✅ | `/private/tmp/pyhwpxlib_verify/.../vendor/rhwp_bg.wasm` 로드 확인 |
| 27개 `test_rhwp_bridge.py` pass | ✅ | dev: 27/27, 격리: 27/27 |
| `README.md` 업데이트 | ✅ | Preview 섹션 + Credits 테이블 업데이트 |
| `README_KO.md` 업데이트 | ✅ | 미리보기 섹션 한국어 추가 |

---

## 5. Quality Criteria (Plan §4.2)

| Criterion | Target | Actual | Status |
|-----------|--------|--------|:------:|
| Wheel 크기 증가 | ≤ 3.5MB | ~1.3MB (0.15MB → 1.55MB) | ✅ |
| Install time (wasmtime 제외) | ≤ 10초 | ~수 초 | ✅ |
| License 재배포 준수 | rhwp MIT 원문 포함 | `vendor/LICENSE.rhwp.txt` + `NOTICE.md` (2곳) | ✅ |
| Backwards compat | 27/27 pass | 27/27 | ✅ |
| Platform | `py3-none-any` 단일 wheel | `pyhwpxlib-0.2.0-py3-none-any.whl` | ✅ |

---

## 6. Design Spec Compliance (구체 매핑)

### 6.1 §2.1 File Layout

| Expected Path | Present? | Notes |
|---|:---:|---|
| `pyhwpxlib/vendor/__init__.py` | ✅ | 빈 파일에 가까운 docstring |
| `pyhwpxlib/vendor/rhwp_bg.wasm` | ✅ | 3.2MB |
| `pyhwpxlib/vendor/LICENSE.rhwp.txt` | ✅ | rhwp MIT 원문 |
| `pyhwpxlib/vendor/NOTICE.md` | ✅ | §3.3 내용과 일치 |
| `pyproject.toml` (MOD) | ✅ | version, extras, package-data |
| `MANIFEST.in` (NEW) | ✅ | §3.7과 일치 |
| `NOTICE.md` (루트) | ✅ | §3.5과 일치 |
| `README.md` / `README_KO.md` (MOD) | ✅ | Preview 섹션 추가 |
| `CHANGELOG.md` (NEW) | ✅ | 0.2.0 엔트리, §3.9보다 상세 |

### 6.2 §3.1 `_find_wasm()` Implementation

`rhwp_bridge.py:71-113`의 구현이 Design 스펙과 **완전 일치**:
- Step 1 env var + loud failure on invalid path (lines 82-90)
- Step 2 `importlib.resources.files(...) / "rhwp_bg.wasm"` via `as_file()` (lines 92-99)
- Step 3 VS Code extension glob fallback (lines 102-108)
- Step 4 `RhwpWasmNotFoundError` with install hint (lines 110-114)
- Python 3.8 backport handling via `importlib_resources` (lines 43-50)
- `(ModuleNotFoundError, FileNotFoundError)` 예외 캐치 (line 99)

### 6.3 기타 Design 섹션

- **§3.6 pyproject.toml diff**: 모든 항목 적용 (version, extras, package-data)
- **§3.7 MANIFEST.in**: 스펙보다 richer (LICENSE, CHANGELOG, README 추가 포함)
- **§3.8 README 섹션**: 영문/한국어 모두 Preview 섹션 + 서드파티 고지 포함
- **§3.9 CHANGELOG**: 0.2.0 엔트리 + `### Changed` 섹션 (스펙보다 상세)

---

## 7. Gaps Found

### Critical
**없음**.

### Major
**없음**.

### Minor

| # | Gap | Location | Severity | Status |
|---|-----|----------|:--------:|:------:|
| 1 | 모듈 docstring이 pre-bundle 3단계 해석 순서를 설명 (번들 단계 누락) | `rhwp_bridge.py:19-23` | Minor | **✅ FIXED** (inline) |
| 2 | `scripts/verify_build.sh`(Design §4.2) 미작성 | project root | Minor (optional) | Deferred — shell one-liner로 대체 수행 |
| 3 | wheel 크기 baseline 수치 비교 미기록 | N/A | Minor | **✅ VERIFIED** (1.55MB, 증가 ~1.3MB, ≤ 3.5MB) |

---

## 8. Verdict

**✅ PASS — Match Rate 98% (≥ 90% threshold)**

Critical/Major gap 없음. Minor gap 3개 중 2개는 해결/검증 완료, 1개는 optional로 Deferred. iterate(Act) 단계 **불필요**.

**다음 액션**: `/pdca report pypi-preview-bundle` → 완료 보고서 작성 후 archive.

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-04-11 | Initial gap analysis (bkit:gap-detector) | claude |
| 1.1 | 2026-04-11 | Minor gap #1 fixed inline; wheel size verified | claude |
