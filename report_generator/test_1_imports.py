#!/usr/bin/env python3
"""
Test Script 1: Import Test
Test if all modules can be imported successfully
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("Test 1: Import Modules")
print("="*60)

try:
    print("\n1. Testing core imports...")
    from src.report_generator import ReportBuilder, ReportConfig
    from src.report_generator import ReportType, PeriodType, DetailLevel
    print("   ✅ Core imports successful")
    
    print("\n2. Testing config creation...")
    config = ReportConfig(
        report_type="COSTTYPE",
        period_type="MTH",
        detail_level="BU_SG_PRODUCT"
    )
    print(f"   ✅ Config created: {config.report_type.value}")
    print(f"      - Period: {config.period_type.value}")
    print(f"      - Detail: {config.detail_level.value}")
    print(f"      - Thai: {config.report_type_thai}")
    
    print("\n3. Testing builder creation...")
    builder = ReportBuilder(config)
    print("   ✅ ReportBuilder created")
    
    print("\n4. Testing column builder...")
    print(f"   ✅ Column builder: {type(builder.column_builder).__name__}")
    
    print("\n5. Testing formatter...")
    print(f"   ✅ Formatter: {type(builder.formatter).__name__}")
    
    print("\n6. Testing all writers...")
    print(f"   ✅ Header writer: {type(builder.header_writer).__name__}")
    print(f"   ✅ Column header writer: {type(builder.column_header_writer).__name__}")
    print(f"   ✅ Data writer: {type(builder.data_writer).__name__}")
    print(f"   ✅ Remark writer: {type(builder.remark_writer).__name__}")
    
    print("\n" + "="*60)
    print("✅ ALL IMPORT TESTS PASSED!")
    print("="*60)
    
except Exception as e:
    print("\n" + "="*60)
    print("❌ IMPORT TEST FAILED!")
    print("="*60)
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
