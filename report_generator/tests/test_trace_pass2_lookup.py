#!/usr/bin/env python3
"""Trace what Pass 2 is looking up for ratio rows"""
import pandas as pd
from pathlib import Path
from src.data_loader import CSVLoader, DataProcessor, DataAggregator
from src.report_generator.core.config import ReportConfig
from src.report_generator.rows.row_builder import RowBuilder
from config.satellite_config import SATELLITE_SUMMARY_ID

# Load data
loader = CSVLoader(encoding='tis-620')
df = loader.load_csv(Path('data/TRN_PL_COSTTYPE_NT_YTD_TABLE_SAT_20251031.csv'))
processor = DataProcessor()
df = processor.process_data(df)

# Create config
config = ReportConfig(
    report_type="COSTTYPE",
    period_type="YTD",
    detail_level="BU_SG"
)

# Build rows
row_builder = RowBuilder(config)
rows = row_builder.build_rows()

# Build aggregator
aggregator = DataAggregator(df)
bu_list = processor.get_unique_business_units(df)
service_group_dict = {}
for bu in bu_list:
    service_group_dict[bu] = processor.get_unique_service_groups(df, bu)

# Simulate Pass 1
print("Simulating Pass 1...")
print("="*80)

all_row_data = {}
current_main_group_label = None
previous_label = None

for row_def in rows:
    label = row_def.label

    # Update main group
    if row_def.level == 0:
        current_main_group_label = label

    # Skip empty rows
    if not label:
        continue

    # Only process the rows we care about
    if label not in ["รายได้บริการ", "คำนวณสัดส่วนต้นทุนบริการต่อรายได้",
                      "     1. ต้นทุนบริการรวม", "         สัดส่วนต่อรายได้",
                      "     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ",
                      "     3. ต้นทุนบริการ - ไม่รวมค่าใช้จ่ายบุคลากรและค่าเสื่อมราคาฯ"]:
        previous_label = label
        continue

    is_ratio_row = (label == "สัดส่วนต่อรายได้" or "สัดส่วนต่อรายได้" in label)
    skip_calculation = (label == "คำนวณสัดส่วนต้นทุนบริการต่อรายได้")

    if skip_calculation:
        row_data = {}
    elif is_ratio_row:
        # Determine ratio type based on previous label
        if previous_label == "     1. ต้นทุนบริการรวม":
            ratio_type = "total_service_cost_ratio"
        elif previous_label == "     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ":
            ratio_type = "service_cost_no_depreciation_ratio"
        elif previous_label == "     3. ต้นทุนบริการ - ไม่รวมค่าใช้จ่ายบุคลากรและค่าเสื่อมราคาฯ":
            ratio_type = "service_cost_no_personnel_depreciation_ratio"
        else:
            ratio_type = "total_service_cost_ratio"

        row_data = aggregator._calculate_ratio_by_type(
            ratio_type, all_row_data, bu_list, service_group_dict
        )
        print(f"\nCalculated ratio: '{label}' (previous: '{previous_label}')")
        print(f"  Ratio type: {ratio_type}")

        bu4 = "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND"
        sat_key = f"{bu4}_{SATELLITE_SUMMARY_ID}"
        print(f"  Satellite value: {row_data.get(sat_key, 'NOT FOUND')}")

    else:
        row_data = aggregator.calculate_summary_row(
            label, bu_list, service_group_dict, all_row_data
        )
        bu4 = "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND"
        sat_key = f"{bu4}_{SATELLITE_SUMMARY_ID}"
        print(f"\nCalculated: '{label}'")
        print(f"  Satellite value: {row_data.get(sat_key, 'NOT FOUND')}")

    # Store with composite key if needed
    if is_ratio_row and previous_label:
        storage_key = f"{previous_label}|{label}"
        all_row_data[storage_key] = row_data
        print(f"  Stored with composite key: '{storage_key}'")
    elif row_def.level == 1 and current_main_group_label:
        storage_key = f"{current_main_group_label}|{label}"
        all_row_data[storage_key] = row_data
        print(f"  Stored with composite key: '{storage_key}'")
    else:
        all_row_data[label] = row_data
        print(f"  Stored with key: '{label}'")

    previous_label = label

print("\n" + "="*80)
print("Pass 1 complete")
print(f"Total keys in all_row_data: {len(all_row_data)}")
print()

# Check what's stored
print("Ratio row storage keys:")
for key in all_row_data.keys():
    if "สัดส่วนต่อรายได้" in key:
        print(f"  '{key}'")
        bu4 = "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND"
        sat_key = f"{bu4}_{SATELLITE_SUMMARY_ID}"
        sat_value = all_row_data[key].get(sat_key, 'NOT FOUND')
        print(f"    Satellite: {sat_value}")
