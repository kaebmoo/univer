#!/usr/bin/env python3
"""Test if satellite summary keys exist in all_row_data"""
import pandas as pd
from pathlib import Path
from src.data_loader import CSVLoader, DataProcessor, DataAggregator

# Load COSTTYPE data
loader = CSVLoader(encoding='tis-620')
df = loader.load_csv(Path('data/TRN_PL_COSTTYPE_NT_YTD_TABLE_20251031.csv'))
processor = DataProcessor()
df = processor.process_data(df)

# Build aggregator
aggregator = DataAggregator(df)

# Get BU list and service_group_dict
bu_list = processor.get_unique_business_units(df)
service_group_dict = {}
for bu in bu_list:
    service_group_dict[bu] = processor.get_unique_service_groups(df, bu)

# Test get_row_data
print("Testing get_row_data() for row '     1. ต้นทุนบริการรวม':")
print("="*80)

from config.data_mapping import get_group_sub_group
group, sub_group = get_group_sub_group("     1. ต้นทุนบริการรวม", "2.ต้นทุนบริการและต้นทุนขาย :")

row_data = aggregator.get_row_data(
    "     1. ต้นทุนบริการรวม",
    "2.ต้นทุนบริการและต้นทุนขาย :",
    bu_list,
    service_group_dict
)

# Check for SATELLITE keys
bu = "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND"
from config.satellite_config import SATELLITE_SUMMARY_ID, get_satellite_service_group_names

satellite_sgs = get_satellite_service_group_names()
print(f"\nChecking keys for BU: {bu}")
print(f"Satellite SGs: {satellite_sgs}")
print(f"Satellite summary ID: {SATELLITE_SUMMARY_ID}")
print()

# Check detail SG keys
for sg in satellite_sgs:
    key = f"{bu}_{sg}"
    if key in row_data:
        print(f"✓ Found key '{key}': {row_data[key]:,.2f}")
    else:
        print(f"✗ Missing key '{key}'")

# Check summary key
summary_key = f"{bu}_{SATELLITE_SUMMARY_ID}"
if summary_key in row_data:
    print(f"✓ Found summary key '{summary_key}': {row_data[summary_key]:,.2f}")
else:
    print(f"✗ Missing summary key '{summary_key}'")

print(f"\nAll keys in row_data: {len(row_data)}")
print("Sample keys:", [k for k in list(row_data.keys())[:10]])
