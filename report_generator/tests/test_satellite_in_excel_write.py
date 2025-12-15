#!/usr/bin/env python3
"""Test what value is returned for satellite summary in Excel write"""
import logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(message)s')

import pandas as pd
from pathlib import Path
from src.data_loader import CSVLoader, DataProcessor, DataAggregator
from config.satellite_config import SATELLITE_SUMMARY_ID

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

# Build all_row_data (simulating what the report generator does)
all_row_data = {}

# Calculate rows in order
print("\nBuilding all_row_data...")
print("="*80)

# รายได้บริการ
all_row_data["รายได้บริการ"] = aggregator.calculate_summary_row(
    "รายได้บริการ", bu_list, service_group_dict, all_row_data
)

# ต้นทุนบริการรวม
all_row_data["     1. ต้นทุนบริการรวม"] = aggregator.calculate_summary_row(
    "     1. ต้นทุนบริการรวม", bu_list, service_group_dict, all_row_data
)

# Check what's in all_row_data
bu = "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND"
sat_key = f"{bu}_{SATELLITE_SUMMARY_ID}"

print(f"\nChecking all_row_data['     1. ต้นทุนบริการรวม']:")
print(f"  Total keys: {len(all_row_data['     1. ต้นทุนบริการรวม'])}")
print(f"  Satellite summary key '{sat_key}' present: {sat_key in all_row_data['     1. ต้นทุนบริการรวม']}")

if sat_key in all_row_data["     1. ต้นทุนบริการรวม"]:
    print(f"  Value: {all_row_data['     1. ต้นทุนบริการรวม'][sat_key]:,.2f}")
else:
    print(f"  Available keys (first 10): {list(all_row_data['     1. ต้นทุนบริการรวม'].keys())[:10]}")

# Now simulate what the data writer does
print("\n" + "="*80)
print("Simulating DataWriter._get_satellite_summary_value()...")
print("="*80)

label = "     1. ต้นทุนบริการรวม"
summary_key = f"{bu}_{SATELLITE_SUMMARY_ID}"
row_dict = all_row_data.get(label, {})
value = row_dict.get(summary_key, 0)

print(f"Label: '{label}'")
print(f"Summary key: '{summary_key}'")
print(f"Row dict has {len(row_dict)} keys")
print(f"Summary key in row_dict: {summary_key in row_dict}")
print(f"Value: {value}")
