#!/usr/bin/env python3
"""
Test GLGROUP Data Loading - Phase 1
Just test if we can load GLGROUP data successfully
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("GLGROUP Data Loading Test")
print("="*70)

try:
    from src.data_loader import CSVLoader, DataProcessor, DataAggregator
    from config.data_mapping_glgroup import get_group_sub_group_glgroup
    
    # Load GLGROUP data
    csv_path = Path("data/TRN_PL_GLGROUP_NT_MTH_TABLE_20251031.csv")
    
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        sys.exit(1)
    
    print(f"\n📁 Loading: {csv_path.name}")
    
    csv_loader = CSVLoader(encoding='tis-620')
    df = csv_loader.load_csv(csv_path)
    
    processor = DataProcessor()
    df = processor.process_data(df)
    
    print(f"✅ Data loaded: {len(df)} rows")
    print(f"\n📊 Columns: {list(df.columns)}")
    
    # Check GROUPs
    print(f"\n🔍 Unique GROUPs:")
    for group in sorted(df['GROUP'].unique()):
        count = len(df[df['GROUP'] == group])
        print(f"  GROUP {group}: {count} rows")
    
    # Test mapping
    print(f"\n🗺️  Testing GLGROUP Mapping:")
    test_labels = [
        "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน",
        "- ค่าใช้จ่ายตอบแทนแรงงาน",
        "3.กำไร(ขาดทุน)ก่อนหักภาษีเงินได้ (EBT) (1)-(2)",
        "4.ภาษีเงินได้นิติบุคคล"
    ]
    
    for label in test_labels:
        group, sub_group = get_group_sub_group_glgroup(label)
        if group:
            print(f"  ✅ '{label[:40]}...' → GROUP={group}, SUB_GROUP={sub_group[:30]}...")
        else:
            print(f"  ❌ '{label}' → NOT MAPPED")
    
    # Test aggregator
    print(f"\n🔧 Testing DataAggregator:")
    aggregator = DataAggregator(df)
    
    # Get BU list
    bu_list = processor.get_unique_business_units(df)
    print(f"  Business Units: {len(bu_list)} units")
    print(f"  Sample BUs: {bu_list[:3]}")
    
    # Try to get data for a revenue row
    print(f"\n📊 Testing Data Retrieval (will use COSTTYPE logic for now):")
    label = "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน"
    try:
        # This will fail because it uses MAIN_GROUP logic
        # But we want to see the error
        row_data = aggregator.get_row_data(
            label,
            "1 รวมรายได้",  # dummy main group
            bu_list,
            {}
        )
        print(f"  ⚠️  Got data (unexpected): {len(row_data)} columns")
    except Exception as e:
        print(f"  ⚠️  Expected error (COSTTYPE logic): {str(e)[:60]}...")
    
    print("\n" + "="*70)
    print("✅ DATA LOADING TEST PASSED")
    print("="*70)
    print("\nNext steps:")
    print("1. Add get_row_data_glgroup() to DataAggregator")
    print("2. Update data_writer.py to use GLGROUP methods")
    print("3. Test full report generation")
    
except Exception as e:
    print("\n" + "="*70)
    print("❌ TEST FAILED")
    print("="*70)
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
