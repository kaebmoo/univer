"""End-to-end integration: generate report from CSV → re-read xlsx → verify all cells.

Skipped if the real CSV is not available in this environment.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.aggregator import build_pivot  # noqa: E402
from src.config import FVConfig  # noqa: E402
from src.data_loader import load_fv_csv  # noqa: E402
from src.reconciler import reconcile  # noqa: E402
from src.report_builder import generate_report  # noqa: E402


CSV = Path("/Users/seal/Documents/NT/Report/vcfc/TRN_FV_Datawarehouse_Y2568(P14).csv")


pytestmark = pytest.mark.skipif(
    not CSV.exists(),
    reason="real P14 CSV not available in this environment",
)


def test_generated_xlsx_matches_csv(tmp_path):
    df = load_fv_csv(CSV)
    config = FVConfig(period_year_be=2568, period_label="P14 test")
    out = tmp_path / "Report_FV_test.xlsx"
    generate_report(df, out, config, period_key=202514, sheet_name="Report_FV")

    result = reconcile(out, df, config, period_key=202514, sheet_name="Report_FV")
    assert not result.mismatches, (
        f"{len(result.mismatches)} cell mismatches of {result.cells_checked} checked; "
        f"first: {result.mismatches[0]}"
    )
    assert result.cells_checked > 0


def test_known_pivot_values():
    """Spot-check totals against expected Dec-2568 P14 values."""
    df = load_fv_csv(CSV)
    pivot = build_pivot(df, period_key=202514)

    from src.normalizer import canonical  # noqa: E402

    revenue = (canonical("1. รายได้"), None, None)

    # Total revenue (รวมทั้งสิ้น)
    assert abs(pivot[(revenue, ("GRAND_TOTAL",))] - 3_293_263_821.16) < 0.01

    # Hard Infrastructure BU revenue
    bu = canonical("1.กลุ่มธุรกิจ HARD INFRASTRUCTURE")
    assert abs(pivot[(revenue, ("BU_TOTAL", bu))] - 779_969_240.54) < 0.01
