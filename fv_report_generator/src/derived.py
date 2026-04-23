"""
Derived-row computations — some template rows are ratios that can't be summed
from raw CSV data (e.g. %กำไรส่วนเกิน = contribution margin / revenue).
"""
from .normalizer import canonical


def compute_contribution_margin_percent(cells: dict, schema) -> dict:
    """Overwrite row 79 cells with (row 78) / (row 10) * 100 per column.

    Args:
        cells: {(row, col): value} dict, mutated in place
        schema: TemplateSchema

    Returns:
        cells (same dict, for chaining)
    """
    revenue_row = schema.row_map.get((canonical("1. รายได้"), None, None))
    cm_row = schema.row_map.get((canonical("3. กำไรส่วนเกิน [CONTRIBUTION MARGIN] (1)-(2)"), None, None))
    pct_row = schema.row_map.get((canonical("%กำไรส่วนเกิน (3)/(1)"), None, None))

    if revenue_row is None or cm_row is None or pct_row is None:
        return cells

    cols_with_pct = set()
    for (r, c) in list(cells.keys()):
        if r == pct_row:
            cols_with_pct.add(c)
            del cells[(r, c)]

    for c in schema.col_map.values():
        revenue = cells.get((revenue_row, c))
        cm = cells.get((cm_row, c))
        if revenue and revenue != 0:
            cells[(pct_row, c)] = (cm or 0) / revenue * 100.0
        elif c in cols_with_pct:
            cells[(pct_row, c)] = 0.0

    return cells
