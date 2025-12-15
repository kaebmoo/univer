#!/usr/bin/env python3
"""Check what service groups BU 4 has in COSTTYPE data"""
import pandas as pd
from pathlib import Path
from src.data_loader import CSVLoader, DataProcessor

# Load COSTTYPE data
loader = CSVLoader(encoding='tis-620')
df = loader.load_csv(Path('data/TRN_PL_COSTTYPE_NT_YTD_TABLE_SAT_20251031.csv'))
processor = DataProcessor()
df = processor.process_data(df)

# Get BU 4 service groups
bu4 = "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND"
service_groups = processor.get_unique_service_groups(df, bu4)

print(f"Service Groups for {bu4}:")
print("="*80)
for sg in service_groups:
    print(f"  {sg}")

print(f"\nTotal: {len(service_groups)} service groups")

# Check for satellite groups
from config.satellite_config import get_satellite_service_group_names, ENABLE_SATELLITE_SPLIT

if ENABLE_SATELLITE_SPLIT:
    satellite_sg_names = get_satellite_service_group_names()
    satellite_groups = [sg for sg in service_groups if sg in satellite_sg_names]

    print(f"\nSATELLITE groups found: {len(satellite_groups)}")
    for sg in satellite_groups:
        print(f"  {sg}")

    # Check for 4.4.x groups
    has_4_4 = any(sg.startswith('4.4') for sg in service_groups)
    print(f"\nHas 4.4.x groups: {has_4_4}")
