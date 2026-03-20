# Data Writer Fixes

## Fix 1: เพิ่ม sg type support

หาบรรทัดที่มี:
```python
elif col_type == 'sg_total':
    # SG total = sum of all products in this SG
    return row_data.get(f'{col.bu}_{col.service_group}', 0)
```

เพิ่มข้างล่างเป็น:
```python
elif col_type == 'sg':
    # For BU+SG builder - SG column (same as sg_total)
    return row_data.get(f'{col.bu}_{col.service_group}', 0)
```

## Fix 2: แก้ ratio row ไม่ควรคำนวณ

หาบรรทัดที่มี:
```python
is_ratio_row = (label == "         สัดส่วนต่อรายได้")
```

เปลี่ยนเป็น:
```python
is_ratio_row = (label == "         สัดส่วนต่อรายได้")

# CRITICAL FIX: ห้ามคำนวณ ratio สำหรับบรรทัดนี้
skip_calculation = (label == "คำนวณสัดส่วนต้นทุนบริการต่อรายได้")
```

แล้วหาบรรทัด:
```python
if is_ratio_row:
```

เปลี่ยนเป็น:
```python
if skip_calculation:
    # ห้ามคำนวณ - ใช้ค่าว่าง
    row_data = {}
elif is_ratio_row:
```

## วิธีแก้:

1. เปิดไฟล์: src/report_generator/writers/data_writer.py
2. แก้ตาม Fix 1 และ Fix 2
3. Save
4. รันทดสอบ: python3 test_phase2c.py
5. เปิด Excel ตรวจสอบ:
   - bu_sg_report.xlsx ต้องมีชื่อกลุ่มบริการ
   - ทุกไฟล์ บรรทัด "คำนวณสัดส่วนต้นทุนบริการต่อรายได้" ต้องเป็นค่าว่าง (ไม่ใช่ 0.00%)
