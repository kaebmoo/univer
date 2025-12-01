#!/usr/bin/env python3
"""
Debug script to check CSV data for expense groups
"""
import pandas as pd

# Read CSV
csv_file = "/Users/seal/Documents/GitHub/univer/report_generator/data/TRN_PL_COSTTYPE_NT_YTD_TABLE_20251031.csv"
df = pd.read_csv(csv_file)

print(f"Total rows in CSV: {len(df)}")
print(f"\nColumns: {df.columns.tolist()}")

# Check for GROUP 02, 04, 06 with SUB_GROUP 01
groups_to_check = [
    ("02.ต้นทุนบริการและต้นทุนขาย :", "01.ค่าใช้จ่ายตอบแทนแรงงาน"),
    ("04.ค่าใช้จ่ายขายและการตลาด :", "01.ค่าใช้จ่ายตอบแทนแรงงาน"),
    ("06.ค่าใช้จ่ายบริหารและสนับสนุน :", "01.ค่าใช้จ่ายตอบแทนแรงงาน"),
]

for group, sub_group in groups_to_check:
    filtered = df[(df['GROUP'] == group) & (df['SUB_GROUP'] == sub_group)]
    total_value = filtered['VALUE'].sum()
    
    print(f"\n{'='*80}")
    print(f"GROUP: {group}")
    print(f"SUB_GROUP: {sub_group}")
    print(f"Number of rows: {len(filtered)}")
    print(f"Total VALUE: {total_value:,.2f}")
    
    if len(filtered) > 0:
        print(f"\nFirst 3 rows:")
        print(filtered[['GROUP', 'SUB_GROUP', 'BU', 'SERVICE_GROUP', 'VALUE']].head(3).to_string())
        
        # Show aggregation by BU
        print(f"\nAggregation by BU:")
        bu_summary = filtered.groupby('BU')['VALUE'].sum().sort_values(ascending=False)
        print(bu_summary.to_string())

print(f"\n{'='*80}")
print("Summary: Check if values are the same across all three groups")
print(f"{'='*80}")

# Compare totals
for group, sub_group in groups_to_check:
    filtered = df[(df['GROUP'] == group) & (df['SUB_GROUP'] == sub_group)]
    total_value = filtered['VALUE'].sum()
    print(f"{group:50s} Total: {total_value:>20,.2f}")
