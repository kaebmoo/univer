"""
Data writer — write each RowDef's label + data cells.

For percent rows, value = pivot[(CM, col_key)] / pivot[(REVENUE, col_key)].
For all other rows, value = pivot.get((row_key, col_key)).
"""
from typing import Dict, List

from .. import derived
from ..column_builder import ColumnDef
from ..row_builder import RowDef


class DataWriter:
    def __init__(self, config, formatter):
        self.config = config
        self.formatter = formatter

    def write(
        self,
        ws,
        columns: List[ColumnDef],
        rows: List[RowDef],
        pivot: Dict,
        start_xl_col: int,
    ) -> int:
        """Write all data rows; return next available row number (1-indexed)."""
        cur_row = self.config.data_start_row

        for rd in rows:
            for col_idx, col in enumerate(columns):
                xl_col = start_xl_col + col_idx
                cell = ws.cell(cur_row, xl_col)

                if col.col_type == "label":
                    self.formatter.format_label(
                        cell, rd.display_label, bold=rd.is_bold, color=rd.color,
                    )
                    continue

                ck = col.col_key
                if ck is None:
                    continue

                if rd.row_type == "percent":
                    val = derived.percent_value(pivot, ck)
                    self.formatter.format_percent(cell, val, bold=rd.is_bold, color=rd.color)
                else:
                    val = pivot.get((rd.row_key, ck))
                    if val is None:
                        # Sub-section header rows often have no direct value (they are bold sub-headers)
                        self.formatter.format_number(cell, None, bold=rd.is_bold, color=rd.color)
                    else:
                        self.formatter.format_number(cell, val, bold=rd.is_bold, color=rd.color)
            cur_row += 1
        return cur_row
