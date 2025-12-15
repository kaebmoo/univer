#!/usr/bin/env python3
"""Test if GLGROUP data rows have satellite summary keys"""
import pandas as pd
from pathlib import Path
from src.data_loader import CSVLoader, DataProcessor, DataAggregator

# Load GLGROUP data
loader = CSVLoader(encoding='tis-620')
csv_path = Path('data/TRN_PL_GLGROUP_NT_YTD_TABLE_SAT_20251031.csv')

if not csv_path.exists():
    print(f"CSV not found: {csv_path}")
    exit(1)

df = loader.load_csv(csv_path)
processor = DataProcessor()
df = processor.process_data(df)

# Build aggregator
aggregator = DataAggregator(df)

# Get BU list and service_group_dict
bu_list = processor.get_unique_business_units(df)
service_group_dict = {}
for bu in bu_list:
    service_group_dict[bu] = processor.get_unique_service_groups(df, bu)

# Test a data row
print("Testing data row: '- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์'")
print("="*80)

row_data = aggregator.get_row_data_glgroup(
    "- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์",
    bu_list,
    service_group_dict
)

# Check for SATELLITE keys
bu = "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND"
from config.satellite_config import SATELLITE_SUMMARY_ID, get_satellite_service_group_names

satellite_sgs = get_satellite_service_group_names()
print(f"\nSatellite service groups: {satellite_sgs}")
print(f"Satellite summary ID: {SATELLITE_SUMMARY_ID}")
print()

# Check detail SG keys
for sg in satellite_sgs:
    key = f"SG_TOTAL_{bu}_{sg}"
    if key in row_data:
        print(f"✓ Found SG key '{key}': {row_data[key]:,.2f}")
    else:
        print(f"✗ Missing SG key '{key}'")

# Check summary key
summary_key = f"{bu}_{SATELLITE_SUMMARY_ID}"
if summary_key in row_data:
    print(f"✓ Found summary key '{summary_key}': {row_data[summary_key]:,.2f}")
else:
    print(f"✗ Missing summary key '{summary_key}'")

print(f"\nAll keys in row_data ({len(row_data)}):")
for key in list(row_data.keys())[:20]:
    if 'FIXED LINE' in key and ('4.5' in key or 'SATELLITE' in key):
        print(f"  {key}: {row_data[key]:,.2f}")
