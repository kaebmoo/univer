#!/usr/bin/env python3
"""
Quick Test - Generate one GLGROUP report
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.cli.commands import generate_report
from config.types import ReportType, DetailLevel, PeriodType

print("Generating GLGROUP YTD BU_ONLY report...")

try:
    generate_report(
        csv_path="data/TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv",
        output_name="GLGROUP_QUICK_TEST.xlsx",
        report_type=ReportType.GLGROUP,
        detail_level=DetailLevel.BU_ONLY,
        period_type=PeriodType.YTD
    )
    print("✅ Report generated: output/GLGROUP_QUICK_TEST.xlsx")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
