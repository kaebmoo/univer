#!/usr/bin/env python3
"""
Test GLGROUP Report - BU+SG and BU+SG+Product levels
Verify that SG and Product columns now have data
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.cli.commands import generate_report
from config.types import ReportType, DetailLevel, PeriodType

print("="*70)
print("GLGROUP FIX TEST - BU+SG and BU+SG+Product")
print("="*70)

# Test BU+SG first
print("\n[1/2] Testing GLGROUP YTD BU+SG...")
print("-" * 70)

try:
    generate_report(
        csv_path="data/TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv",
        output_name="GLGROUP_FIX_BU_SG.xlsx",
        report_type=ReportType.GLGROUP,
        detail_level=DetailLevel.BU_SG,
        period_type=PeriodType.YTD
    )
    output_path = Path("output/GLGROUP_FIX_BU_SG.xlsx")
    if output_path.exists():
        size_kb = output_path.stat().st_size / 1024
        print(f"✅ SUCCESS: {output_path} ({size_kb:.1f} KB)")
    else:
        print(f"❌ FAILED: File not created")
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test BU+SG+Product
print("\n[2/2] Testing GLGROUP YTD BU+SG+Product...")
print("-" * 70)

try:
    generate_report(
        csv_path="data/TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv",
        output_name="GLGROUP_FIX_BU_SG_PRODUCT.xlsx",
        report_type=ReportType.GLGROUP,
        detail_level=DetailLevel.BU_SG_PRODUCT,
        period_type=PeriodType.YTD
    )
    output_path = Path("output/GLGROUP_FIX_BU_SG_PRODUCT.xlsx")
    if output_path.exists():
        size_kb = output_path.stat().st_size / 1024
        print(f"✅ SUCCESS: {output_path} ({size_kb:.1f} KB)")
    else:
        print(f"❌ FAILED: File not created")
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print("\nPlease check the output files:")
print("  1. output/GLGROUP_FIX_BU_SG.xlsx - should have data in SG columns")
print("  2. output/GLGROUP_FIX_BU_SG_PRODUCT.xlsx - should have data in Product columns")
