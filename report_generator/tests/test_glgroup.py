#!/usr/bin/env python3
"""
Test GLGROUP Report Generation
Tests all 3 detail levels with both MTH and YTD data
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.cli.commands import generate_report
from config.types import ReportType, DetailLevel, PeriodType

print("="*70)
print("GLGROUP REPORT GENERATION TEST")
print("="*70)

# Test cases
test_cases = [
    {
        "name": "GLGROUP MTH - BU Only",
        "csv_path": "data/TRN_PL_GLGROUP_NT_MTH_TABLE_20251031.csv",
        "report_type": ReportType.GLGROUP,
        "detail_level": DetailLevel.BU_ONLY,
        "period_type": PeriodType.MTH,
        "output_name": "GLGROUP_MTH_BU_ONLY.xlsx"
    },
    {
        "name": "GLGROUP MTH - BU + SG",
        "csv_path": "data/TRN_PL_GLGROUP_NT_MTH_TABLE_20251031.csv",
        "report_type": ReportType.GLGROUP,
        "detail_level": DetailLevel.BU_SG,
        "period_type": PeriodType.MTH,
        "output_name": "GLGROUP_MTH_BU_SG.xlsx"
    },
    {
        "name": "GLGROUP MTH - BU + SG + Products",
        "csv_path": "data/TRN_PL_GLGROUP_NT_MTH_TABLE_20251031.csv",
        "report_type": ReportType.GLGROUP,
        "detail_level": DetailLevel.BU_SG_PRODUCT,
        "period_type": PeriodType.MTH,
        "output_name": "GLGROUP_MTH_BU_SG_PRODUCT.xlsx"
    },
    {
        "name": "GLGROUP YTD - BU Only",
        "csv_path": "data/TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv",
        "report_type": ReportType.GLGROUP,
        "detail_level": DetailLevel.BU_ONLY,
        "period_type": PeriodType.YTD,
        "output_name": "GLGROUP_YTD_BU_ONLY.xlsx"
    },
    {
        "name": "GLGROUP YTD - BU + SG",
        "csv_path": "data/TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv",
        "report_type": ReportType.GLGROUP,
        "detail_level": DetailLevel.BU_SG,
        "period_type": PeriodType.YTD,
        "output_name": "GLGROUP_YTD_BU_SG.xlsx"
    },
    {
        "name": "GLGROUP YTD - BU + SG + Products",
        "csv_path": "data/TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv",
        "report_type": ReportType.GLGROUP,
        "detail_level": DetailLevel.BU_SG_PRODUCT,
        "period_type": PeriodType.YTD,
        "output_name": "GLGROUP_YTD_BU_SG_PRODUCT.xlsx"
    }
]

# Run tests
results = []
for i, test in enumerate(test_cases, 1):
    print(f"\n[{i}/{len(test_cases)}] {test['name']}")
    print("-" * 70)
    
    try:
        generate_report(
            csv_path=test['csv_path'],
            output_name=test['output_name'],
            report_type=test['report_type'],
            detail_level=test['detail_level'],
            period_type=test['period_type']
        )
        
        output_path = Path("output") / test['output_name']
        if output_path.exists():
            size_kb = output_path.stat().st_size / 1024
            print(f"✅ SUCCESS: {output_path} ({size_kb:.1f} KB)")
            results.append((test['name'], True, None))
        else:
            print(f"❌ FAILED: Output file not found")
            results.append((test['name'], False, "File not created"))
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results.append((test['name'], False, str(e)))

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)

passed = sum(1 for _, success, _ in results if success)
failed = len(results) - passed

for name, success, error in results:
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {name}")
    if error:
        print(f"   Error: {error}")

print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed}")

if failed == 0:
    print("\n🎉 ALL TESTS PASSED!")
else:
    print(f"\n⚠️  {failed} test(s) failed")
    sys.exit(1)
