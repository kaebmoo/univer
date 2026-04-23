"""
Pivoter — transform long-format FV CSV into a {(row_key, col_key): sum(VALUE)} map
that aligns with the template schema produced by template_reader.

Each CSV row contributes to multiple aggregate levels:
- row: section → (section, sub1) → (section, sub1, sub2)
- col: GRAND_TOTAL → (BU) → (BU, SG) → (BU, SG, PRODUCT_KEY)

We sum per (row_key, col_key) pair. The writer later fills only cells whose row_key
AND col_key are both present in the template schema.
"""
from collections import defaultdict
from typing import Optional

import pandas as pd

from .normalizer import canonical, canonical_product_key
from .satellite_split import subsg_for


def _build_sg_alias(col_map: dict, df_sg_canon: set) -> dict:
    """Build a CSV-SG → template-SG canonical alias for cases where the template
    label is truncated or otherwise differs from the CSV.

    Heuristic: a CSV canonical matches a template canonical when one is a prefix
    of the other and the common prefix is at least 10 characters.
    """
    template_sgs = {k[2] for k in col_map if k[0] in ("SG_TOTAL", "SUBSG_TOTAL", "PRODUCT") and len(k) >= 3}
    alias = {}
    for csv_c in df_sg_canon:
        if csv_c in template_sgs:
            continue
        for t in template_sgs:
            if not t:
                continue
            prefix_len = min(len(csv_c), len(t))
            if prefix_len < 10:
                continue
            if csv_c.startswith(t) or t.startswith(csv_c):
                alias[csv_c] = t
                break
    return alias


def build_pivot(df: pd.DataFrame, period_key: Optional[int] = None, col_map: Optional[dict] = None) -> dict:
    """Return {(row_key, col_key): value} aggregation.

    row_key = (section, sub1_or_None, sub2_or_None), canonicalized.
    col_key is one of:
      ("GRAND_TOTAL",)
      ("BU_TOTAL", bu)
      ("SG_TOTAL", bu, sg)
      ("PRODUCT", bu, sg, pkey)
    with all text fields canonicalized.
    """
    if period_key is not None:
        df = df[df["TIME_KEY"] == period_key]

    sg_canon = df["SERVICE_GROUP"].map(lambda x: canonical(x) if pd.notna(x) else None)

    # Apply SG alias if a col_map is provided (handles template-side truncations etc.)
    sg_alias = _build_sg_alias(col_map, set(s for s in sg_canon if s)) if col_map else {}
    if sg_alias:
        sg_canon = sg_canon.map(lambda x: sg_alias.get(x, x) if x else x)

    work = pd.DataFrame({
        "section": df["GROUP"].map(canonical),
        "sub1": df["SUB_GROUP1"].map(lambda x: canonical(x) if pd.notna(x) else None),
        "sub2": df["SUB_GROUP2"].map(lambda x: canonical(x) if pd.notna(x) else None),
        "bu": df["BU"].map(canonical),
        "sg": sg_canon,
        "pkey": df["PRODUCT_KEY"].map(canonical_product_key),
        "value": df["VALUE"].astype(float).fillna(0.0),
    })

    totals = defaultdict(float)

    for row in work.itertuples(index=False):
        value = row.value
        if value == 0.0:
            continue

        section = row.section
        sub1 = row.sub1
        sub2 = row.sub2

        # Row-identity aggregates (walk from deepest up to section-level)
        row_keys = [(section, None, None)]
        if sub1:
            row_keys.append((section, sub1, None))
        if sub1 and sub2:
            row_keys.append((section, sub1, sub2))

        # Column-identity aggregates
        bu = row.bu
        sg = row.sg
        pkey = row.pkey
        col_keys = [("GRAND_TOTAL",)]
        if bu:
            col_keys.append(("BU_TOTAL", bu))
        if bu and sg:
            col_keys.append(("SG_TOTAL", bu, sg))
            subsg = subsg_for(sg, pkey) if pkey else sg
            if subsg != sg:
                col_keys.append(("SUBSG_TOTAL", bu, sg, subsg))
            if pkey:
                col_keys.append(("PRODUCT", bu, sg, subsg, pkey))

        for rk in row_keys:
            for ck in col_keys:
                totals[(rk, ck)] += value

    return dict(totals)


def apply_pivot_to_schema(pivot: dict, row_map: dict, col_map: dict) -> dict:
    """Filter pivot down to keys that appear in both maps, returning {(row_num, col_num): value}."""
    out = {}
    for (rk, ck), value in pivot.items():
        r = row_map.get(rk)
        c = col_map.get(ck)
        if r is None or c is None:
            continue
        out[(r, c)] = value
    return out
