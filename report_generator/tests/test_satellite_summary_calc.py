#!/usr/bin/env python3
"""Test satellite summary calculation for calculated rows"""

# Mock setup
all_row_data = {
    "1 รวมรายได้": {
        "GRAND_TOTAL": 49165074507.34,
        "BU_TOTAL_4.กลุ่มธุรกิจ FIXED LINE & BROADBAND": 14514300175.94,
        "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND_4.5.1 กลุ่มบริการ Satellite-NT": 238797432.96,
        "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND_4.5.2 กลุ่มบริการ Satellite-ไทยคม": 398565045.90,
    }
}

# Test calculation
from config.satellite_config import get_satellite_service_group_names

bu = "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND"
label = "1 รวมรายได้"

satellite_sgs = get_satellite_service_group_names()
print(f"Satellite service groups: {satellite_sgs}")
print()

total = 0
for sg in satellite_sgs:
    key = f"{bu}_{sg}"
    print(f"Looking for key: '{key}'")
    value = all_row_data.get(label, {}).get(key, 0)
    print(f"  Value: {value:,.2f}")
    if value is not None:
        total += value

print(f"\nTotal: {total:,.2f}")
print(f"Expected: 637,362,478.86")
