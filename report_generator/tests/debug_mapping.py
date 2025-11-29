#!/usr/bin/env python3
"""
Debug GLGROUP Data Mapping
Find out why get_row_data_glgroup returns empty
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data_loader import CSVLoader, DataProcessor
from config.data_mapping_glgroup import get_group_sub_group_glgroup

print("="*70)
print("GLGROUP DATA MAPPING DEBUG")
print("="*70)

# Load data
csv_path = project_root / "data" / "TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv"
loader = CSVLoader()
df = loader.load_csv(csv_path)

processor = DataProcessor()
df = processor.process_data(df)

print(f"\n📊 Loaded {len(df)} rows")

# Check unique GROUPs
print("\n🔍 Unique GROUP values in data:")
unique_groups = df['GROUP'].unique()
for g in sorted(unique_groups):
    count = len(df[df['GROUP'] == g])
    print(f"  {g} ({count} rows)")

# Test label mapping
test_labels = [
    "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน",
    "1 รวมรายได้",
    "2 รวมค่าใช้จ่าย",
    "3.กำไร(ขาดทุน)ก่อนหักภาษีเงินได้ (EBT) (1)-(2)",
]

print("\n🔍 Testing label mappings:")
for label in test_labels:
    group, sub_group = get_group_sub_group_glgroup(label)
    print(f"\n  Label: {label}")
    print(f"  → GROUP: {group}")
    print(f"  → SUB_GROUP: {sub_group}")
    
    if group:
        # Check if this GROUP exists in data
        matching = df[df['GROUP'] == group]
        print(f"  → Rows in data: {len(matching)}")
        
        if sub_group:
            matching_sub = matching[matching['SUB_GROUP'] == sub_group]
            print(f"  → Rows with SUB_GROUP: {len(matching_sub)}")
            
            if len(matching_sub) > 0:
                print(f"  ✅ Data found!")
                sample = matching_sub.head(1)
                print(f"  Sample: BU={sample.iloc[0]['BU']}, VALUE={sample.iloc[0]['VALUE']}")
            else:
                print(f"  ❌ No matching data!")
                # Show what SUB_GROUPs exist for this GROUP
                if len(matching) > 0:
                    actual_subs = matching['SUB_GROUP'].unique()
                    print(f"  Available SUB_GROUPs for {group}:")
                    for s in sorted(actual_subs)[:5]:
                        print(f"    - {s}")
    else:
        print(f"  ❌ No mapping found!")

print("\n" + "="*70)
