#!/usr/bin/env python3
"""
Debug cost calculation
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import CSVLoader, DataProcessor, DataAggregator

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

# Get total service cost (GROUP 02)
print("="*80)
print("ต้นทุนบริการรวม (GROUP 02):")
print("="*80)
total_cost_data = aggregator._sum_by_group("02.ต้นทุนบริการและต้นทุนขาย :", bu_list, service_group_dict)
grand_total_cost = total_cost_data.get("GRAND_TOTAL", 0)
print(f"GRAND_TOTAL: {grand_total_cost:,.2f}\n")

# Get depreciation from all expense groups (02, 04, 06)
print("="*80)
print("ค่าเสื่อมราคา (ทุก GROUP: 02, 04, 06):")
print("="*80)
depreciation_data = aggregator._sum_depreciation(bu_list, service_group_dict)  # No filter
grand_total_dep = depreciation_data.get("GRAND_TOTAL", 0)
print(f"GRAND_TOTAL: {grand_total_dep:,.2f}\n")

# Calculate cost without depreciation
print("="*80)
print("ต้นทุนบริการ - ค่าเสื่อมราคาฯ:")
print("="*80)
cost_no_dep = grand_total_cost - grand_total_dep
print(f"GRAND_TOTAL: {cost_no_dep:,.2f}")
print(f"(Expected: 885,164,020.77)\n")

# Get personnel from all expense groups (02, 04, 06)
print("="*80)
print("ค่าใช้จ่ายบุคลากร (ทุก GROUP: 02, 04, 06):")
print("="*80)
personnel_data = aggregator._sum_personnel(bu_list, service_group_dict)  # No filter
grand_total_pers = personnel_data.get("GRAND_TOTAL", 0)
print(f"GRAND_TOTAL: {grand_total_pers:,.2f}\n")

# Calculate cost without personnel and depreciation
print("="*80)
print("ต้นทุนบริการ - ไม่รวมบุคลากรและค่าเสื่อมราคาฯ:")
print("="*80)
cost_no_pers_dep = grand_total_cost - grand_total_pers - grand_total_dep
print(f"GRAND_TOTAL: {cost_no_pers_dep:,.2f}")
print(f"(Expected: 1,410,180,113.46)\n")

# Check ratio
print("="*80)
print("สัดส่วน:")
print("="*80)
service_revenue_data = aggregator._sum_by_group("01.รายได้", bu_list, service_group_dict)
service_revenue = service_revenue_data.get("GRAND_TOTAL", 0)
print(f"รายได้บริการ: {service_revenue:,.2f}")
print(f"ต้นทุนบริการรวม: {grand_total_cost:,.2f}")
ratio = (grand_total_cost / service_revenue) * 100 if service_revenue > 0 else 0
print(f"สัดส่วน: {ratio:.2f}%")
print(f"(Expected: 91.43%)\n")
