#!/usr/bin/env python3
"""Debug ratio calculation"""
import pandas as pd
from pathlib import Path
from src.data_loader import CSVLoader, DataProcessor, DataAggregator
from config.satellite_config import SATELLITE_SUMMARY_ID

# Load data
loader = CSVLoader(encoding='tis-620')
df = loader.load_csv(Path('data/TRN_PL_COSTTYPE_NT_YTD_TABLE_SAT_20251031.csv'))
processor = DataProcessor()
df = processor.process_data(df)

# Build aggregator
aggregator = DataAggregator(df)

# Get BU list and service_group_dict
bu_list = processor.get_unique_business_units(df)
service_group_dict = {}
for bu in bu_list:
    service_group_dict[bu] = processor.get_unique_service_groups(df, bu)

# Build all_row_data
all_row_data = {}

# Calculate needed rows
all_row_data["รายได้บริการ"] = aggregator.calculate_summary_row(
    "รายได้บริการ", bu_list, service_group_dict, all_row_data
)

all_row_data["     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ"] = aggregator.calculate_summary_row(
    "     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ", bu_list, service_group_dict, all_row_data
)

# Manually call _calculate_ratio
bu4 = "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND"
sat_key = f"{bu4}_{SATELLITE_SUMMARY_ID}"

service_revenue = all_row_data.get("รายได้บริการ", {})
cost_no_dep = all_row_data.get("     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ", {})

print("service_revenue dict:")
print(f"  Total keys: {len(service_revenue)}")
print(f"  Satellite key '{sat_key}' present: {sat_key in service_revenue}")
if sat_key in service_revenue:
    print(f"  Value: {service_revenue[sat_key]}")

print()
print("cost_no_dep dict:")
print(f"  Total keys: {len(cost_no_dep)}")
print(f"  Satellite key '{sat_key}' present: {sat_key in cost_no_dep}")
if sat_key in cost_no_dep:
    print(f"  Value: {cost_no_dep[sat_key]}")

print()
print("Calling _calculate_ratio...")
result = aggregator._calculate_ratio(cost_no_dep, service_revenue)

print(f"Result dict:")
print(f"  Total keys: {len(result)}")
print(f"  Satellite key '{sat_key}' present: {sat_key in result}")
if sat_key in result:
    print(f"  Value: {result[sat_key]}")
else:
    print(f"  Keys in result (first 10): {list(result.keys())[:10]}")
