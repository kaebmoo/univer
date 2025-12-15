#!/usr/bin/env python3
"""Test if satellite summary keys appear in calculated rows"""
import logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(message)s')

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

# Test total_service_cost calculation
print("\n" + "="*80)
print("Testing total_service_cost calculation:")
print("="*80)

# Build all_row_data (simulating what the report generator does)
all_row_data = {}

# First, calculate service revenue
print("\n1. Calculating รายได้บริการ...")
all_row_data["รายได้บริการ"] = aggregator.calculate_summary_row(
    "รายได้บริการ",
    bu_list,
    service_group_dict,
    all_row_data
)

bu = "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND"
from config.satellite_config import SATELLITE_SUMMARY_ID
sat_key = f"{bu}_{SATELLITE_SUMMARY_ID}"

if sat_key in all_row_data["รายได้บริการ"]:
    print(f"   ✓ Satellite summary key found: {all_row_data['รายได้บริการ'][sat_key]:,.2f}")
else:
    print(f"   ✗ Satellite summary key NOT found")

# Then, calculate total service cost
print("\n2. Calculating      1. ต้นทุนบริการรวม...")
all_row_data["     1. ต้นทุนบริการรวม"] = aggregator.calculate_summary_row(
    "     1. ต้นทุนบริการรวม",
    bu_list,
    service_group_dict,
    all_row_data
)

if sat_key in all_row_data["     1. ต้นทุนบริการรวม"]:
    print(f"   ✓ Satellite summary key found: {all_row_data['     1. ต้นทุนบริการรวม'][sat_key]:,.2f}")
else:
    print(f"   ✗ Satellite summary key NOT found")
    print(f"   Keys in total_cost: {list(all_row_data['     1. ต้นทุนบริการรวม'].keys())[:10]}")

# Finally, calculate the ratio
print("\n3. Calculating          สัดส่วนต่อรายได้...")
all_row_data["         สัดส่วนต่อรายได้"] = aggregator.calculate_summary_row(
    "         สัดส่วนต่อรายได้",
    bu_list,
    service_group_dict,
    all_row_data
)

if sat_key in all_row_data["         สัดส่วนต่อรายได้"]:
    ratio_value = all_row_data["         สัดส่วนต่อรายได้"][sat_key]
    print(f"   ✓ Satellite summary key found: {ratio_value}")
else:
    print(f"   ✗ Satellite summary key NOT found")
    print(f"   Keys in ratio: {list(all_row_data['         สัดส่วนต่อรายได้'].keys())[:10]}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"รายได้บริการ satellite sum: {all_row_data['รายได้บริการ'].get(sat_key, 'NOT FOUND')}")
print(f"ต้นทุนบริการรวม satellite sum: {all_row_data['     1. ต้นทุนบริการรวม'].get(sat_key, 'NOT FOUND')}")
print(f"สัดส่วนต่อรายได้ satellite sum: {all_row_data['         สัดส่วนต่อรายได้'].get(sat_key, 'NOT FOUND')}")
