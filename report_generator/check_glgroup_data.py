#!/usr/bin/env python3
"""Quick check GLGROUP data structure"""
import pandas as pd
from pathlib import Path

csv_path = Path("data/TRN_PL_GLGROUP_NT_MTH_TABLE_20251031.csv")

print(f"Reading: {csv_path}")
df = pd.read_csv(csv_path, encoding='tis-620', nrows=10)

print(f"\n📊 Columns ({len(df.columns)}):")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:2d}. {col}")

print(f"\n📋 Sample Data (first 3 rows):")
print(df.head(3)[['GROUP', 'SUB_GROUP', 'BU', 'SERVICE_GROUP', 'VALUE']].to_string())

print(f"\n🔍 Unique GROUPs:")
for group in sorted(df['GROUP'].unique()):
    count = len(df[df['GROUP'] == group])
    print(f"  - {group} ({count} rows)")

print(f"\n🔍 Sample SUB_GROUPs for GROUP='1':")
group_1 = df[df['GROUP'] == '1']['SUB_GROUP'].unique()
for sg in list(group_1)[:5]:
    print(f"  - {sg}")
