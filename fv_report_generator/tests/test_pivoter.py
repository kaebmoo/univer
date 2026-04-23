"""Tests for the pivot builder using a tiny in-memory DataFrame."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.normalizer import canonical  # noqa: E402
from src.pivoter import build_pivot  # noqa: E402


def _fixture_df():
    return pd.DataFrame(
        [
            # revenue, hard infra / conduit
            dict(TIME_KEY=202514, GROUP="01.รายได้", SUB_GROUP1="01.รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน",
                 SUB_GROUP2=None, BU="1.กลุ่มธุรกิจ HARD INFRASTRUCTURE",
                 SERVICE_GROUP="1.1 กลุ่มบริการท่อร้อยสาย",
                 PRODUCT_NAME="บริการท่อร้อยสาย", PRODUCT_KEY="000000000181030004",
                 ALLIE="N", VALUE=100.0),
            # revenue, hard infra / dark fiber
            dict(TIME_KEY=202514, GROUP="01.รายได้", SUB_GROUP1="01.รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน",
                 SUB_GROUP2=None, BU="1.กลุ่มธุรกิจ HARD INFRASTRUCTURE",
                 SERVICE_GROUP="1.2 กลุ่มบริการ DARK FIBER",
                 PRODUCT_NAME="บริการโครงข่าย-Dark Fiber", PRODUCT_KEY="000000000181030006",
                 ALLIE="N", VALUE=50.0),
            # expense variable, hard infra / conduit, payroll
            dict(TIME_KEY=202514, GROUP="02.ค่าใช้จ่ายผันแปร", SUB_GROUP1="01.ต้นทุนบริการและต้นทุนขาย :",
                 SUB_GROUP2="01.ค่าใช้จ่ายตอบแทนแรงงาน", BU="1.กลุ่มธุรกิจ HARD INFRASTRUCTURE",
                 SERVICE_GROUP="1.1 กลุ่มบริการท่อร้อยสาย",
                 PRODUCT_NAME="บริการท่อร้อยสาย", PRODUCT_KEY="000000000181030004",
                 ALLIE="N", VALUE=-30.0),
            # different period (should be excluded)
            dict(TIME_KEY=202513, GROUP="01.รายได้", SUB_GROUP1="01.รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน",
                 SUB_GROUP2=None, BU="1.กลุ่มธุรกิจ HARD INFRASTRUCTURE",
                 SERVICE_GROUP="1.1 กลุ่มบริการท่อร้อยสาย",
                 PRODUCT_NAME="บริการท่อร้อยสาย", PRODUCT_KEY="000000000181030004",
                 ALLIE="N", VALUE=9999.0),
        ]
    )


def test_pivot_filters_by_period():
    p = build_pivot(_fixture_df(), period_key=202514)
    # Period 202513 row (9999) must not appear in any sum
    for v in p.values():
        assert 9999.0 not in (v,)


def test_pivot_aggregates_at_all_levels():
    p = build_pivot(_fixture_df(), period_key=202514)
    revenue = (canonical("01.รายได้"), None, None)
    bu = canonical("1.กลุ่มธุรกิจ HARD INFRASTRUCTURE")

    # Grand total revenue
    assert p[(revenue, ("GRAND_TOTAL",))] == pytest.approx(150.0)
    # BU-level total revenue
    assert p[(revenue, ("BU_TOTAL", bu))] == pytest.approx(150.0)
    # SG-level split
    sg_conduit = canonical("1.1 กลุ่มบริการท่อร้อยสาย")
    sg_dark = canonical("1.2 กลุ่มบริการ DARK FIBER")
    assert p[(revenue, ("SG_TOTAL", bu, sg_conduit))] == pytest.approx(100.0)
    assert p[(revenue, ("SG_TOTAL", bu, sg_dark))] == pytest.approx(50.0)
    # Product-level (5-tuple with subsg=sg)
    product_key = ("PRODUCT", bu, sg_conduit, sg_conduit, "181030004")
    assert p[(revenue, product_key)] == pytest.approx(100.0)


def test_pivot_includes_sub2_for_expenses():
    p = build_pivot(_fixture_df(), period_key=202514)
    section = canonical("02.ค่าใช้จ่ายผันแปร")
    sub1 = canonical("01.ต้นทุนบริการและต้นทุนขาย :")
    sub2 = canonical("01.ค่าใช้จ่ายตอบแทนแรงงาน")

    # Drilldown: section, sub1, sub2 all present
    assert p[((section, None, None), ("GRAND_TOTAL",))] == pytest.approx(-30.0)
    assert p[((section, sub1, None), ("GRAND_TOTAL",))] == pytest.approx(-30.0)
    assert p[((section, sub1, sub2), ("GRAND_TOTAL",))] == pytest.approx(-30.0)
