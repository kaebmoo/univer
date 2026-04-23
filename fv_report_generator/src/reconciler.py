"""
Reconciler — compare the pivoted values from CSV against the Data_P14 sheet in
the template workbook. Data_P14 is a wide matrix (rows = line items, columns =
BU/SG/Product flat hierarchy); we walk it cell-by-cell, match to our canonical
(row_key, col_key), and report mismatches.
"""
from dataclasses import dataclass, field
from typing import Optional

import openpyxl

from .normalizer import canonical, canonical_product_key


@dataclass
class ReconcileResult:
    csv_only: list = field(default_factory=list)     # (row_key, col_key, csv_value) — no match in Data_P14
    data_only: list = field(default_factory=list)    # (row_label, col_label, data_value) — no match in pivot
    mismatches: list = field(default_factory=list)   # (row_key, col_key, csv_v, data_v, diff)

    @property
    def ok(self) -> bool:
        return not self.mismatches


def _data_p14_column_keys(ws):
    """Walk Data_P14 row 1 and infer a flat list of (col_num, col_key) based on label pattern."""
    keys = {}
    current_bu = None
    current_sg = None
    for c in range(1, ws.max_column + 1):
        raw = ws.cell(1, c).value
        if raw is None:
            continue
        text = str(raw).replace("\n", " ").strip()
        if c == 1:
            keys[c] = ("LABEL",)
            continue
        if text == "รวมทั้งสิ้น":
            keys[c] = ("GRAND_TOTAL",)
            continue
        # BU-level header (e.g., "1.กลุ่มธุรกิจ HARD INFRASTRUCTURE")
        # — starts with digit.digit-space OR single digit-dot
        if text and text[0].isdigit() and "กลุ่มธุรกิจ" in text and "." in text[:3]:
            current_bu = canonical(text)
            current_sg = None
            keys[c] = ("BU_TOTAL", current_bu)
            continue
        # SG-level header (e.g., "1.1 กลุ่มบริการท่อร้อยสาย")
        parts = text.split()
        first = parts[0] if parts else ""
        if "." in first and first[0].isdigit() and current_bu:
            current_sg = canonical(text)
            keys[c] = ("SG_TOTAL", current_bu, current_sg)
            continue
        # Product header: "<PRODUCT_KEY>\n<PRODUCT_NAME>" (newline replaced with space above)
        first_tok = parts[0] if parts else ""
        if first_tok.isdigit() and current_bu and current_sg:
            pkey = canonical_product_key(first_tok)
            keys[c] = ("PRODUCT", current_bu, current_sg, pkey)
            continue
        # Catch-all: single-column BU that also acts as its own SG (BU 8 case)
        if "รายได้อื่น" in text or "ค่าใช้จ่ายอื่น" in text:
            current_bu = canonical(text)
            current_sg = None
            keys[c] = ("BU_TOTAL", current_bu)
    return keys


def _data_p14_row_keys(ws):
    """Walk Data_P14 column 1 to infer (row_num, row_key) sequence from rows 2+."""
    keys = {}
    current_section = None
    current_sub1 = None
    for r in range(2, ws.max_row + 1):
        raw = ws.cell(r, 1).value
        if raw is None:
            continue
        label = str(raw)
        stripped = label.strip().lstrip("\u2000").strip()
        leading_ws = label[: len(label) - len(label.lstrip())]
        # Section-level labels start with "NN." no indent (e.g., "01.รายได้", "02.ค่าใช้จ่ายผันแปร")
        if stripped[:2].isdigit() and stripped[2:3] == "." and len(leading_ws) <= 1:
            current_section = canonical(stripped)
            current_sub1 = None
            keys[r] = (current_section, None, None)
            continue
        # Sub1 (non-indented but not numbered): e.g., "ต้นทุนบริการและต้นทุนขาย :"
        if len(leading_ws) == 0 and not stripped[:2].isdigit():
            current_sub1 = canonical(stripped)
            keys[r] = (current_section, current_sub1, None)
            continue
        # Indented: SUB_GROUP1 (no further nesting visible) OR SUB_GROUP2 (under expense sub1)
        item = canonical(stripped)
        if current_sub1 is not None:
            keys[r] = (current_section, current_sub1, item)
        else:
            keys[r] = (current_section, item, None)
    return keys


def _flatten_pivot(pivot: dict) -> dict:
    """Produce a view of pivot keyed in Data_P14's flat shape (no sub-SG level).

    Data_P14 has only SG-level aggregation, so we:
    - Drop SUBSG_TOTAL entries (they are a finer split already accounted for in SG_TOTAL).
    - Collapse 5-tuple PRODUCT (bu, sg, subsg, pkey) to 4-tuple (bu, sg, pkey).
      A single product appears once, so no summation across sub-SGs is needed.
    """
    flat = {}
    for (rk, ck), v in pivot.items():
        if ck[0] == "SUBSG_TOTAL":
            continue
        if ck[0] == "PRODUCT" and len(ck) == 5:
            new_ck = ("PRODUCT", ck[1], ck[2], ck[4])
        else:
            new_ck = ck
        flat[(rk, new_ck)] = flat.get((rk, new_ck), 0.0) + v
    return flat


def reconcile(template_path, pivot: dict, tolerance: float = 0.01) -> ReconcileResult:
    """Compare pivot dict against the Data_P14 sheet inside the template workbook."""
    wb = openpyxl.load_workbook(template_path, data_only=True)
    ws = wb["Data_P14"]

    col_keys = _data_p14_column_keys(ws)
    row_keys = _data_p14_row_keys(ws)
    flat_pivot = _flatten_pivot(pivot)

    result = ReconcileResult()
    seen = set()

    for r, rk in row_keys.items():
        for c, ck in col_keys.items():
            if ck == ("LABEL",):
                continue
            data_v = ws.cell(r, c).value
            try:
                data_v = float(data_v) if data_v is not None else 0.0
            except (TypeError, ValueError):
                continue
            pivot_v = flat_pivot.get((rk, ck))
            seen.add((rk, ck))
            if pivot_v is None:
                if abs(data_v) > tolerance:
                    result.data_only.append((rk, ck, data_v))
                continue
            diff = pivot_v - data_v
            if abs(diff) > tolerance:
                result.mismatches.append((rk, ck, pivot_v, data_v, diff))

    for (rk, ck), v in flat_pivot.items():
        if (rk, ck) in seen:
            continue
        if abs(v) > tolerance:
            result.csv_only.append((rk, ck, v))

    return result
