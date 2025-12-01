# Common Size Feature - Implementation Summary

## วันที่: 30 พฤศจิกายน 2568

## สรุปการเปลี่ยนแปลง

เพิ่มคุณสมบัติ **Common Size** ในรายงาน P&L สำหรับกลุ่มธุรกิจ (BU_ONLY) เท่านั้น

### คุณสมบัติที่เพิ่ม

1. **การคำนวณ Common Size**
   - หารตัวเลขแต่ละบรรทัดด้วย "รายได้รวม" แสดงเป็น %
   - ยกเว้นบรรทัด "สัดส่วนต่อรายได้" (ไม่คำนวณ Common Size)

2. **การแสดงผล**
   - ค่าเป็น 0: ไม่แสดง (blank)
   - ค่าเป็นบวก: แสดง 42.00%
   - ค่าเป็นลบ: แสดง (42.00%) สีแดง

3. **ตำแหน่ง Column**
   - Common Size อยู่ถัดจาก column จำนวนเงินเสมอ
   - รวมทั้งสิ้น → Common Size → BU1 → Common Size → BU2 → Common Size → ...

4. **Default Behavior**
   - **BU_ONLY**: มี Common Size โดยอัตโนมัติ
   - **BU_SG** และ **BU_SG_PRODUCT**: ไม่มี Common Size (ตามที่ระบุว่าเฉพาะกลุ่มธุรกิจ)

## ไฟล์ที่แก้ไข

### 1. `src/report_generator/core/config.py`
- เพิ่ม field `include_common_size: Optional[bool] = None`
- แก้ไข `__post_init__()` ให้ auto-detect ตาม detail_level:
  - BU_ONLY: default = True
  - BU_SG: default = False
  - BU_SG_PRODUCT: default = False

### 2. `src/report_generator/columns/base_column_builder.py`
- เพิ่ม method `_create_common_size_column(bu=None)`
- สร้าง ColumnDef ประเภท 'common_size'

### 3. `src/report_generator/columns/bu_only_builder.py`
- แก้ไข `build_columns()` เพื่อเพิ่ม common size column
- เพิ่มหลัง grand_total และหลัง bu_total แต่ละ BU

### 4. `src/report_generator/writers/column_header_writer.py`
- เพิ่ม logic เขียน header สำหรับ col_type == 'common_size'
- Merge cells จาก row 1-4 เหมือน label และ grand_total

### 5. `src/report_generator/writers/data_writer.py`
- เพิ่ม case `col_type == 'common_size'` ใน `_get_cell_value()`
- เพิ่ม method `_calculate_common_size()`:
  - ดึง "รายได้รวม" (COSTTYPE) หรือ "1 รวมรายได้" (GLGROUP)
  - คำนวณ current_value / total_revenue
  - ยกเว้นบรรทัด "สัดส่วนต่อรายได้"
- แก้ไข `is_percentage` ให้รวม `col.col_type == 'common_size'`

### 6. `src/report_generator/formatters/cell_formatter.py`
- แก้ไข number format สำหรับ percentage:
  - จาก: `'0.00%'`
  - เป็น: `'0.00%;[Red](0.00%);""'`
  - ผลลัพธ์: 0 = blank, ลบ = (42.00%) สีแดง

### 7. `generate_report.py`
- เพิ่ม argument `--common-size` (force enable)
- เพิ่ม argument `--no-common-size` (force disable)
- Default: None (auto-detect จาก detail_level)

## วิธีใช้งาน

### 1. ใช้ default (BU_ONLY มี common size อัตโนมัติ)
```bash
python generate_report.py --detail-level BU_ONLY
```

### 2. Force enable common size
```bash
python generate_report.py --detail-level BU_ONLY --common-size
```

### 3. Force disable common size
```bash
python generate_report.py --detail-level BU_ONLY --no-common-size
```

### 4. ตัวอย่างคำสั่งเต็ม
```bash
python generate_report.py \
    --csv-file data/TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv \
    --report-type COSTTYPE \
    --period MTH \
    --detail-level BU_ONLY \
    --output output/test_common_size.xlsx
```

## ตัวอย่าง Output

**Column Header Structure (2-level):**
```
รายละเอียด                    รวมทั้งสิ้น                    1.กลุ่มธุรกิจ HARD INFRASTRUCTURE
                           จำนวนเงิน  | Common Size   จำนวนเงิน  | Common Size
```

**Data Rows:**
```
รายได้รวม                  2,981,973.55 | 100.00%       661,999.87 | 100.00%
- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน  610,144.93 | 20.47%        609,433.51 | 92.06%
- รายได้กลุ่มธุรกิจโทรศัพท์ประจำที่... 1,478,292.47 | 49.57%        ...        | ...
รายได้บริการ              2,726,542.03 | 91.43%        486,319.71 | 73.46%
ต้นทุนบริการรวม         (1,478,292.47)| (49.57%)      (333,768.49)| (50.42%)
  สัดส่วนต่อรายได้            54.21%       |             68.64%     |
```

**หมายเหตุ:**
- Row 1: ชื่อ BU merge ข้าม 2 columns (จำนวนเงิน + Common Size)
- Row 2-4: Sub-headers "จำนวนเงิน" | "Common Size"
- บรรทัด "สัดส่วนต่อรายได้" ไม่มี Common Size

## หมายเหตุสำคัญ

1. **ความปลอดภัย**: ไม่กระทบโค้ดเดิม ทุกอย่างเป็น optional
2. **Backward Compatible**: ถ้าไม่ใช้ `--common-size` ก็จะทำงานเหมือนเดิม
3. **เฉพาะ BU_ONLY**: Common Size จะแสดงเฉพาะเมื่อ detail_level = BU_ONLY เท่านั้น (ตาม requirement)
4. **รองรับทั้ง COSTTYPE และ GLGROUP**: ใช้งานได้ทั้ง 2 แบบ

## การทดสอบที่แนะนำ

1. ทดสอบ COSTTYPE MTH BU_ONLY (default)
2. ทดสอบ GLGROUP YTD BU_ONLY (default)
3. ทดสอบ BU_ONLY with --no-common-size
4. ทดสอบ BU_SG (ควรไม่มี common size)
5. ทดสอบว่าค่าลบแสดงเป็น (42.00%) สีแดง
6. ทดสอบว่าค่า 0 ไม่แสดงอะไร
7. ทดสอบว่าบรรทัด "สัดส่วนต่อรายได้" ไม่มี common size
