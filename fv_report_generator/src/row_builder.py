"""
Row builder — emit RowDef sequence by walking CSV's GROUP / SUB_GROUP1 /
SUB_GROUP2 hierarchy. The structure adapts to whatever the CSV contains; new
sub-groups (e.g., a new ER row in a future period) appear automatically.

Display labels follow Report_P14 conventions:
- Section headers: leading zero stripped ("02.X" → "2. X"), with " - Variable
  Cost" / " - Fixed Cost" suffix appended to expense sections.
- Sub-group-1 headers in expense sections (CSV "...:") become bold sub-section
  headers like "ต้นทุนบริการและต้นทุนขาย - Variable Cost".
- Sub-group-1 in revenue/other sections render as indented "    - <label>".
- Sub-group-2 always renders as indented "    - <label>".
- A "%กำไรส่วนเกิน (3)/(1)" derived row is inserted right after section 03.
- A "(1)" / "(2)" / etc. legend isn't injected — labels come straight from CSV.
"""
from dataclasses import dataclass
from typing import List, Optional

import pandas as pd

from . import aggregator
from .normalizer import canonical


# CSV section codes that are computed (no sub-groups; single value per column)
_PURE_SECTION_CODES = {"03", "05", "07", "09", "10", "11", "33"}

# Where to insert the derived %กำไรส่วนเกิน row
_PERCENT_AFTER_SECTION_CODE = "03"

_VARIABLE_SECTION_CODE = "02"
_FIXED_SECTION_CODE = "04"


@dataclass
class RowDef:
    row_type: str            # 'section' | 'sub1' | 'sub2' | 'percent' | 'informational'
    display_label: str
    row_key: tuple           # (section_canonical, sub1_canonical_or_None, sub2_canonical_or_None)
    is_bold: bool = False
    indent: int = 0          # informational only; otherwise ignored
    color: Optional[str] = None
    is_section: bool = False
    parent_section_code: Optional[str] = None  # '01', '02', etc.


def _section_code(section_raw: str) -> str:
    """Extract '01', '02', ... from a CSV GROUP label."""
    s = (section_raw or "").lstrip()
    code = ""
    for ch in s:
        if ch.isdigit():
            code += ch
        else:
            break
    return code.zfill(2) if code else ""


def _section_display(section_raw: str, code: str) -> str:
    """Strip CSV leading zero and apply Variable/Fixed suffix where applicable."""
    s = section_raw or ""
    # Drop leading "01." / "02." pattern
    if len(s) >= 3 and s[0:2].isdigit() and s[2] == ".":
        s = s[3:].lstrip()
        s = f"{int(code)}. {s}" if code else s
    if code == _VARIABLE_SECTION_CODE:
        return f"{s} - Variable Cost"
    if code == _FIXED_SECTION_CODE:
        return f"{s} - Fixed Cost"
    return s


def _strip_numeric_prefix(text: str) -> str:
    """Drop a leading 'NN.' or 'N.' prefix from a label (keep the rest as-is)."""
    s = (text or "").strip()
    i = 0
    while i < len(s) and s[i].isdigit():
        i += 1
    if i > 0 and i < len(s) and s[i] == ".":
        return s[i + 1:].lstrip()
    return s


def _sub1_display(sub1_raw: str, parent_code: str) -> str:
    """Render a SUB_GROUP1 label.

    For expense sections (02 = Variable, 04 = Fixed) where CSV ends with " :",
    render as a bold sub-header like "ต้นทุนบริการและต้นทุนขาย - Variable Cost".
    Otherwise render indented as "    - <stripped label>".
    """
    raw = (sub1_raw or "").strip()
    is_expense_section = parent_code in (_VARIABLE_SECTION_CODE, _FIXED_SECTION_CODE)
    is_subheader = is_expense_section and raw.endswith(":")
    label = _strip_numeric_prefix(raw)
    if label.endswith(":"):
        label = label[:-1].rstrip()
    if is_subheader:
        suffix = " - Variable Cost" if parent_code == _VARIABLE_SECTION_CODE else " - Fixed Cost"
        return label + suffix
    return f"    - {label}"


def _sub2_display(sub2_raw: str) -> str:
    return f"    - {_strip_numeric_prefix(sub2_raw)}"


def _is_expense_subheader(sub1_raw: str, parent_code: str) -> bool:
    raw = (sub1_raw or "").strip()
    return parent_code in (_VARIABLE_SECTION_CODE, _FIXED_SECTION_CODE) and raw.endswith(":")


def build_rows(
    df: pd.DataFrame,
    config,
    period_key: Optional[int] = None,
) -> List[RowDef]:
    """Walk CSV hierarchy and emit RowDef sequence."""
    rows: List[RowDef] = []
    sections = aggregator.enumerate_sections(df, period_key=period_key)

    for section_raw in sections:
        code = _section_code(section_raw)
        section_canonical = canonical(section_raw)
        section_display = _section_display(section_raw, code)

        rows.append(RowDef(
            row_type="section",
            display_label=section_display,
            row_key=(section_canonical, None, None),
            is_bold=True,
            color=config.section_color,
            is_section=True,
            parent_section_code=code,
        ))

        if code in _PURE_SECTION_CODES:
            # Section-level value only — no sub-groups
            if code == _PERCENT_AFTER_SECTION_CODE:
                rows.append(RowDef(
                    row_type="percent",
                    display_label="%กำไรส่วนเกิน (3)/(1)",
                    row_key=(canonical("%กำไรส่วนเกิน (3)/(1)"), None, None),
                    is_bold=True,
                    color=config.derived_color,
                ))
            continue

        # Walk sub_group1 / sub_group2
        sub_groups = aggregator.enumerate_sub_groups(df, section_raw, period_key=period_key)
        for sub1_raw, sub2_list in sub_groups.items():
            sub1_label = _sub1_display(sub1_raw, code)
            sub1_is_subheader = _is_expense_subheader(sub1_raw, code)
            sub1_canonical = canonical(sub1_raw)
            rows.append(RowDef(
                row_type="sub1",
                display_label=sub1_label,
                row_key=(section_canonical, sub1_canonical, None),
                is_bold=sub1_is_subheader,
                color=config.section_color if sub1_is_subheader else None,
            ))
            for sub2_raw in sub2_list:
                sub2_canonical = canonical(sub2_raw)
                rows.append(RowDef(
                    row_type="sub2",
                    display_label=_sub2_display(sub2_raw),
                    row_key=(section_canonical, sub1_canonical, sub2_canonical),
                ))
    return rows
