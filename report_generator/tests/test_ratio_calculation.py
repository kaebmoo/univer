#!/usr/bin/env python3
"""Test ratio calculation for satellite summary"""
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

# Build all_row_data in the same order as the report
all_row_data = {}

# Calculate the rows in order
print("Calculating rows in order...")
print("="*80)

# 1. รายได้บริการ
print("\n1. Calculating รายได้บริการ...")
all_row_data["รายได้บริการ"] = aggregator.calculate_summary_row(
    "รายได้บริการ", bu_list, service_group_dict, all_row_data
)

bu4 = "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND"
sat_key = f"{bu4}_{SATELLITE_SUMMARY_ID}"
print(f"   Satellite: {all_row_data['รายได้บริการ'].get(sat_key, 'NOT FOUND')}")

# 2. ต้นทุนบริการรวม
print("\n2. Calculating      1. ต้นทุนบริการรวม...")
all_row_data["     1. ต้นทุนบริการรวม"] = aggregator.calculate_summary_row(
    "     1. ต้นทุนบริการรวม", bu_list, service_group_dict, all_row_data
)
print(f"   Satellite: {all_row_data['     1. ต้นทุนบริการรวม'].get(sat_key, 'NOT FOUND')}")

# 3. สัดส่วนต่อรายได้ (ratio for row 2)
print("\n3. Calculating          สัดส่วนต่อรายได้ (for total_service_cost)...")
all_row_data["         สัดส่วนต่อรายได้_1"] = aggregator.calculate_summary_row(
    "         สัดส่วนต่อรายได้", bu_list, service_group_dict, all_row_data
)
print(f"   Satellite: {all_row_data['         สัดส่วนต่อรายได้_1'].get(sat_key, 'NOT FOUND')}")

# 4. ต้นทุนบริการ - ค่าเสื่อมราคาฯ
print("\n4. Calculating      2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ...")
all_row_data["     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ"] = aggregator.calculate_summary_row(
    "     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ", bu_list, service_group_dict, all_row_data
)
print(f"   Satellite: {all_row_data['     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ'].get(sat_key, 'NOT FOUND')}")

# 5. สัดส่วนต่อรายได้ (ratio for row 4)
print("\n5. Calculating          สัดส่วนต่อรายได้ (for service_cost_no_depreciation)...")
all_row_data["         สัดส่วนต่อรายได้_2"] = aggregator.calculate_summary_row(
    "         สัดส่วนต่อรายได้", bu_list, service_group_dict, all_row_data
)
print(f"   Satellite: {all_row_data['         สัดส่วนต่อรายได้_2'].get(sat_key, 'NOT FOUND')}")

# Verify the calculation manually
revenue_sat = all_row_data["รายได้บริการ"].get(sat_key, 0)
cost_no_dep_sat = all_row_data["     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ"].get(sat_key, 0)
ratio_sat = all_row_data["         สัดส่วนต่อรายได้_2"].get(sat_key, 0)

print()
print("="*80)
print("VERIFICATION")
print("="*80)
print(f"Revenue satellite: {revenue_sat:,.2f}")
print(f"Cost (no depreciation) satellite: {cost_no_dep_sat:,.2f}")
print(f"Ratio satellite: {ratio_sat}")
print(f"Expected ratio: {cost_no_dep_sat / revenue_sat if revenue_sat != 0 else 0}")

if abs(ratio_sat - (cost_no_dep_sat / revenue_sat)) < 0.0001:
    print("✓ Ratio calculation CORRECT")
else:
    print("❌ Ratio calculation WRONG")
