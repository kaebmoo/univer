"""
Column builder — enumerate BU/SG/SUBSG/PRODUCT columns from CSV and emit
ColumnDef objects that the writer + cell-lookup will use.

For SGs in the SATELLITE split (4.5), we emit an SG_TOTAL summary column
("รวม 4.5 SATELLITE") followed by per-sub-SG groups (4.5.1 + products,
4.5.2 + products). Other SGs are emitted as flat SG_TOTAL + product columns.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import pandas as pd

from . import aggregator
from .normalizer import canonical, canonical_product_key
from .satellite_split import (
    SATELLITE_GROUPS,
    is_split_sg,
)


@dataclass
class ColumnDef:
    """One column in the output.

    col_type ∈ {label, grand_total, bu_total, sg_total, subsg_total, product}.
    The col_key is the tuple used to look up values from the pivot dict.
    """
    col_type: str
    display_name: str = ""
    bu_raw: Optional[str] = None
    sg_raw: Optional[str] = None
    subsg_raw: Optional[str] = None
    product_key_raw: Optional[str] = None
    product_name: Optional[str] = None
    width: int = 16
    color: str = "FFFFFF"

    @property
    def col_key(self) -> Optional[tuple]:
        if self.col_type == "label":
            return None
        if self.col_type == "grand_total":
            return ("GRAND_TOTAL",)
        bu_c = canonical(self.bu_raw)
        if self.col_type == "bu_total":
            return ("BU_TOTAL", bu_c)
        sg_c = canonical(self.sg_raw)
        if self.col_type == "sg_total":
            return ("SG_TOTAL", bu_c, sg_c)
        subsg_c = canonical(self.subsg_raw) if self.subsg_raw else sg_c
        if self.col_type == "subsg_total":
            return ("SUBSG_TOTAL", bu_c, sg_c, subsg_c)
        if self.col_type == "product":
            return ("PRODUCT", bu_c, sg_c, subsg_c, canonical_product_key(self.product_key_raw))
        return None


def _strip_leading_zero(text: str) -> str:
    """'01.กลุ่ม...' -> '1.กลุ่ม...'; 'รวม 01.กลุ่ม...' -> 'รวม 1.กลุ่ม...'."""
    if not text:
        return text
    prefix = ""
    main = text
    if main.startswith("รวม "):
        prefix, main = "รวม ", main[4:]
    if len(main) >= 3 and main[0] == "0" and main[1].isdigit() and main[2] == ".":
        main = main[1:]
    return prefix + main


def _subsg_display_name(subsg_raw: str) -> str:
    return _strip_leading_zero(subsg_raw)


def build_columns(
    df: pd.DataFrame,
    config,
    period_key: Optional[int] = None,
) -> List[ColumnDef]:
    """Build the full ColumnDef sequence for the report."""
    cols: List[ColumnDef] = []

    # 1) Label
    cols.append(ColumnDef(
        col_type="label",
        display_name="รายละเอียด",
        width=config.label_width,
        color=config.label_header_color,
    ))

    # 2) Grand total
    cols.append(ColumnDef(
        col_type="grand_total",
        display_name="รวมทั้งสิ้น",
        width=config.data_col_width + 4,
        color=config.grand_total_color,
    ))

    # 3) Per BU
    bus = aggregator.enumerate_bus(df, period_key=period_key)
    for bu in bus:
        bu_color = config.bu_color(bu)
        cols.append(ColumnDef(
            col_type="bu_total",
            display_name=f"รวม {_strip_leading_zero(bu)}",
            bu_raw=bu,
            width=config.data_col_width,
            color=bu_color,
        ))

        sgs = aggregator.enumerate_sgs(df, bu, period_key=period_key)
        for sg in sgs:
            if is_split_sg(canonical(sg)):
                cols.extend(_build_split_sg_columns(df, bu, sg, bu_color, config, period_key))
            else:
                cols.extend(_build_flat_sg_columns(df, bu, sg, bu_color, config, period_key))

    return cols


def _build_flat_sg_columns(
    df: pd.DataFrame,
    bu: str,
    sg: str,
    bu_color: str,
    config,
    period_key: Optional[int],
) -> List[ColumnDef]:
    out: List[ColumnDef] = []
    out.append(ColumnDef(
        col_type="sg_total",
        display_name=f"รวม {_strip_leading_zero(sg)}",
        bu_raw=bu,
        sg_raw=sg,
        subsg_raw=sg,
        width=config.data_col_width,
        color=bu_color,
    ))
    products = aggregator.enumerate_products(df, bu, sg, period_key=period_key)
    for pkey, pname in products:
        out.append(ColumnDef(
            col_type="product",
            display_name=pname,
            bu_raw=bu,
            sg_raw=sg,
            subsg_raw=sg,
            product_key_raw=pkey,
            product_name=pname,
            width=config.data_col_width,
            color=bu_color,
        ))
    return out


def _build_split_sg_columns(
    df: pd.DataFrame,
    bu: str,
    sg: str,
    bu_color: str,
    config,
    period_key: Optional[int],
) -> List[ColumnDef]:
    """Emit summary + sub-SG groups for a split SG (e.g., 4.5)."""
    out: List[ColumnDef] = []

    # SG-level summary (sums all sub-SGs)
    out.append(ColumnDef(
        col_type="sg_total",
        display_name=f"รวม {_strip_leading_zero(sg)}",
        bu_raw=bu,
        sg_raw=sg,
        subsg_raw=sg,
        width=config.data_col_width,
        color=bu_color,
    ))

    # Iterate sub-SGs by their natural prefix order (4.5.1 before 4.5.2)
    subsg_names = sorted([g["name"] for g in SATELLITE_GROUPS.values()])
    for subsg in subsg_names:
        subsg_c = canonical(subsg)
        # SUBSG total
        out.append(ColumnDef(
            col_type="subsg_total",
            display_name=f"รวม {_subsg_display_name(subsg)}",
            bu_raw=bu,
            sg_raw=sg,
            subsg_raw=subsg,
            width=config.data_col_width,
            color=bu_color,
        ))
        # Products under this sub-SG
        products = aggregator.enumerate_products(
            df, bu, sg, period_key=period_key, subsg_canon=subsg_c,
        )
        for pkey, pname in products:
            out.append(ColumnDef(
                col_type="product",
                display_name=pname,
                bu_raw=bu,
                sg_raw=sg,
                subsg_raw=subsg,
                product_key_raw=pkey,
                product_name=pname,
                width=config.data_col_width,
                color=bu_color,
            ))
    return out
