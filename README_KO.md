# pyhwpxlib

파이썬으로 HWPX(한글) 문서를 생성, 변환, 편집하는 라이브러리입니다. 한컴오피스 설치가 필요 없습니다.

[**English**](README.md)

## 이런 상황에 쓰세요

- 서버에서 HWPX 보고서를 자동 생성해야 할 때
- 마크다운이나 HTML을 한글 문서로 변환해야 할 때
- 정부 양식/계약서에 데이터를 자동으로 채워야 할 때
- AI 에이전트(Claude Code, Cursor 등)가 한글 문서를 출력해야 할 때
- 구형 HWP 5.x 파일을 HWPX로 변환해야 할 때
- 여러 HWPX 파일을 하나로 합쳐야 할 때
- HWPX에서 텍스트를 추출해야 할 때

## 설치

```bash
pip install pyhwpxlib
```

이 명령 하나로 Python 라이브러리와 `pyhwpxlib` CLI 명령어가 함께 설치됩니다.

Python 3.10 이상 필요. 핵심 기능은 외부 의존성 없이 동작합니다.

```bash
# 선택: 이미지 처리
pip install pyhwpxlib[images]    # Pillow

# 선택: 빠른 XML 파싱
pip install pyhwpxlib[lxml]      # lxml

# 선택: HWP 5.x → HWPX 변환
pip install pyhwpxlib[hwp]       # olefile

# 전부 설치
pip install pyhwpxlib[all]
```

## 빠른 시작

### 5줄로 문서 만들기

```python
from pyhwpxlib import HwpxBuilder

doc = HwpxBuilder()
doc.add_heading("프로젝트 보고서", level=1)
doc.add_paragraph("2026년 4월 작성")
doc.add_table([
    ["항목", "수량", "금액"],
    ["서버", "3", "9,000,000"],
    ["라이선스", "10", "5,000,000"],
])
doc.add_heading("1. 개요", level=2)
doc.add_paragraph("본 보고서는...")
doc.save("보고서.hwpx")
```

### 터미널에서 마크다운 변환

```bash
pyhwpxlib md2hwpx 보고서.md -o 보고서.hwpx
```

### 정부 양식 자동 채우기

```python
from pyhwpxlib.api import fill_template_checkbox

fill_template_checkbox(
    "근로계약서_양식.hwpx",
    data={
        ">성 명<": ">성 명  홍길동<",
        ">사업체명<": ">사업체명  (주)블루오션<",
    },
    checks=["민간기업"],
    output_path="근로계약서_홍길동.hwpx",
)
```

### AI 에이전트 연동

AI에게 자연어로 문서를 설명하면 pyhwpxlib API를 조합해서 `.hwpx`를 생성합니다:

```
나: "3분기 매출 보고서 만들어줘. 제목, 개요, 월별 매출 표,
     핵심 성과 3개를 글머리표로, 마지막에 요약."

AI → pyhwpxlib 호출 → 보고서.hwpx
```

---

## CLI 명령어 레퍼런스

`pip install pyhwpxlib` 설치 시 `pyhwpxlib` 명령어 9개가 함께 설치됩니다:

### md2hwpx -- 마크다운을 HWPX로 변환

```bash
pyhwpxlib md2hwpx 보고서.md -o 보고서.hwpx
pyhwpxlib md2hwpx 보고서.md -o 보고서.hwpx -s github   # 스타일 프리셋
```

자동 인식: 제목(#), **볼드**, *이탈릭*, 글머리표, 번호 목록, 코드 블록, 표, 수평선

### hwpx2html -- HWPX를 HTML로 변환

```bash
pyhwpxlib hwpx2html 문서.hwpx -o 문서.html
```

이미지가 base64로 포함된 독립 실행형 HTML을 생성합니다.

### text -- HWPX에서 텍스트 추출

```bash
pyhwpxlib text 문서.hwpx                        # 일반 텍스트 (기본)
pyhwpxlib text 문서.hwpx -f markdown             # 마크다운으로
pyhwpxlib text 문서.hwpx -f html                 # HTML로
```

### fill -- 양식 템플릿에 데이터 채우기

```bash
# key=value 쌍으로 입력
pyhwpxlib fill 양식.hwpx -o 결과.hwpx -d 이름=홍길동 나이=30

# JSON 파일에서 입력
pyhwpxlib fill 양식.hwpx -o 결과.hwpx -d data.json
```

### info -- HWPX 파일 정보 확인

```bash
pyhwpxlib info 문서.hwpx
```

파일 크기, 섹션 수, 이미지 목록, 텍스트 글자/줄 수, 텍스트 미리보기를 표시합니다.

### merge -- 여러 HWPX 파일 합치기

```bash
pyhwpxlib merge 1장.hwpx 2장.hwpx 3장.hwpx -o 전체.hwpx
```

문서 사이에 페이지 나누기가 자동 삽입됩니다.

### unpack -- HWPX를 폴더로 풀기

```bash
pyhwpxlib unpack 문서.hwpx -o unpacked/
```

HWPX ZIP 안의 XML과 바이너리 파일을 폴더로 추출합니다.

### pack -- 폴더를 HWPX로 묶기

```bash
pyhwpxlib pack unpacked/ -o output.hwpx
```

풀었던 폴더를 다시 HWPX 파일로 패키징합니다. `mimetype` 항목은 OWPML 스펙에 따라 비압축 저장됩니다.

### validate -- HWPX 구조 검증

```bash
pyhwpxlib validate output.hwpx
```

필수 파일(`mimetype`, `header.xml`, `section0.xml`, `content.hpf`) 존재 여부와 XML 파싱을 검사합니다. 성공 시 종료 코드 0, 실패 시 1.

---

## Python API

### 문서 생성 (HwpxBuilder)

HWPX 문서를 생성하는 고수준 빌더입니다. 표 스타일 프리셋(`corporate`, `government`, `academic`, `default`)을 지원합니다.

```python
doc = HwpxBuilder(table_preset='corporate')
```

| 메서드 | 설명 |
|--------|------|
| `add_heading(text, level)` | 제목 (1~4단계) |
| `add_paragraph(text, bold, italic, font_size, text_color, alignment)` | 스타일 단락 |
| `add_table(data, header_bg, col_widths, merge_info, cell_colors, ...)` | 표 (프리셋 자동 적용) |
| `add_bullet_list(items, bullet_char)` | 글머리 기호 목록 (`-`, `•`, `◦`) |
| `add_numbered_list(items, format_string)` | 번호 목록 (`^1.`, `^1)`, `(^1)`) |
| `add_nested_bullet_list(items)` | 다단계 글머리 기호 (레벨 0~6) |
| `add_nested_numbered_list(items)` | 다단계 번호 목록 |
| `add_image(path, width, height)` | 로컬 이미지 삽입 |
| `add_image_from_url(url, width, height)` | URL 이미지 삽입 (자동 다운로드) |
| `add_page_break()` | 페이지 나누기 |
| `add_line()` | 구분선 |
| `add_header(text)` / `add_footer(text)` | 머리말 / 꼬리말 |
| `add_page_number(pos)` | 페이지 번호 (4가지 위치) |
| `add_footnote(text)` | 각주 |
| `add_equation(script)` | 수식 |
| `add_highlight(text, color)` | 하이라이트 텍스트 |
| `add_rectangle(...)` / `add_draw_line(...)` | 도형 |
| `save(path)` | .hwpx로 저장 |

### 저수준 API (pyhwpxlib.api)

HWPX 객체 모델을 직접 제어할 때 사용합니다:

```python
from pyhwpxlib.api import create_document, add_paragraph, add_table, save

doc = create_document()
add_paragraph(doc, "안녕하세요!", bold=True, font_size=14)
add_table(doc, rows=3, cols=2, data=[["A","B"],["1","2"],["3","4"]])
save(doc, "output.hwpx")
```

**저수준 함수 전체 목록:**

| 카테고리 | 함수 |
|----------|------|
| 텍스트 | `add_paragraph`, `add_styled_paragraph`, `add_heading`, `add_hyperlink`, `add_code_block` |
| 목록 | `add_bullet_list`, `add_numbered_list`, `add_nested_bullet_list`, `add_nested_numbered_list` |
| 표 | `add_table` (셀 병합, 그라데이션, 셀별 스타일) |
| 이미지 & 도형 | `add_image`, `add_rectangle`, `add_ellipse`, `add_line`, `add_arc`, `add_polygon`, `add_curve`, `add_connect_line`, `add_textart`, `add_rectangle_with_image_fill` |
| 레이아웃 | `add_header`, `add_footer`, `add_page_number`, `add_page_break`, `set_page_setup`, `set_columns` |
| 주석 | `add_footnote`, `add_bookmark`, `add_indexmark`, `add_hidden_comment`, `add_highlight`, `add_dutmal` |
| 특수 | `add_equation`, `add_tab`, `add_special_char`, `add_container` |
| 폼 컨트롤 | `add_checkbox`, `add_radio_button`, `add_button`, `add_combobox`, `add_listbox`, `add_edit_field`, `add_scrollbar` |
| 변환 | `convert_md_to_hwpx`, `convert_md_file_to_hwpx`, `convert_html_to_hwpx`, `convert_html_file_to_hwpx`, `convert_hwpx_to_html` |
| 읽기 | `open_document`, `extract_text`, `extract_markdown`, `extract_html` |
| 양식 | `fill_template`, `fill_template_checkbox`, `fill_template_batch`, `extract_schema`, `analyze_schema_with_llm` |
| 문서 | `merge_documents` |
| 페이지 설정 | `set_page_setup(paper="A4"/"A3"/"B5"/"LETTER"/"LEGAL", landscape=True, margin_*)` |

### 변환 매트릭스

| 방향 | CLI | Python |
|------|-----|--------|
| 마크다운 → HWPX | `pyhwpxlib md2hwpx in.md -o out.hwpx` | `convert_md_file_to_hwpx("in.md", "out.hwpx")` |
| HTML → HWPX | -- | `convert_html_file_to_hwpx("in.html", "out.hwpx")` |
| HWPX → HTML | `pyhwpxlib hwpx2html in.hwpx -o out.html` | `convert_hwpx_to_html("in.hwpx", "out.html")` |
| HWP 5.x → HWPX | -- | `from pyhwpxlib.hwp2hwpx import convert; convert("old.hwp", "new.hwpx")` |
| HWPX → 텍스트 | `pyhwpxlib text in.hwpx` | `extract_text("document.hwpx")` |
| HWPX → 마크다운 | `pyhwpxlib text in.hwpx -f markdown` | `extract_markdown("document.hwpx")` |

### 양식 자동화

```python
from pyhwpxlib.api import extract_schema, fill_template_checkbox, fill_template_batch

# 1. 양식에 어떤 필드가 있는지 탐지
schema = extract_schema("서식_양식.hwpx")
print(schema)  # {'title': '...', 'fields': [...], 'checkboxes': [...]}

# 2. 단일 문서 채우기
fill_template_checkbox(
    "서식_양식.hwpx",
    data={">성 명<": ">성 명  홍길동<"},
    checks=["동의함"],
    output_path="서식_홍길동.hwpx",
)

# 3. 여러 건을 한번에 생성 (배치)
fill_template_batch(
    "서식_양식.hwpx",
    records=[
        {"data": {">성 명<": ">성 명  김철수<"}, "checks": ["동의함"]},
        {"data": {">성 명<": ">성 명  이영희<"}, "checks": ["동의함"]},
    ],
    output_dir="output/",
)
```

### 기존 문서 편집 (언팩/팩)

```bash
pyhwpxlib unpack 문서.hwpx -o unpacked/        # ZIP을 폴더로 풀기
# unpacked/Contents/ 안의 XML 파일을 직접 편집
pyhwpxlib pack unpacked/ -o output.hwpx         # 다시 HWPX로 묶기
pyhwpxlib validate output.hwpx                  # 구조 검증
```

---

## 미리보기 (HWP/HWPX → SVG)

HWP 또는 HWPX 문서를 SVG로 렌더링해 시각적으로 확인하거나 LLM이 검토하게 할 수 있습니다:

```bash
pip install pyhwpxlib[preview]
```

```python
from pyhwpxlib.rhwp_bridge import RhwpEngine

engine = RhwpEngine()  # WASM 1회 로드
with engine.load("sample.hwp") as doc:   # HWP / HWPX 둘 다
    print(doc.page_count)
    svg = doc.render_page_svg(0)
    all_svgs = doc.render_all_svgs()
```

macOS에서 한글 폰트 측정을 더 정확히 하려면 Pillow도 함께 설치:

```bash
pip install pyhwpxlib[preview-fonts]
```

이 기능은 LLM이 HWPX 문서를 생성한 뒤 결과물을 시각적으로 검증해야 하는
워크플로에 특히 유용합니다.

### 서드파티 고지

미리보기 기능은 [rhwp 프로젝트](https://github.com/edwardkim/rhwp)에서
빌드된 WebAssembly 바이너리를 번들로 포함합니다 (MIT License,
© 2025-2026 Edward Kim). 바이너리는 수정 없이 재배포됩니다.
자세한 내용은 [`NOTICE.md`](NOTICE.md)와 `pyhwpxlib/vendor/LICENSE.rhwp.txt`
를 참조하세요.

---

## HWPX 포맷이란?

HWPX는 한컴오피스의 차세대 문서 포맷입니다. ZIP 안에 XML 파일이 들어있는 구조로, Microsoft Word의 `.docx`와 비슷한 개념입니다. 한국 공공기관과 기업에서 표준으로 사용됩니다.

## 크레딧

| 프로젝트 | 저작자 | 라이선스 | 사용 내용 |
|---------|--------|---------|----------|
| [hwp2hwpx](https://github.com/neolord0/hwp2hwpx) | neolord0 | Apache 2.0 | HWP→HWPX 변환 로직 (Python 포팅) |
| [hwplib](https://github.com/neolord0/hwplib) | neolord0 | Apache 2.0 | HWP 바이너리 파서 (Python 포팅) |
| [python-hwpx](https://github.com/airmang/python-hwpx) | 고규현 | MIT | HWPX 데이터클래스 모델 |
| [rhwp](https://github.com/edwardkim/rhwp) | Edward Kim | MIT | HWP/HWPX → SVG 렌더러 (WASM 번들, `[preview]` extras) |

## 알려진 한계

- 복잡한 셀 병합 레이아웃은 수동 검토 필요
- ~~HWPX 렌더링 미리보기 미지원~~ → **v0.2.0부터 `[preview]` 지원**
- CSS→HWPX 매핑은 주요 속성 46개만 지원
- 이미지 내 텍스트 인식(OCR)은 별도 API 키 필요

## 라이선스

파일별로 다른 라이선스가 적용됩니다. 자세한 내용은 [LICENSE.md](LICENSE.md)를 참조하세요.

| 대상 | 라이선스 |
|------|---------|
| `hwp2hwpx.py`, `hwp_reader.py`, `value_convertor.py` | Apache 2.0 (원본 파생물) |
| **나머지 전체** | **BSL 1.1** |

**BSL 1.1 요약:**
- 개인/비상업/교육/오픈소스 → **무료**
- 사내 5인 이하 → **무료**
- 상업적 사용/6인 이상 → **유료 라이선스 필요**
