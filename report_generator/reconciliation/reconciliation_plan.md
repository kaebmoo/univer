# NT P&L Reconciliation Plan

## สรุปผลการตรวจกระทบยอด (ธ.ค. 2568)

ทำการตรวจกระทบยอดระหว่าง CSV source data กับ Excel report ทั้ง 2 ชุด:

- **รายเดือน (MTH)**: Report_NT_ธ.ค.68_(ก่อนผู้สอบบัญชีรับรอง)_T.xlsx vs TRN_PL_*_MTH_TABLE_20251231.csv
- **สะสม (YTD)**: Report_NT BU_สะสมธ.ค.2568_(ก่อนผู้สอบบัญชีรับรอง)_T.xlsx vs TRN_PL_*_YTD_TABLE_20251231.csv

**ผลลัพธ์: 92 รายการตรวจ ผ่านทั้งหมด (PASS 100%)**

## ระดับการตรวจสอบที่ทำ

### 1. CSV vs Excel - รวมทั้งสิ้น (Total column)
เทียบยอดรวมทุก GROUP row (รายได้, ต้นทุน, กำไรขั้นต้น, ค่าใช้จ่ายขาย, ฯลฯ จนถึงกำไรสุทธิ)
- COSTTYPE CSV vs ต้นทุน_กลุ่มธุรกิจ: 14 rows x 2 periods = 26 checks (MTH ครบ 14, YTD ครบ 12)
- GLGROUP CSV vs หมวดบัญชี_กลุ่มธุรกิจ: 5 rows x 2 periods = 10 checks

### 2. CSV vs Excel - รายกลุ่มธุรกิจ (per-BU)
เทียบยอดรายได้และกำไรสุทธิ แยกตามกลุ่มธุรกิจ (6 กลุ่ม)
- Revenue per-BU: 12 checks (6 BU x 2 periods)

### 3. Cross-sheet Consistency
เทียบระหว่าง ต้นทุน sheets vs หมวดบัญชี sheets (ต้องเท่ากัน)
- กลุ่มธุรกิจ, กลุ่มบริการ, บริการ: 4 items x 3 levels x 2 periods = 24 checks

### 4. Alliance Check
ตรวจ: พันธมิตร + ไม่รวมพันธมิตร = รวมทั้งสิ้น
- 2 items x 4 sheets x 2 periods = ~14 checks

## แผนการตรวจสอบสำหรับครั้งต่อไป

### ขั้นตอนการใช้งาน

1. **เตรียมไฟล์**: วาง CSV files ไว้ใน `report_generator/data/` และ Excel files ไว้ที่ path ที่กำหนด
2. **แก้ path ใน script**: แก้ `DATA_DIR`, `REPORT_DIR`, และชื่อไฟล์ใน `main()` ให้ตรงกับเดือนที่ต้องการตรวจ
3. **รัน**: `python3 reconcile_nt_pl.py`
4. **ดูผล**: ผลลัพธ์จะแสดงใน terminal และ export เป็น Excel

### สิ่งที่ควรพัฒนาเพิ่มเติม

1. **Parameterize**: รับ date parameter (e.g., `--date 20260131`) แทนการ hardcode path
2. **กลุ่มบริการ/บริการ level drill-down**: ตรวจรายละเอียดลงไปถึงระดับ SERVICE_GROUP และ PRODUCT_KEY vs Excel columns
3. **SUB_GROUP matching**: เทียบ sub-group level (เช่น ค่าใช้จ่ายตอบแทนแรงงาน, ค่าสวัสดิการ ฯลฯ)
4. **Manual Excel tolerance**: Excel ที่ทำ manual อาจมีการปัดเศษ ควร parameterize tolerance
5. **HTML dashboard**: สร้าง interactive report แทน Excel
6. **Integration กับ existing reconciliation scripts**: รวมเข้ากับ `pl_reconciliation_enhanced.py` ที่มีอยู่

## โครงสร้าง CSV

ทุกไฟล์ CSV มี columns: `TIME_KEY, GROUP, SUB_GROUP, BU, SERVICE_GROUP, PRODUCT_NAME, PRODUCT_KEY, ALLIE, VALUE`

- **Encoding**: TIS-620 / cp874 (ไม่ใช่ UTF-8)
- **ALLIE**: 'Y' = พันธมิตร, 'N' = ไม่ใช่พันธมิตร
- **COSTTYPE**: GROUP มี 14 ระดับ (01.รายได้ ถึง 14.กำไรสุทธิ) - map กับ ต้นทุน sheets
- **GLGROUP**: GROUP มี 5 ระดับ (01.รายได้ ถึง 05.กำไรสุทธิ) - map กับ หมวดบัญชี sheets

## โครงสร้าง Excel

6 sheets ต่อไฟล์: ต้นทุน_กลุ่มธุรกิจ, ต้นทุน_กลุ่มบริการ, ต้นทุน_บริการ, หมวดบัญชี_กลุ่มธุรกิจ, หมวดบัญชี_กลุ่มบริการ, หมวดบัญชี_บริการ

Column layout (กลุ่มธุรกิจ level):
- B: รายละเอียด (row labels)
- C-D: รวมทั้งสิ้น (จำนวนเงิน, Common Size)
- E-F: พันธมิตร
- G-H: ไม่รวมพันธมิตร
- I onwards: per-BU columns
