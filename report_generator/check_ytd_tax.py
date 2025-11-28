#!/usr/bin/env python3
"""Check YTD data for tax"""
import pandas as pd

csv_path = "data/TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv"
df = pd.read_csv(csv_path, encoding='tis-620')

print(f"📊 Total rows: {len(df)}")
print(f"\n🔍 Unique GROUPs:")
for group in sorted(df['GROUP'].unique()):
    count = len(df[df['GROUP'] == group])
    print(f"  - {group} ({count} rows)")

# Check for tax
tax_data = df[df['GROUP'].str.contains('ภาษี', na=False)]
print(f"\n💰 Tax data (GROUP contains 'ภาษี'):")
if len(tax_data) > 0:
    print(f"  Found {len(tax_data)} rows")
    print(f"  Sample:")
    print(tax_data[['GROUP', 'SUB_GROUP', 'VALUE']].head(3))
else:
    print(f"  No tax data found in any GROUP")

# Check GROUP 04
group_04 = df[df['GROUP'].str.startswith('04', na=False)]
print(f"\n🔍 GROUP 04 data:")
if len(group_04) > 0:
    print(f"  Found {len(group_04)} rows")
    print(f"  Unique SUB_GROUPs: {group_04['SUB_GROUP'].unique()}")
else:
    print(f"  No GROUP 04 found")
