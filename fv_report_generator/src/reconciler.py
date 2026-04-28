"""
Reconciler — verify the generated .xlsx against the source CSV.

Algorithm: re-aggregate the CSV with the same pipeline used to build the
report, then walk every data cell in the output workbook and compare its
value to the expected aggregation. This catches writer bugs, lost cells,
column-map drift, and rounding regressions end-to-end.

This is the only verification path now — there is no external "Data_P14"
ground-truth file. The CSV itself is the source of truth.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import openpyxl
import pandas as pd

from . import aggregator, column_builder, derived, row_builder


@dataclass
class ReconcileResult:
    mismatches: List[Tuple] = field(default_factory=list)
    # (row_label, col_display, actual_in_xlsx, expected_from_csv, diff)

    cells_checked: int = 0
    cells_skipped: int = 0  # informational/empty etc.

    @property
    def ok(self) -> bool:
        return not self.mismatches


def _to_float(value) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def reconcile(
    output_path,
    df: pd.DataFrame,
    config,
    period_key: Optional[int] = None,
    sheet_name: str = "Report_FV",
    tolerance: float = 0.01,
) -> ReconcileResult:
    """Compare every non-label data cell in `output_path` to the pivot recomputed from `df`."""
    pivot = aggregator.build_pivot(df, period_key=period_key)
    columns = column_builder.build_columns(df, config, period_key=period_key)
    rows = row_builder.build_rows(df, config, period_key=period_key)

    wb = openpyxl.load_workbook(output_path, data_only=True)
    if sheet_name not in wb.sheetnames:
        raise KeyError(f"sheet {sheet_name!r} not found in {output_path}; available: {wb.sheetnames}")
    ws = wb[sheet_name]

    result = ReconcileResult()

    for row_offset, rd in enumerate(rows):
        xl_row = config.data_start_row + row_offset
        for col_offset, col in enumerate(columns):
            xl_col = config.label_col + col_offset
            if col.col_type == "label":
                continue

            ck = col.col_key
            if ck is None:
                continue

            # Expected value
            if rd.row_type == "percent":
                expected = derived.percent_value(pivot, ck)
            else:
                expected = pivot.get((rd.row_key, ck))

            actual = _to_float(ws.cell(xl_row, xl_col).value)

            # Treat None and 0 as equivalent (writer formats 0 as blank).
            exp_f = expected if expected is not None else 0.0
            act_f = actual if actual is not None else 0.0

            result.cells_checked += 1
            diff = act_f - exp_f
            if abs(diff) > tolerance:
                result.mismatches.append((
                    rd.display_label,
                    col.display_name or repr(ck),
                    act_f,
                    exp_f,
                    diff,
                ))
    return result
