#!/usr/bin/env python3
"""
Quick Test Script for Common Size Feature
ทดสอบว่า Common Size ทำงานได้ถูกต้อง
"""
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from src.report_generator.core.config import ReportConfig

def test_common_size_config():
    """Test Common Size configuration"""
    print("=" * 70)
    print("🧪 Testing Common Size Configuration")
    print("=" * 70)
    
    # Test 1: BU_ONLY default (should be True)
    print("\n1️⃣ Test BU_ONLY (default should enable common size)")
    config1 = ReportConfig(
        report_type="COSTTYPE",
        period_type="MTH",
        detail_level="BU_ONLY"
    )
    print(f"   include_common_size: {config1.include_common_size}")
    assert config1.include_common_size == True, "❌ FAILED: BU_ONLY should have common_size=True"
    print("   ✅ PASSED")
    
    # Test 2: BU_SG default (should be False)
    print("\n2️⃣ Test BU_SG (default should disable common size)")
    config2 = ReportConfig(
        report_type="COSTTYPE",
        period_type="MTH",
        detail_level="BU_SG"
    )
    print(f"   include_common_size: {config2.include_common_size}")
    assert config2.include_common_size == False, "❌ FAILED: BU_SG should have common_size=False"
    print("   ✅ PASSED")
    
    # Test 3: Explicit override (Force True for BU_SG)
    print("\n3️⃣ Test explicit override (force True for BU_SG)")
    config3 = ReportConfig(
        report_type="COSTTYPE",
        period_type="MTH",
        detail_level="BU_SG",
        include_common_size=True
    )
    print(f"   include_common_size: {config3.include_common_size}")
    assert config3.include_common_size == True, "❌ FAILED: Explicit override should work"
    print("   ✅ PASSED")
    
    # Test 4: Force disable for BU_ONLY
    print("\n4️⃣ Test force disable (--no-common-size for BU_ONLY)")
    config4 = ReportConfig(
        report_type="COSTTYPE",
        period_type="MTH",
        detail_level="BU_ONLY",
        include_common_size=False
    )
    print(f"   include_common_size: {config4.include_common_size}")
    assert config4.include_common_size == False, "❌ FAILED: Force disable should work"
    print("   ✅ PASSED")
    
    # Test 5: GLGROUP BU_ONLY (should also work)
    print("\n5️⃣ Test GLGROUP BU_ONLY")
    config5 = ReportConfig(
        report_type="GLGROUP",
        period_type="YTD",
        detail_level="BU_ONLY"
    )
    print(f"   include_common_size: {config5.include_common_size}")
    assert config5.include_common_size == True, "❌ FAILED: GLGROUP BU_ONLY should have common_size=True"
    print("   ✅ PASSED")
    
    print("\n" + "=" * 70)
    print("✅ All Configuration Tests PASSED!")
    print("=" * 70)


def test_column_builder():
    """Test that column builder creates common size columns"""
    print("\n" + "=" * 70)
    print("🧪 Testing Column Builder")
    print("=" * 70)
    
    from src.report_generator.columns.bu_only_builder import BUOnlyBuilder
    from src.data_loader import CSVLoader, DataProcessor
    
    # Load sample data
    data_file = Path("data/TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv")
    if not data_file.exists():
        print(f"⚠️  Skip: Data file not found: {data_file}")
        return
    
    csv_loader = CSVLoader(encoding='tis-620')
    df = csv_loader.load_csv(data_file)
    data_processor = DataProcessor()
    df = data_processor.process_data(df)
    
    # Test with common size enabled
    print("\n1️⃣ Test BU_ONLY with common_size=True")
    config_with = ReportConfig(
        report_type="COSTTYPE",
        period_type="MTH",
        detail_level="BU_ONLY",
        include_common_size=True
    )
    builder_with = BUOnlyBuilder(config_with)
    columns_with = builder_with.build_columns(df)
    
    common_size_cols = [c for c in columns_with if c.col_type == 'common_size']
    print(f"   Total columns: {len(columns_with)}")
    print(f"   Common Size columns: {len(common_size_cols)}")
    assert len(common_size_cols) > 0, "❌ FAILED: Should have common_size columns"
    print("   ✅ PASSED")
    
    # Test without common size
    print("\n2️⃣ Test BU_ONLY with common_size=False")
    config_without = ReportConfig(
        report_type="COSTTYPE",
        period_type="MTH",
        detail_level="BU_ONLY",
        include_common_size=False
    )
    builder_without = BUOnlyBuilder(config_without)
    columns_without = builder_without.build_columns(df)
    
    common_size_cols_2 = [c for c in columns_without if c.col_type == 'common_size']
    print(f"   Total columns: {len(columns_without)}")
    print(f"   Common Size columns: {len(common_size_cols_2)}")
    assert len(common_size_cols_2) == 0, "❌ FAILED: Should NOT have common_size columns"
    print("   ✅ PASSED")
    
    print("\n" + "=" * 70)
    print("✅ All Column Builder Tests PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_common_size_config()
        test_column_builder()
        
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print("\n📝 Next Steps:")
        print("   1. Run actual report generation:")
        print("      python generate_report.py --detail-level BU_ONLY")
        print("\n   2. Verify output Excel file:")
        print("      - Check Common Size columns exist")
        print("      - Check values are percentages")
        print("      - Check negative values show as (42.00%) in red")
        print("      - Check zero values are blank")
        print("\n   3. Test edge cases:")
        print("      - สัดส่วนต่อรายได้ rows should NOT have common size")
        print("      - Both COSTTYPE and GLGROUP should work")
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
