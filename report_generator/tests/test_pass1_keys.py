#!/usr/bin/env python3
"""Test if Pass 1 stores satellite summary keys in all_row_data"""
import pandas as pd
from pathlib import Path
from src.data_loader import CSVLoader, DataProcessor, DataAggregator
from config.satellite_config import SATELLITE_SUMMARY_ID

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

# Simulate Pass 1 for a data row
label = "- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์"
print(f"Testing label: '{label}'")
print("="*80)

row_data = aggregator.get_row_data_glgroup(
    label,
    bu_list,
    service_group_dict
)

# Check for satellite summary key
bu = "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND"
summary_key = f"{bu}_{SATELLITE_SUMMARY_ID}"

print(f"\nChecking for key '{summary_key}' in row_data:")
if summary_key in row_data:
    print(f"✓ Found: {row_data[summary_key]:,.2f}")
else:
    print(f"✗ Not found")

print(f"\nAll SATELLITE keys in row_data:")
for key in row_data.keys():
    if 'FIXED LINE' in key and ('4.5' in key or 'SATELLITE' in key or 'SUMMARY' in key):
        print(f"  {key}: {row_data[key]:,.2f}")

# Simulate storing to all_row_data
all_row_data = {}
main_group = "2 รวมค่าใช้จ่าย"
storage_key = f"{main_group}|{label}"
all_row_data[storage_key] = row_data

print(f"\n\nStored in all_row_data with key: '{storage_key}'")
print(f"Checking retrieval:")

# Try to retrieve it back
if storage_key in all_row_data:
    retrieved = all_row_data[storage_key]
    if summary_key in retrieved:
        print(f"✓ Can retrieve satellite summary: {retrieved[summary_key]:,.2f}")
    else:
        print(f"✗ Satellite summary NOT in retrieved dict")
        print(f"   Retrieved has {len(retrieved)} keys")
else:
    print(f"✗ Storage key not found in all_row_data")
