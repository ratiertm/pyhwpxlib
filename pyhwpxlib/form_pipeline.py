"""Form filling pipeline — label-based navigation + cell patching.

This module provides utilities for filling HWPX form templates by:
1. Parsing all table cells and their (row, col) addresses
2. Finding label cells by text match
3. Navigating to adjacent cells (right/left/up/down) relative to labels
4. Patching empty cells via cellAddr anchor or replacing placeholder text

Used by the MCP server's ``hwpx_fill_form`` and ``hwpx_analyze_form`` tools
and directly importable for label-based form automation.

Example
-------
>>> from pyhwpxlib.form_pipeline import fill_by_labels
>>> fill_by_labels("resume.hwpx", {
...     "성 명>right": "홍길동",
...     "전화번호>right": "010-1234-5678",
... }, "resume_filled.hwpx")
"""
from __future__ import annotations

import re
import shutil
import zipfile
from typing import Optional


# ---------------------------------------------------------------------------
# Low-level XML parsing
# ---------------------------------------------------------------------------

_CELL_RE = re.compile(r'<hp:tc\b[^>]*>.*?</hp:tc>', re.DOTALL)
_CELL_ADDR_RE = re.compile(r'colAddr="(\d+)"\s+rowAddr="(\d+)"')
_CELL_SPAN_RE = re.compile(r'colSpan="(\d+)"\s+rowSpan="(\d+)"')
_HP_T_RE = re.compile(r'<hp:t>([^<]*)</hp:t>')
_TBL_RE = re.compile(r'<hp:tbl\b[^>]*rowCnt="(\d+)"\s+colCnt="(\d+)"[^>]*>')


def _iter_section_xmls(hwpx_path: str):
    """Yield (name, xml_string) for every Contents/sectionN.xml."""
    with zipfile.ZipFile(hwpx_path) as z:
        for name in z.namelist():
            if re.match(r'Contents/section\d+\.xml$', name):
                yield name, z.read(name).decode('utf-8')


def _parse_cells(xml: str) -> list[dict]:
    """Return list of cell dicts with row, col, colSpan, rowSpan, text, start, end."""
    cells = []
    for m in _CELL_RE.finditer(xml):
        cell_xml = m.group(0)
        addr = _CELL_ADDR_RE.search(cell_xml)
        if not addr:
            continue
        col, row = int(addr.group(1)), int(addr.group(2))
        span = _CELL_SPAN_RE.search(cell_xml)
        col_span = int(span.group(1)) if span else 1
        row_span = int(span.group(2)) if span else 1
        texts = _HP_T_RE.findall(cell_xml)
        text = ''.join(texts).strip()
        cells.append({
            'row': row, 'col': col,
            'colSpan': col_span, 'rowSpan': row_span,
            'text': text,
            'start': m.start(), 'end': m.end(),
            'xml': cell_xml,
        })
    return cells


# ---------------------------------------------------------------------------
# Cell patching primitives
# ---------------------------------------------------------------------------

def _escape_xml(s: str) -> str:
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _patch_empty_cell(cell_xml: str, text: str) -> tuple[str, bool]:
    """Replace the first empty <hp:t/> or <hp:t></hp:t> with text. Returns (new_xml, changed)."""
    esc = _escape_xml(text)
    new = re.sub(r'<hp:t\s*/>', f'<hp:t>{esc}</hp:t>', cell_xml, count=1)
    if new == cell_xml:
        new = re.sub(r'<hp:t></hp:t>', f'<hp:t>{esc}</hp:t>', cell_xml, count=1)
    return new, new != cell_xml


def _replace_placeholder(cell_xml: str, search: str, replace: str) -> tuple[str, bool]:
    """Replace placeholder text inside <hp:t> runs. Returns (new_xml, changed)."""
    if search not in cell_xml:
        return cell_xml, False
    # Limit replacement to <hp:t> content
    def sub_text(m):
        return '<hp:t>' + m.group(1).replace(search, replace, 1) + '</hp:t>'
    new = re.sub(r'<hp:t>([^<]*)</hp:t>',
                 lambda m: sub_text(m) if search in m.group(1) else m.group(0),
                 cell_xml, count=1)
    return new, new != cell_xml


# ---------------------------------------------------------------------------
# Label-based navigation
# ---------------------------------------------------------------------------

_DIRECTIONS = {
    'right': (0, +1),
    'left':  (0, -1),
    'up':    (-1, 0),
    'down':  (+1, 0),
}


def find_cell_by_label(
    form: dict,
    label: str,
    direction: str = 'right',
) -> Optional[dict]:
    """Find a cell matching ``label`` and return the target cell in the given direction.

    Parameters
    ----------
    form : dict
        As returned by :func:`extract_form`.
    label : str
        Label text to search for (substring or exact match on cell text).
    direction : str
        One of ``right``, ``left``, ``up``, ``down``.

    Returns
    -------
    dict or None
        ``{"label_cell": {...}, "target_cell": {...}}`` or None if not found.
    """
    if direction not in _DIRECTIONS:
        return None
    dr, dc = _DIRECTIONS[direction]

    for tbl in form.get('tables', []):
        cells = tbl['cells']
        # Build (row, col) → cell index
        by_pos = {(c['row'], c['col']): c for c in cells}

        # Search for label match
        for lbl in cells:
            if not lbl['text']:
                continue
            # Match if label text is contained or equals
            if label.strip() in lbl['text'].strip() or lbl['text'].strip() == label.strip():
                # Compute target position
                # Respect colSpan/rowSpan (step beyond the label cell boundary)
                if direction == 'right':
                    tr = lbl['row']
                    tc = lbl['col'] + max(1, lbl.get('colSpan', 1))
                elif direction == 'left':
                    tr = lbl['row']
                    tc = lbl['col'] - 1
                elif direction == 'down':
                    tr = lbl['row'] + max(1, lbl.get('rowSpan', 1))
                    tc = lbl['col']
                else:  # up
                    tr = lbl['row'] - 1
                    tc = lbl['col']

                target = by_pos.get((tr, tc))
                if target is not None:
                    return {
                        'label_cell': {
                            'row': lbl['row'], 'col': lbl['col'],
                            'text': lbl['text'],
                        },
                        'target_cell': {
                            'row': target['row'], 'col': target['col'],
                            'text': target['text'],
                        },
                        'table_index': tbl['index'],
                    }
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_form(hwpx_path: str) -> dict:
    """Extract all tables and cells from every section.

    Returns
    -------
    dict
        ``{"tables": [{"index": int, "rows": int, "cols": int,
                       "cells": [{row, col, colSpan, rowSpan, text, lines}...],
                       "section": str}, ...]}``

    ``lines`` is a placeholder for compatibility with the MCP server shape.
    """
    tables = []
    t_index = 0
    for section_name, xml in _iter_section_xmls(hwpx_path):
        # Split into per-table blocks
        tbl_spans = []
        for m in re.finditer(r'<hp:tbl\b[^>]*>', xml):
            start = m.start()
            # Find matching </hp:tbl>
            end = xml.find('</hp:tbl>', m.end())
            if end < 0:
                continue
            end += len('</hp:tbl>')
            tbl_spans.append((start, end, m.group(0)))

        for start, end, open_tag in tbl_spans:
            tbl_xml = xml[start:end]
            row_match = re.search(r'rowCnt="(\d+)"', open_tag)
            col_match = re.search(r'colCnt="(\d+)"', open_tag)
            rows = int(row_match.group(1)) if row_match else 0
            cols = int(col_match.group(1)) if col_match else 0
            parsed = _parse_cells(tbl_xml)
            # Add lines key for backward compat with skill/server shape
            for c in parsed:
                c['lines'] = [{'runs': [{'text': c['text']}]}] if c['text'] else []
            tables.append({
                'index': t_index,
                'rows': rows,
                'cols': cols,
                'cells': parsed,
                'section': section_name,
            })
            t_index += 1
    return {'tables': tables}


def fill_by_labels(
    template_path: str,
    mappings: dict[str, str],
    output_path: str,
) -> dict:
    """Fill an HWPX form template by label-based navigation.

    Parameters
    ----------
    template_path : str
        Path to the source .hwpx file.
    mappings : dict
        Keys are ``"<label>>direction"`` strings (direction is one of
        ``right``/``left``/``up``/``down``). Values are the text to insert.
    output_path : str
        Path for the filled output .hwpx file.

    Returns
    -------
    dict
        ``{"applied": int, "failed": int, "details": [...]}`` with
        per-mapping success/failure info.
    """
    shutil.copy2(template_path, output_path)

    details = []
    applied = 0
    failed = 0

    # Process section-by-section (most forms have section0 only, but handle multi)
    section_xmls = dict(_iter_section_xmls(template_path))

    # Parse once per section
    form = extract_form(template_path)

    for key, value in mappings.items():
        if '>' not in key:
            details.append({'mapping': key, 'status': 'skipped',
                            'reason': 'no direction (use "label>direction")'})
            failed += 1
            continue
        label, direction = key.rsplit('>', 1)
        direction = direction.strip().lower()

        found = find_cell_by_label(form, label.strip(), direction)
        if not found:
            details.append({'mapping': key, 'status': 'not_found',
                            'reason': f'label "{label}" not found'})
            failed += 1
            continue

        tbl_idx = found['table_index']
        tbl = form['tables'][tbl_idx]
        section_name = tbl['section']
        xml = section_xmls[section_name]

        # Locate target cell in live XML by its (row, col)
        target_row = found['target_cell']['row']
        target_col = found['target_cell']['col']

        # Find cell byte range in current XML
        anchor = f'colAddr="{target_col}" rowAddr="{target_row}"'
        idx = xml.find(anchor)
        if idx < 0:
            details.append({'mapping': key, 'status': 'failed',
                            'reason': 'target cell lost'})
            failed += 1
            continue
        cell_start = xml.rfind('<hp:tc', 0, idx)
        cell_end = xml.find('</hp:tc>', idx) + len('</hp:tc>')
        cell_xml = xml[cell_start:cell_end]

        # Try empty patch first, fall back to placeholder replacement if the
        # cell already has any text (e.g., placeholder like "년 월 일")
        new_cell, changed = _patch_empty_cell(cell_xml, value)
        if not changed and found['target_cell']['text']:
            # Cell has existing text — replace entire text content (first <hp:t>)
            new_cell = re.sub(r'<hp:t>[^<]*</hp:t>',
                              f'<hp:t>{_escape_xml(value)}</hp:t>',
                              cell_xml, count=1)
            changed = new_cell != cell_xml

        if not changed:
            details.append({'mapping': key, 'status': 'failed',
                            'reason': 'could not patch cell'})
            failed += 1
            continue

        # Update the in-memory section XML
        section_xmls[section_name] = xml[:cell_start] + new_cell + xml[cell_end:]
        applied += 1
        details.append({
            'mapping': key,
            'status': 'applied',
            'label_pos': f"r{found['label_cell']['row']}c{found['label_cell']['col']}",
            'target_pos': f"r{target_row}c{target_col}",
            'value': value,
        })

    # Write all modified sections back to the output file
    _rewrite_sections(output_path, section_xmls)

    return {'applied': applied, 'failed': failed, 'details': details}


def _rewrite_sections(hwpx_path: str, section_xmls: dict[str, str]) -> None:
    """Rewrite specific section XMLs in an HWPX file, preserving other entries.

    Keeps ``mimetype`` as the first entry with STORED compression.
    """
    # Read all entries first
    with zipfile.ZipFile(hwpx_path, 'r') as z:
        entries = [(n, z.read(n)) for n in z.namelist()]

    with zipfile.ZipFile(hwpx_path, 'w', zipfile.ZIP_DEFLATED) as z:
        # mimetype first, STORED
        for n, data in entries:
            if n == 'mimetype':
                z.writestr(zipfile.ZipInfo('mimetype'), data, zipfile.ZIP_STORED)
                break
        # Everything else
        for n, data in entries:
            if n == 'mimetype':
                continue
            if n in section_xmls:
                z.writestr(n, section_xmls[n].encode('utf-8'))
            else:
                z.writestr(n, data)
