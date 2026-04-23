"""End-to-end integration: CSV pivot vs Data_P14 sheet.

Requires the real P14 template and CSV to be present at the NT/Report/vcfc path.
Skipped if either file is missing so the suite still runs in other environments.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_loader import load_fv_csv  # noqa: E402
from src.pivoter import build_pivot  # noqa: E402
from src.reconciler import reconcile  # noqa: E402
from src.template_reader import read_template  # noqa: E402


TEMPLATE = Path("/Users/seal/Documents/NT/Report/vcfc/Report_FV_Y2568(P14).XLSX")
CSV = Path("/Users/seal/Documents/NT/Report/vcfc/TRN_FV_Datawarehouse_Y2568(P14).csv")


pytestmark = pytest.mark.skipif(
    not (TEMPLATE.exists() and CSV.exists()),
    reason="real P14 template or CSV not available in this environment",
)


def test_pivot_has_no_value_mismatches_vs_data_p14():
    df = load_fv_csv(CSV)
    schema = read_template(TEMPLATE)
    pivot = build_pivot(df, period_key=202514, col_map=schema.col_map)
    result = reconcile(TEMPLATE, pivot)
    assert not result.mismatches, f"{len(result.mismatches)} value mismatches (see reconciler output)"


def test_known_cell_values():
    """Spot-check a handful of cells against values observed in the Dec-2568 P14 template."""
    df = load_fv_csv(CSV)
    schema = read_template(TEMPLATE)
    pivot = build_pivot(df, period_key=202514, col_map=schema.col_map)

    from src.normalizer import canonical  # noqa: E402

    revenue = (canonical("1. รายได้"), None, None)

    # Total revenue (รวมทั้งสิ้น)
    assert abs(pivot[(revenue, ("GRAND_TOTAL",))] - 3_293_263_821.16) < 0.01

    # Hard Infrastructure BU revenue
    bu = canonical("1.กลุ่มธุรกิจ HARD INFRASTRUCTURE")
    assert abs(pivot[(revenue, ("BU_TOTAL", bu))] - 779_969_240.54) < 0.01
