"""Backwards-compatibility shim — re-export build_pivot from aggregator.

The original pivoter.build_pivot accepted an optional col_map for SG-alias
construction; the new aggregator no longer needs that (the data drives the
column structure), so col_map is accepted and ignored.
"""
from typing import Optional

import pandas as pd

from .aggregator import build_pivot as _build_pivot


def build_pivot(df: pd.DataFrame, period_key: Optional[int] = None, col_map=None) -> dict:
    return _build_pivot(df, period_key=period_key)
