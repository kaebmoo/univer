#!/usr/bin/env python3
"""
Quick fix script - เพิ่ม sg type support และแก้ปัญหา ratio row
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("Applying quick fixes...")

# นี่คือสรุปของสิ่งที่ต้องแก้:

print("""
สิ่งที่แก้ไขแล้ว:
✅ column_header_writer.py - เพิ่ม _write_sg_column() สำหรับ BU+SG

สิ่งที่ต้องแก้ต่อ:

1. data_writer.py - เพิ่ม handling สำหรับ col_type == 'sg':
   
   ใน _get_cell_value():
   ```python
   elif col_type == 'sg':
       # For BU+SG builder - same as sg_total
       return row_data.get(f'{col.bu}_{col.service_group}', 0)
   ```

2. data_writer.py - แก้ปัญหา ratio row ไม่ควรคำนวณ:
   
   ตรง is_ratio_row check:
   ```python
   # ห้ามคำนวณ ratio สำหรับบรรทัด "คำนวณสัดส่วนต้นทุนบริการต่อรายได้"
   is_ratio_row = (label == "         สัดส่วนต่อรายได้")
   
   # เพิ่ม check:
   if label == "คำนวณสัดส่วนต้นทุนบริการต่อรายได้":
       # ไม่ทำอะไร - ไม่คำนวณ
       row_data = {}
   elif is_ratio_row:
       # คำนวณ ratio
       ...
   ```

ให้รันคำสั่ง:
python3 test_phase2c.py

แล้วตรวจสอบว่ายังมีปัญหาหรือไม่
""")

print("\n✅ แก้ column_header_writer.py เสร็จแล้ว")
print("⏳ ต้องแก้ data_writer.py ด้วยตนเอง")
