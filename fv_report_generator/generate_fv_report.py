#!/usr/bin/env python3
"""
FV Report Generator — produce a Report_P14-style Excel file from the FV
data-warehouse CSV extract.

Basic usage
    python generate_fv_report.py                 # auto-detect CSV + template
    python generate_fv_report.py \\
        --csv-file /path/to/TRN_FV_Datawarehouse_Y2568(P14).csv \\
        --template /path/to/Report_FV_Y2568(P14).XLSX \\
        --period-key 202514 \\
        --reconcile

The generator copies the template workbook, clears its data area, and fills in
freshly pivoted values. All header formatting, merged cells, fonts, and column
widths are preserved from the template.
"""
import argparse
import logging
import re
import sys
from pathlib import Path

from src.data_loader import load_fv_csv
from src.derived import compute_contribution_margin_percent
from src.pivoter import apply_pivot_to_schema, build_pivot
from src.reconciler import reconcile
from src.template_reader import read_template
from src.writer import write_report


_PERIOD_FROM_NAME = re.compile(r"Y(\d{4}).*?\(P?(\d{1,2})\)", re.IGNORECASE)


def infer_period_key(csv_path: Path) -> int | None:
    """Derive TIME_KEY (e.g. 202514) from filename like '...Y2568(P14).csv'.

    Filename uses Buddhist Era (BE); CSV TIME_KEY uses Gregorian (CE = BE - 543).
    """
    m = _PERIOD_FROM_NAME.search(csv_path.name)
    if not m:
        return None
    year = int(m.group(1))
    period = int(m.group(2))
    if year >= 2400:  # Buddhist Era → convert to Gregorian
        year -= 543
    return year * 100 + period


def main():
    parser = argparse.ArgumentParser(
        description="Generate an FV (Fixed/Variable cost) report Excel file from the data-warehouse CSV.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--csv-file", type=Path, required=True, help="Path to TRN_FV_Datawarehouse_*.csv")
    parser.add_argument("--template", type=Path, required=True, help="Path to Report_FV_*(P*).XLSX template")
    parser.add_argument("--output", type=Path, help="Output .xlsx (default: output/Report_FV_P<period>.xlsx)")
    parser.add_argument("--period-key", type=int, help="TIME_KEY to filter CSV (e.g. 202514). Auto-inferred from filename.")
    parser.add_argument("--sheet", default="Report_P14", help="Target sheet name (default: Report_P14)")
    parser.add_argument("--encoding", default="tis-620", help="CSV encoding (default: tis-620)")
    parser.add_argument("--reconcile", action="store_true", help="Cross-check pivot against Data_P14 sheet")
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
    if not args.template.exists():
        log.error("Template not found: %s", args.template)
        return 1

    period_key = args.period_key or infer_period_key(args.csv_file)
    if period_key is None:
        log.error("Could not infer --period-key from filename %s; pass it explicitly.", args.csv_file.name)
        return 1
    log.info("period_key = %s", period_key)

    if args.output is None:
        args.output = Path("output") / f"Report_FV_P{period_key % 100}.xlsx"

    log.info("loading CSV %s", args.csv_file)
    df = load_fv_csv(args.csv_file, encoding=args.encoding)
    log.info("  %d rows loaded", len(df))

    log.info("reading template %s", args.template)
    schema = read_template(args.template, sheet_name=args.sheet)
    log.info("  %d template rows / %d template cols mapped", len(schema.data_rows), len(schema.col_map))

    log.info("building pivot")
    pivot = build_pivot(df, period_key=period_key, col_map=schema.col_map)

    if args.reconcile:
        log.info("reconciling against Data_P14")
        result = reconcile(args.template, pivot)
        if result.mismatches:
            log.warning("  %d value mismatches vs Data_P14", len(result.mismatches))
            for rk, ck, pv, dv, diff in result.mismatches[:10]:
                log.warning("    %s × %s: pivot=%.2f data=%.2f diff=%+.2f", rk, ck, pv, dv, diff)
        else:
            log.info("  0 value mismatches")
        log.info("  %d pivot-only keys, %d data-only keys (likely header-label mismatches)",
                 len(result.csv_only), len(result.data_only))

    cells = apply_pivot_to_schema(pivot, schema.row_map, schema.col_map)
    compute_contribution_margin_percent(cells, schema)
    log.info("writing %d cells → %s", len(cells), args.output)
    path = write_report(args.template, args.output, cells, schema, sheet_name=args.sheet)
    log.info("done: %s (%.1f KB)", path, path.stat().st_size / 1024)
    return 0


if __name__ == "__main__":
    sys.exit(main())
