"""
Aggregator — pivot CSV (long format) into a flat dict
{(row_key, col_key): float} that reports everything from the data itself.

This is data-driven: the row hierarchy and column hierarchy come from CSV
contents, not from a fixed template. The output shape matches what the old
pivoter.py emitted, so reconciler.py keeps working.

Helpers `enumerate_*` are exposed so the column/row builders can walk the
unique BU / SG / SUBSG / PRODUCT / SECTION / SUB_GROUP combinations directly.
"""
from collections import OrderedDict, defaultdict
from typing import List, Optional, Tuple

import pandas as pd

from .normalizer import canonical, canonical_product_key
from .satellite_split import is_split_sg, subsg_for


# --- CSV section codes treated specially -------------------------------------
# CSV "33." is a per-product percentage already calculated; we do NOT sum it
# (percentages don't sum across rows). The display %กำไรส่วนเกิน row is
# recomputed from contribution margin / revenue per column instead.
_PERCENT_GROUP_PREFIX = "33."


def _strip_period(text: Optional[str]) -> Optional[str]:
    """Drop trailing ' :' or '.' so SUB_GROUP1 labels normalize cleanly."""
    if text is None:
        return None
    s = str(text).strip()
    if s.endswith(":"):
        s = s[:-1].rstrip()
    return s


def build_pivot(
    df: pd.DataFrame,
    period_key: Optional[int] = None,
) -> dict:
    """Aggregate VALUE per (row_key, col_key) for the given period.

    row_key shape: (section_canonical, sub1_canonical_or_None, sub2_canonical_or_None)
    col_key shape:
        ("GRAND_TOTAL",)
        ("BU_TOTAL", bu_canonical)
        ("SG_TOTAL", bu_canonical, sg_canonical)
        ("SUBSG_TOTAL", bu_canonical, sg_canonical, subsg_canonical)
        ("PRODUCT", bu_canonical, sg_canonical, subsg_canonical, pkey_canonical)
    """
    if period_key is not None:
        df = df[df["TIME_KEY"] == period_key]

    work = pd.DataFrame({
        "section_raw": df["GROUP"],
        "sub1_raw": df["SUB_GROUP1"],
        "sub2_raw": df["SUB_GROUP2"],
        "section": df["GROUP"].map(canonical),
        "sub1": df["SUB_GROUP1"].map(lambda x: canonical(_strip_period(x)) if pd.notna(x) else None),
        "sub2": df["SUB_GROUP2"].map(lambda x: canonical(x) if pd.notna(x) else None),
        "bu": df["BU"].map(canonical),
        "sg": df["SERVICE_GROUP"].map(lambda x: canonical(x) if pd.notna(x) else None),
        "pkey": df["PRODUCT_KEY"].map(canonical_product_key),
        "value": df["VALUE"].astype(float).fillna(0.0),
    })

    totals = defaultdict(float)
    for row in work.itertuples(index=False):
        # Skip percentage-group rows — they are not summable.
        section_raw = row.section_raw
        if isinstance(section_raw, str) and section_raw.lstrip().startswith(_PERCENT_GROUP_PREFIX):
            continue

        value = row.value
        if value == 0.0:
            continue

        section, sub1, sub2 = row.section, row.sub1, row.sub2
        row_keys = [(section, None, None)]
        if sub1:
            row_keys.append((section, sub1, None))
        if sub1 and sub2:
            row_keys.append((section, sub1, sub2))

        bu, sg, pkey = row.bu, row.sg, row.pkey
        col_keys: List[tuple] = [("GRAND_TOTAL",)]
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


# --- Enumeration helpers ------------------------------------------------------

def _sort_key(text: str) -> tuple:
    """Sort by leading numeric prefix, then by text. Handles '1.', '1.1', '01.', etc."""
    s = (text or "").strip().lstrip("0")
    parts = []
    head = ""
    i = 0
    while i < len(s) and (s[i].isdigit() or s[i] == "."):
        head += s[i]
        i += 1
    for piece in head.split("."):
        try:
            parts.append(int(piece))
        except (ValueError, TypeError):
            parts.append(0)
    return (tuple(parts), s)


def enumerate_bus(df: pd.DataFrame, period_key: Optional[int] = None) -> List[str]:
    """Distinct BU labels, sorted by numeric prefix."""
    if period_key is not None:
        df = df[df["TIME_KEY"] == period_key]
    bus = df["BU"].dropna().unique().tolist()
    return sorted(bus, key=_sort_key)


def enumerate_sgs(df: pd.DataFrame, bu: str, period_key: Optional[int] = None) -> List[str]:
    """Distinct SG labels for a BU, sorted by numeric prefix."""
    if period_key is not None:
        df = df[df["TIME_KEY"] == period_key]
    sgs = df[df["BU"] == bu]["SERVICE_GROUP"].dropna().unique().tolist()
    return sorted(sgs, key=_sort_key)


def enumerate_products(
    df: pd.DataFrame,
    bu: str,
    sg: str,
    period_key: Optional[int] = None,
    subsg_canon: Optional[str] = None,
) -> List[Tuple[str, str]]:
    """Return [(product_key_raw, product_name)] for the (BU, SG) pair, sorted by PRODUCT_KEY.

    If `subsg_canon` is given (for split SGs), only products whose canonical
    sub-SG matches are returned.
    """
    if period_key is not None:
        df = df[df["TIME_KEY"] == period_key]
    sub = df[(df["BU"] == bu) & (df["SERVICE_GROUP"] == sg)].copy()
    sub = sub[["PRODUCT_KEY", "PRODUCT_NAME"]].dropna(subset=["PRODUCT_KEY"])
    # Coerce to string so mixed int/str PRODUCT_KEYs sort consistently
    sub["PRODUCT_KEY"] = sub["PRODUCT_KEY"].apply(lambda x: str(x).strip())
    sub = sub.drop_duplicates().sort_values("PRODUCT_KEY")
    out = []
    for pkey, pname in sub.itertuples(index=False, name=None):
        if subsg_canon is not None:
            sg_c = canonical(sg)
            if subsg_for(sg_c, canonical_product_key(pkey)) != subsg_canon:
                continue
        out.append((str(pkey).strip(), str(pname).strip() if pd.notna(pname) else ""))
    return out


def enumerate_sections(df: pd.DataFrame, period_key: Optional[int] = None) -> List[str]:
    """Distinct GROUP labels (excluding percent group), sorted by numeric prefix."""
    if period_key is not None:
        df = df[df["TIME_KEY"] == period_key]
    sections = df["GROUP"].dropna().unique().tolist()
    sections = [s for s in sections if not str(s).lstrip().startswith(_PERCENT_GROUP_PREFIX)]
    return sorted(sections, key=_sort_key)


def enumerate_sub_groups(
    df: pd.DataFrame,
    section_raw: str,
    period_key: Optional[int] = None,
) -> "OrderedDict[str, List[str]]":
    """Return ordered {sub1_raw: [sub2_raw, ...]} for a section.

    Sub-groups (and their sub2 children) are sorted by numeric prefix.
    Sub-groups with no sub2 still appear (as empty list).
    """
    if period_key is not None:
        df = df[df["TIME_KEY"] == period_key]
    sub = df[df["GROUP"] == section_raw]
    grouped: "OrderedDict[str, List[str]]" = OrderedDict()
    sub1_values = sub["SUB_GROUP1"].dropna().unique().tolist()
    for s1 in sorted(sub1_values, key=_sort_key):
        sub2_values = sub[sub["SUB_GROUP1"] == s1]["SUB_GROUP2"].dropna().unique().tolist()
        grouped[s1] = sorted(sub2_values, key=_sort_key)
    return grouped


def is_subsg_split(sg_raw: str) -> bool:
    return is_split_sg(canonical(sg_raw))
