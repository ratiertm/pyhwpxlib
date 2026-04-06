# pyhwpxlib

Python library for creating, converting, and editing HWPX (Hancom Office) documents programmatically. No Hancom Office installation required.

[한국어](README_KO.md)

## Why pyhwpxlib?

- Generate HWPX reports on a server with zero desktop dependencies
- Convert Markdown, HTML, or legacy HWP 5.x files to HWPX
- Auto-fill government forms and contracts from data
- Let AI agents (Claude Code, Cursor, etc.) produce native Korean documents
- Extract text, Markdown, or HTML from existing HWPX files
- Merge multiple HWPX files into one

## Install

```bash
pip install pyhwpxlib
```

This installs both the Python library and the `pyhwpxlib` CLI command.

Python 3.10+ required. No external dependencies for core features.

```bash
# Optional: image support
pip install pyhwpxlib[images]    # Pillow

# Optional: faster XML parsing
pip install pyhwpxlib[lxml]      # lxml

# Install everything
pip install pyhwpxlib[all]
```

## Quick Start

### Create a document in 5 lines

```python
from pyhwpxlib import HwpxBuilder

doc = HwpxBuilder()
doc.add_heading("Project Report", level=1)
doc.add_paragraph("April 2026")
doc.add_table([
    ["Item", "Qty", "Price"],
    ["Server", "3", "9,000,000"],
    ["License", "10", "5,000,000"],
])
doc.add_heading("1. Overview", level=2)
doc.add_paragraph("This report covers...")
doc.save("report.hwpx")
```

### Convert Markdown from the terminal

```bash
pyhwpxlib md2hwpx report.md -o report.hwpx
```

### Fill a government form template

```python
from pyhwpxlib.api import fill_template_checkbox

fill_template_checkbox(
    "contract_template.hwpx",
    data={">Name<": ">Name  John Doe<"},
    checks=["Agree"],
    output_path="contract_filled.hwpx",
)
```

---

## CLI Reference

`pip install pyhwpxlib` installs the `pyhwpxlib` command with 6 subcommands:

### md2hwpx -- Markdown to HWPX

```bash
pyhwpxlib md2hwpx report.md -o report.hwpx
pyhwpxlib md2hwpx report.md -o report.hwpx -s github   # style preset
```

Auto-detects: headings (#), **bold**, *italic*, bullet/numbered lists, code blocks, tables, horizontal rules.

### hwpx2html -- HWPX to HTML

```bash
pyhwpxlib hwpx2html document.hwpx -o document.html
```

Produces a self-contained HTML with embedded base64 images.

### text -- Extract text from HWPX

```bash
pyhwpxlib text document.hwpx                      # plain text (default)
pyhwpxlib text document.hwpx -f markdown           # as Markdown
pyhwpxlib text document.hwpx -f html               # as HTML
```

### fill -- Fill template with data

```bash
# Key-value pairs
pyhwpxlib fill template.hwpx -o filled.hwpx -d name=Hong age=30

# From JSON file
pyhwpxlib fill template.hwpx -o filled.hwpx -d data.json
```

### info -- Inspect HWPX file

```bash
pyhwpxlib info document.hwpx
```

Shows file size, section count, image list, text character/line counts, and a text preview.

### merge -- Merge multiple HWPX files

```bash
pyhwpxlib merge part1.hwpx part2.hwpx part3.hwpx -o combined.hwpx
```

Inserts page breaks between documents automatically.

---

## Python API

### Document Creation (HwpxBuilder)

High-level builder with method chaining. Includes table style presets (`corporate`, `government`, `academic`, `default`).

```python
doc = HwpxBuilder(table_preset='corporate')
```

| Method | Description |
|--------|-------------|
| `add_heading(text, level)` | Headings (level 1--4) |
| `add_paragraph(text, bold, italic, font_size, text_color, alignment)` | Styled paragraphs |
| `add_table(data, header_bg, col_widths, merge_info, cell_colors, ...)` | Tables with auto-preset styling |
| `add_bullet_list(items, bullet_char)` | Bullet lists (`-`, `•`, `◦`) |
| `add_numbered_list(items, format_string)` | Numbered lists (`^1.`, `^1)`, `(^1)`) |
| `add_nested_bullet_list(items)` | Multi-level bullet lists (level 0--6) |
| `add_nested_numbered_list(items)` | Multi-level numbered lists |
| `add_image(path, width, height)` | Local image |
| `add_image_from_url(url, width, height)` | Image from URL (auto-download) |
| `add_page_break()` | Page break |
| `add_line()` | Horizontal divider |
| `add_header(text)` / `add_footer(text)` | Header / Footer |
| `add_page_number(pos)` | Page numbers (4 positions) |
| `add_footnote(text)` | Footnotes |
| `add_equation(script)` | Math equations |
| `add_highlight(text, color)` | Highlighted text |
| `add_rectangle(...)` / `add_draw_line(...)` | Shapes |
| `save(path)` | Save as .hwpx |

### Low-Level API (pyhwpxlib.api)

For fine-grained control over the HWPX object model:

```python
from pyhwpxlib.api import create_document, add_paragraph, add_table, save

doc = create_document()
add_paragraph(doc, "Hello, World!", bold=True, font_size=14)
add_table(doc, rows=3, cols=2, data=[["A","B"],["1","2"],["3","4"]])
save(doc, "output.hwpx")
```

**Additional low-level functions:**

| Category | Functions |
|----------|-----------|
| Text | `add_paragraph`, `add_styled_paragraph`, `add_heading`, `add_hyperlink`, `add_code_block` |
| Lists | `add_bullet_list`, `add_numbered_list`, `add_nested_bullet_list`, `add_nested_numbered_list` |
| Tables | `add_table` (with merge, gradient, per-cell styles) |
| Images & Shapes | `add_image`, `add_rectangle`, `add_ellipse`, `add_line`, `add_arc`, `add_polygon`, `add_curve`, `add_connect_line`, `add_textart`, `add_rectangle_with_image_fill` |
| Layout | `add_header`, `add_footer`, `add_page_number`, `add_page_break`, `set_page_setup`, `set_columns` |
| Annotations | `add_footnote`, `add_bookmark`, `add_indexmark`, `add_hidden_comment`, `add_highlight`, `add_dutmal` |
| Special | `add_equation`, `add_tab`, `add_special_char`, `add_container` |
| Form Controls | `add_checkbox`, `add_radio_button`, `add_button`, `add_combobox`, `add_listbox`, `add_edit_field`, `add_scrollbar` |
| Conversion | `convert_md_to_hwpx`, `convert_md_file_to_hwpx`, `convert_html_to_hwpx`, `convert_html_file_to_hwpx`, `convert_hwpx_to_html` |
| Reading | `open_document`, `extract_text`, `extract_markdown`, `extract_html` |
| Templates | `fill_template`, `fill_template_checkbox`, `fill_template_batch`, `extract_schema`, `analyze_schema_with_llm` |
| Documents | `merge_documents` |
| Page Setup | `set_page_setup(paper="A4"/"A3"/"B5"/"LETTER"/"LEGAL", landscape=True, margin_*)` |

### Conversions

| Direction | CLI | Python |
|-----------|-----|--------|
| Markdown → HWPX | `pyhwpxlib md2hwpx in.md -o out.hwpx` | `convert_md_file_to_hwpx("in.md", "out.hwpx")` |
| HTML → HWPX | -- | `convert_html_file_to_hwpx("in.html", "out.hwpx")` |
| HWPX → HTML | `pyhwpxlib hwpx2html in.hwpx -o out.html` | `convert_hwpx_to_html("in.hwpx", "out.html")` |
| HWP 5.x → HWPX | -- | `from pyhwpxlib.hwp2hwpx import convert; convert("old.hwp", "new.hwpx")` |
| HWPX → Text | `pyhwpxlib text in.hwpx` | `extract_text("document.hwpx")` |
| HWPX → Markdown | `pyhwpxlib text in.hwpx -f markdown` | `extract_markdown("document.hwpx")` |

### Template Automation

```python
from pyhwpxlib.api import extract_schema, fill_template_checkbox, fill_template_batch

# 1. Discover what fields a template has
schema = extract_schema("form_template.hwpx")
print(schema)  # {'title': '...', 'fields': [...], 'checkboxes': [...]}

# 2. Fill a single document
fill_template_checkbox(
    "form_template.hwpx",
    data={">Name<": ">Name  Jane Doe<"},
    checks=["Agree"],
    output_path="filled.hwpx",
)

# 3. Batch-generate from a list of records
fill_template_batch(
    "form_template.hwpx",
    records=[
        {"data": {">Name<": ">Name  Alice<"}, "checks": ["Agree"]},
        {"data": {">Name<": ">Name  Bob<"},   "checks": ["Agree"]},
    ],
    output_dir="output/",
)
```

### Edit Existing Documents (Unpack/Pack)

```bash
python -m pyhwpxlib unpack document.hwpx unpacked/   # Extract ZIP to folder
# Edit XML files in unpacked/Contents/ directly
python -m pyhwpxlib pack unpacked/ output.hwpx        # Re-package as HWPX
python -m pyhwpxlib validate output.hwpx              # Validate structure
```

---

## What is HWPX?

HWPX is the modern document format for Hancom Office, the standard office suite in South Korea. It's a ZIP archive containing XML files (OWPML spec) -- similar to `.docx` for Microsoft Word. Used by Korean government agencies, public institutions, and enterprises.

## Credits

| Project | Author | License | Usage |
|---------|--------|---------|-------|
| [hwp2hwpx](https://github.com/neolord0/hwp2hwpx) | neolord0 | Apache 2.0 | HWP→HWPX conversion (ported to Python) |
| [hwplib](https://github.com/neolord0/hwplib) | neolord0 | Apache 2.0 | HWP binary parser (ported to Python) |
| [python-hwpx](https://github.com/airmang/python-hwpx) | Kyuhyun Ko | MIT | HWPX dataclass model |

## Known Limitations

- Complex cell-merge layouts may require manual review
- No built-in HWPX preview (verify in Hancom Office or Whale)
- CSS→HWPX mapping covers 46 major properties only
- Image OCR for form text requires a separate API key

## License

Dual license -- see [LICENSE.md](LICENSE.md) for details.

| Files | License |
|-------|---------|
| `hwp2hwpx.py`, `hwp_reader.py`, `value_convertor.py` | Apache 2.0 (derivative works) |
| **All other files** | **BSL 1.1** |

**BSL 1.1 summary:** Personal/non-commercial/educational/open-source use is free. Commercial use requires a license. Converts to Apache 2.0 after 2030-04-07.
