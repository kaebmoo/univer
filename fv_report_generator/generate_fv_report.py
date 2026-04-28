#!/usr/bin/env python3
"""
FV Report Generator (data-driven) — produce a Report_P14-style Excel file
purely from the FV data-warehouse CSV. Row/column structure adapts to the
data: new products, removed products, new line items appear/disappear
automatically.

Usage:
    python generate_fv_report.py \\
        --csv-file /path/to/TRN_FV_Datawarehouse_Y2568(P14).csv \\
        --output output/Report_FV_P14.xlsx \\
        [--reconcile-against /path/to/Report_FV_*.XLSX]
"""
import argparse
import logging
import re
import sys
from pathlib import Path

from src.config import FVConfig
from src.data_loader import load_fv_csv
from src.reconciler import reconcile
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
        help="After writing, re-read the output workbook and verify each cell matches the source CSV.",
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

    if args.reconcile:
        log.info("reconciling output %s against source CSV", out_path)
        result = reconcile(out_path, df, config, period_key=period_key, sheet_name=args.sheet)
        if result.mismatches:
            log.warning("  %d cell mismatches (of %d checked)",
                        len(result.mismatches), result.cells_checked)
            for label, col_disp, act, exp, diff in result.mismatches[:10]:
                log.warning("    [%s] × [%s]: xlsx=%.2f csv=%.2f diff=%+.2f",
                            label, col_disp, act, exp, diff)
        else:
            log.info("  OK — %d cells verified, 0 mismatches", result.cells_checked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
