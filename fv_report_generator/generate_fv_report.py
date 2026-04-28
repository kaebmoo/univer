#!/usr/bin/env python3
"""
FV Report Generator (data-driven) — produce a Report_P14-style Excel file
purely from the FV data-warehouse CSV. Row/column structure adapts to the
data: new products, removed products, new line items appear/disappear
automatically.

Usage:
    # Generate + run ALL verification checks
    python generate_fv_report.py \\
        --csv-file /path/to/TRN_FV_Datawarehouse_Y2568(P14).csv \\
        --output output/Report_FV_P14.xlsx \\
        --reconcile

    # Generate + run invariant-only check (no .xlsx needed)
    python generate_fv_report.py \\
        --csv-file /path/to/TRN_FV_Datawarehouse_Y2568(P14).csv \\
        --reconcile-invariants

Verification layers when --reconcile is used:
  1. Cell-by-cell: every data cell in .xlsx vs pivot recomputed from CSV
  2. Invariant A:  GRAND_TOTAL == Σ BU_TOTAL == Σ SG_TOTAL == Σ PRODUCT
  3. Invariant B:  raw CSV groupby-sum matches pivot per section
  4. Invariant C:  %%กำไรส่วนเกิน formula verified independently
  5. Business rule: CM_xlsx = Revenue_xlsx − VarCost_xlsx  (reads xlsx directly)
"""
import argparse
import logging
import re
import sys
from pathlib import Path

from src.config import FVConfig
from src.data_loader import load_fv_csv
from src.reconciler import reconcile, reconcile_business_rules, reconcile_invariants
from src.report_builder import generate_report


_PERIOD_FROM_NAME = re.compile(r"Y(\d{4}).*?\(P?(\d{1,2})\)", re.IGNORECASE)

_THAI_MONTHS = [
    "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม",
]


def infer_period_key(csv_path: Path):
    m = _PERIOD_FROM_NAME.search(csv_path.name)
    if not m:
        return None, None
    year_be = int(m.group(1))
    period = int(m.group(2))
    year_ce = year_be - 543 if year_be >= 2400 else year_be
    return year_ce * 100 + period, year_be


def _period_label(year_be: int, period: int) -> str:
    """Format the row-3 period label, e.g.:
    'ประจำเดือน ธันวาคม  2568   (ก่อนผู้สอบบัญชีรับรอง_งวด 14)'
    Period 1..12 = the month directly. Period 13 = year-end. Period 14 = audit close.
    """
    if 1 <= period <= 12:
        return f"ประจำเดือน {_THAI_MONTHS[period]}  {year_be}   (งวด {period})"
    if period == 13:
        return f"งวดสะสม 12 เดือน  {year_be}   (งวด {period})"
    return f"ประจำเดือน ธันวาคม  {year_be}   (ก่อนผู้สอบบัญชีรับรอง_งวด {period})"


def main():
    parser = argparse.ArgumentParser(
        description="Generate the FV (Fixed/Variable cost) report from a data-warehouse CSV.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--csv-file", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--period-key", type=int, help="TIME_KEY (e.g. 202514). Auto-inferred from filename.")
    parser.add_argument("--encoding", default="tis-620")
    parser.add_argument(
        "--reconcile",
        action="store_true",
        help=(
            "After writing, run ALL verification checks: "
            "(1) cell-by-cell comparison of .xlsx vs CSV, "
            "(2) hierarchical-total invariants, "
            "(3) raw-CSV cross-check, "
            "(4) percent-row formula."
        ),
    )
    parser.add_argument(
        "--reconcile-invariants",
        action="store_true",
        dest="reconcile_invariants",
        help=(
            "Run invariant checks on the aggregation pipeline only (no .xlsx needed). "
            "Checks hierarchy totals, raw CSV sums, and percent formula."
        ),
    )
    parser.add_argument(
        "--reconcile-rules",
        action="store_true",
        dest="reconcile_rules",
        help=(
            "Verify accounting identities directly in the .xlsx (no CSV reference): "
            "CM = Revenue − Variable Cost per column."
        ),
    )
    parser.add_argument("--sheet", default="Report_FV", help="Output sheet name (default: Report_FV)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s %(message)s",
    )
    log = logging.getLogger("fv_report")

    if not args.csv_file.exists():
        log.error("CSV not found: %s", args.csv_file)
        return 1

    period_key = args.period_key
    year_be = None
    if period_key is None:
        period_key, year_be = infer_period_key(args.csv_file)
    if period_key is None:
        log.error("Could not infer --period-key from filename %s; pass it explicitly.", args.csv_file.name)
        return 1
    period_num = period_key % 100
    if year_be is None:
        year_ce = period_key // 100
        year_be = year_ce + 543

    if args.output is None:
        args.output = Path("output") / f"Report_FV_P{period_num}.xlsx"

    config = FVConfig(
        period_year_be=year_be,
        period_label=_period_label(year_be, period_num),
    )

    log.info("loading CSV %s", args.csv_file)
    df = load_fv_csv(args.csv_file, encoding=args.encoding)
    log.info("  %d rows", len(df))

    log.info("generating report (period_key=%s)", period_key)
    out_path, pivot = generate_report(
        df, args.output, config, period_key=period_key, sheet_name=args.sheet,
    )
    log.info("done: %s", out_path)

    failed = False

    # ------------------------------------------------------------------
    # Invariant checks — run before cell check so CSV bugs surface first
    # ------------------------------------------------------------------
    if args.reconcile or args.reconcile_invariants:
        log.info("running invariant checks on aggregation pipeline…")
        inv = reconcile_invariants(df, period_key=period_key)
        if inv.ok:
            log.info("  [invariants] OK — %d checks passed", inv.checks_run)
        else:
            failed = True
            log.warning("  [invariants] %d violation(s) in %d checks:",
                        len(inv.violations), inv.checks_run)
            for v in inv.violations:
                log.warning("    [%s] %s: got=%.4f expected=%.4f diff=%+.4f",
                            v.layer, v.description, v.got, v.expected, v.diff)

    # ------------------------------------------------------------------
    # Cell-by-cell check — requires the .xlsx to exist
    # ------------------------------------------------------------------
    if args.reconcile:
        log.info("reconciling output %s against source CSV (cell-by-cell)…", out_path)
        result = reconcile(out_path, df, config, period_key=period_key, sheet_name=args.sheet)
        if result.mismatches:
            failed = True
            log.warning("  [cell-check] %d cell mismatches (of %d checked)",
                        len(result.mismatches), result.cells_checked)
            for label, col_disp, act, exp, diff in result.mismatches[:20]:
                log.warning("    row=%-40s col=%-30s xlsx=%12.2f csv=%12.2f diff=%+.2f",
                            label, col_disp, act, exp, diff)
            if len(result.mismatches) > 20:
                log.warning("    … and %d more (use -v to see all)",
                            len(result.mismatches) - 20)
        else:
            log.info("  [cell-check] OK — %d cells verified, 0 mismatches",
                     result.cells_checked)

    # ------------------------------------------------------------------
    # Business-rule check — reads xlsx directly, trusts neither pivot nor CSV
    # ------------------------------------------------------------------
    if args.reconcile or args.reconcile_rules:
        log.info("running business-rule checks on .xlsx…")
        br = reconcile_business_rules(
            out_path, df, config, period_key=period_key, sheet_name=args.sheet
        )
        if br.skipped_sections:
            log.warning("  [biz-rules] skipped — sections not found: %s",
                        br.skipped_sections)
        elif br.ok:
            log.info("  [biz-rules] OK — %d checks passed (CM = Revenue − VarCost)",
                     br.checks_run)
        else:
            failed = True
            log.warning("  [biz-rules] %d violation(s) in %d checks:",
                        len(br.violations), br.checks_run)
            for v in br.violations:
                log.warning("    [%s] col=%s  diff=%+.2f", v.rule, v.col_display, v.diff)
                if v.detail:
                    log.warning("      %s", v.detail)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
