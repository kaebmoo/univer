"""Derived-row computations for the FV report.

%กำไรส่วนเกิน (3)/(1) is recomputed per column from contribution margin /
revenue rather than summed from CSV (CSV ships pre-computed per-product
percentages under GROUP "33." that are not summable).
"""
from typing import Optional

from .normalizer import canonical


_REVENUE_KEY = (canonical("01.รายได้"), None, None)
_CM_KEY = (canonical("03.กำไรส่วนเกิน [CONTRIBUTION MARGIN] (1) (2)"), None, None)
PERCENT_ROW_KEY = (canonical("%กำไรส่วนเกิน (3)/(1)"), None, None)


def percent_value(pivot: dict, col_key: tuple) -> Optional[float]:
    """Return contribution-margin / revenue for a column, or None if undefined."""
    revenue = pivot.get((_REVENUE_KEY, col_key))
    cm = pivot.get((_CM_KEY, col_key))
    if not revenue:
        return None
    return (cm or 0.0) / revenue
