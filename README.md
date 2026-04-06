# pyhwpxlib

Python library for creating and editing HWPX (Hancom Office) documents. No Hancom Office installation required.

[한국어](README_KO.md)

## Install

```bash
pip install pyhwpxlib
```

Python 3.10+

## Quick Start

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

## Features

### Create Documents

```python
doc = HwpxBuilder()
doc.add_heading(text, level)           # Headings (1-4)
doc.add_paragraph(text, bold, font_size, text_color)  # Paragraphs
doc.add_table(data, header_bg, col_widths)  # Tables with presets
doc.add_bullet_list(items)             # Bullet lists
doc.add_numbered_list(items)           # Numbered lists
doc.add_image(path, width, height)     # Images
doc.add_page_break()                   # Page breaks
doc.add_header(text)                   # Headers
doc.add_footer(text)                   # Footers
doc.add_page_number()                  # Page numbers
doc.save(path)
```

### Convert

```bash
# Markdown → HWPX
pyhwpxlib md2hwpx report.md -o report.hwpx

# HWP 5.x → HWPX
python -c "from pyhwpxlib.hwp2hwpx import convert; convert('old.hwp', 'new.hwpx')"
```

```python
# HTML → HWPX
from pyhwpxlib.api import convert_html_file_to_hwpx
convert_html_file_to_hwpx("page.html", "doc.hwpx")

# Text extraction
from pyhwpxlib.api import extract_text
text = extract_text("document.hwpx")
```

### Fill Form Templates

```python
from pyhwpxlib.api import fill_template_checkbox

fill_template_checkbox(
    "contract_template.hwpx",
    data={">Name<": ">Name  John Doe<"},
    checks=["Agree"],
    output_path="contract_filled.hwpx",
)
```

### Edit Existing Documents

```bash
python -m pyhwpxlib unpack document.hwpx unpacked/
# Edit XML files in unpacked/Contents/
python -m pyhwpxlib pack unpacked/ output.hwpx
python -m pyhwpxlib validate output.hwpx
```

## What is HWPX?

HWPX is the modern document format for Hancom Office, the standard office suite in South Korea. It's a ZIP archive containing XML files (OWPML spec) — similar to `.docx` for Microsoft Word.

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

Dual license — see [LICENSE.md](LICENSE.md) for details.

| Files | License |
|-------|---------|
| `hwp2hwpx.py`, `hwp_reader.py`, `value_convertor.py` | Apache 2.0 (derivative works) |
| **All other files** | **BSL 1.1** |

**BSL 1.1 summary:** Personal/non-commercial/educational/open-source use is free. Commercial use requires a license. Converts to Apache 2.0 after 2030-04-07.
