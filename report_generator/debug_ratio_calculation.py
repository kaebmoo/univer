#!/usr/bin/env python3
"""
Debug ratio calculation in aggregator
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import CSVLoader, DataProcessor, DataAggregator
from config.row_order import ROW_ORDER
from config.data_mapping import is_calculated_row

# Load CSV
csv_path = Path("../data/TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv")
csv_loader = CSVLoader(encoding='tis-620')
df = csv_loader.load_csv(csv_path)

# Process data
data_processor = DataProcessor()
df = data_processor.process_data(df)

# Create aggregator
aggregator = DataAggregator(df)

# Get BUs and service groups
bu_list = data_processor.get_unique_business_units(df)
service_group_dict = {}
for bu in bu_list:
    service_group_dict[bu] = data_processor.get_unique_service_groups(df, bu)

# Simulate row-by-row calculation
all_row_data = {}

for level, label, is_calc, formula, is_bold in ROW_ORDER:
    if not label:
        continue

    # Get row data
    if is_calculated_row(label):
        row_data = aggregator.calculate_summary_row(label, bu_list, service_group_dict, all_row_data)
    else:
        row_data = aggregator.get_row_data(label, bu_list, service_group_dict)

    all_row_data[label] = row_data

    # Check if this is a row we care about
    if label in [
        "รายได้บริการ",
        "     1. ต้นทุนบริการรวม",
        "         สัดส่วนต่อรายได้",
        "     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ",
        "     3. ต้นทุนบริการ - ไม่รวมค่าใช้จ่ายบุคลากรและค่าเสื่อมราคาฯ"
    ]:
        grand_total = row_data.get("GRAND_TOTAL", 0)
        print(f"{label}:")
        print(f"  GRAND_TOTAL: {grand_total}")
        if "สัดส่วน" in label:
            print(f"  As %: {grand_total*100:.2f}%")
        print()

print("="*80)
print("Checking all_row_data keys available when calculating first ratio:")
print("="*80)
for key in sorted(all_row_data.keys()):
    if "รายได้" in key or "ต้นทุน" in key:
        print(f"  - {key}")
