"""FV report configuration — fonts, colors, layout constants."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


_DEFAULT_BU_COLORS = {
    # Match report_generator/config/report_config.py with both 0X and X. forms
    "1.กลุ่มธุรกิจ HARD INFRASTRUCTURE": "E2EFDA",
    "2.กลุ่มธุรกิจ INTERNATIONAL": "DDEBF7",
    "3.กลุ่มธุรกิจ MOBILE": "DBD3E5",
    "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND": "FCE4D6",
    "5.กลุ่มธุรกิจ DIGITAL": "D9E1F2",
    "6.กลุ่มธุรกิจ ICT SOLUTION": "C6E0B4",
    "7.กลุ่มบริการอื่นไม่ใช่โทรคมนาคม": "BDD7EE",
    "8.รายได้อื่น/ค่าใช้จ่ายอื่น": "EAC1C0",
    "9.บริการตามนโยบายภาครัฐ": "FFF2CC",
}


@dataclass
class MandatoryRow:
    """A row that must always appear in the report, even when absent from the CSV.

    Attributes
    ----------
    display_label:
        The text shown in the label column (e.g. '8. ต้นทุนทางการเงิน-ด้านการจัดหาเงิน').
    insert_after_code:
        Parent-section code after whose *last row* (including sub-rows) this
        row will be injected.  E.g. '07' to insert after all Depreciation rows.
    section_code:
        The section code to assign (used by reconciler to locate the row).
        Should match the numeric prefix of display_label.
    is_bold:
        Whether to render the label in bold (default True for section rows).
    color:
        Optional fill color hex (without '#').  Defaults to section_color.
    """
    display_label: str
    insert_after_code: str
    section_code: str
    is_bold: bool = True
    color: Optional[str] = None  # None → use config.section_color


@dataclass
class FVConfig:
    """Configuration for the FV (Fixed/Variable cost) report."""

    # Font/style
    font_name: str = "TH Sarabun New"
    font_size: int = 14
    header_font_size: int = 14
    title_font_size: int = 18

    # Column widths
    label_width: int = 50
    data_col_width: int = 16

    # Excel layout (1-indexed; row 1 = title, rows 2-3 = sub-title, rows 5-9 = column headers, row 10+ = data)
    title_row: int = 1
    company_row: int = 1
    report_title_row: int = 2
    period_row: int = 3
    header_start_row: int = 5
    header_rows: int = 5  # BU / SG / SUBSG / PKEY / PNAME
    data_start_row: int = 10
    label_col: int = 2  # column B

    # Colors
    bu_colors: Dict[str, str] = field(default_factory=lambda: dict(_DEFAULT_BU_COLORS))
    grand_total_color: str = "FFD966"
    label_header_color: str = "F4DEDC"
    section_color: str = "F8CBAD"
    derived_color: str = "FFF2CC"

    # Period info (set per run)
    period_year_be: int = 0       # Buddhist Era year (e.g., 2568)
    period_label: str = ""        # Display string for "ประจำเดือน X YYYY"

    # Rows that must always appear even when absent from the CSV.
    # Inserted in order after the section specified by insert_after_code.
    mandatory_rows: List[MandatoryRow] = field(default_factory=lambda: [
        MandatoryRow(
            display_label="8. ต้นทุนทางการเงิน-ด้านการจัดหาเงิน",
            insert_after_code="07",
            section_code="08",
        ),
    ])

    def bu_color(self, bu_canonical_or_raw: str) -> str:
        """Look up BU background color, with leading-zero tolerance."""
        if not bu_canonical_or_raw:
            return "FFFFFF"
        if bu_canonical_or_raw in self.bu_colors:
            return self.bu_colors[bu_canonical_or_raw]
        # Try with/without leading zero
        if len(bu_canonical_or_raw) >= 2 and bu_canonical_or_raw[1] == ".":
            if bu_canonical_or_raw[0:2].isdigit():
                alt = bu_canonical_or_raw[1:]
            elif bu_canonical_or_raw[0].isdigit():
                alt = "0" + bu_canonical_or_raw
            else:
                alt = None
            if alt and alt in self.bu_colors:
                return self.bu_colors[alt]
        return "FFFFFF"
