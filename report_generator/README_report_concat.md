# Report Concatenation Tool

## คำอธิบาย
สคริปต์สำหรับรวมไฟล์รายงาน Excel หลายๆ ไฟล์ให้เป็นไฟล์เดียว โดยแต่ละไฟล์จะกลายเป็น sheet แยกกัน พร้อมการจัดรูปแบบ (formatting) ครบถ้วน

## ฟีเจอร์หลัก
- รองรับการรวมรายงานทั้งแบบ MTH (รายเดือน) และ YTD (สะสมตั้งแต่ต้นปี)
- สามารถระบุเดือนที่ต้องการประมวลผล หรือประมวลผลทุกเดือนที่มีอยู่
- คัดลอก formatting, cell styles, merged cells ทั้งหมดจากไฟล์ต้นฉบับ
- ตั้งชื่อ sheet เป็นภาษาไทยแบบอ่านง่าย

## วิธีการใช้งาน

### 1. ประมวลผลทุกเดือนที่มีอยู่
```bash
python report_concat.py
```

หากใน folder มีไฟล์หลายเดือน เช่น:
- `PL_COSTTYPE_MTH_BU_ONLY_202509.xlsx`
- `PL_COSTTYPE_MTH_BU_ONLY_202511.xlsx`

จะได้ผลลัพธ์:
- `Report_NT_202509.xlsx` (MTH เดือน 09)
- `Report_NT_202511.xlsx` (MTH เดือน 11)
- `Report_NT_YTD_202509.xlsx` (YTD เดือน 09)
- `Report_NT_YTD_202511.xlsx` (YTD เดือน 11)

### 2. ประมวลผลเฉพาะเดือนที่ระบุ
```bash
python report_concat.py --month 202509
```

จะได้เฉพาะ:
- `Report_NT_202509.xlsx` (MTH)
- `Report_NT_YTD_202509.xlsx` (YTD)

## โครงสร้างไฟล์

### Input Files (ใน folder output/)
```
PL_COSTTYPE_MTH_BU_ONLY_YYYYMM.xlsx
PL_COSTTYPE_MTH_BU_SG_YYYYMM.xlsx
PL_COSTTYPE_MTH_BU_SG_PRODUCT_YYYYMM.xlsx
PL_GLGROUP_MTH_BU_ONLY_YYYYMM.xlsx
PL_GLGROUP_MTH_BU_SG_YYYYMM.xlsx
PL_GLGROUP_MTH_BU_SG_PRODUCT_YYYYMM.xlsx

PL_COSTTYPE_YTD_BU_ONLY_YYYYMM.xlsx
PL_COSTTYPE_YTD_BU_SG_YYYYMM.xlsx
PL_COSTTYPE_YTD_BU_SG_PRODUCT_YYYYMM.xlsx
PL_GLGROUP_YTD_BU_ONLY_YYYYMM.xlsx
PL_GLGROUP_YTD_BU_SG_YYYYMM.xlsx
PL_GLGROUP_YTD_BU_SG_PRODUCT_YYYYMM.xlsx
```

### Output Files (ใน folder output/)
```
Report_NT_YYYYMM.xlsx          (MTH รายงานรายเดือน)
Report_NT_YTD_YYYYMM.xlsx      (YTD รายงานสะสม)
```

## ชื่อ Sheets ในไฟล์ผลลัพธ์
1. **ต้นทุน_กลุ่มธุรกิจ** - จาก PL_COSTTYPE_xxx_BU_ONLY
2. **ต้นทุน_กลุ่มบริการ** - จาก PL_COSTTYPE_xxx_BU_SG
3. **ต้นทุน_บริการ** - จาก PL_COSTTYPE_xxx_BU_SG_PRODUCT
4. **หมวดบัญชี_กลุ่มธุรกิจ** - จาก PL_GLGROUP_xxx_BU_ONLY
5. **หมวดบัญชี_กลุ่มบริการ** - จาก PL_GLGROUP_xxx_BU_SG
6. **หมวดบัญชี_บริการ** - จาก PL_GLGROUP_xxx_BU_SG_PRODUCT

## ตัวอย่าง Log Output
```
INFO - Script Location: .../univer/report_generator
INFO - Reading from:    .../report_generator/output
INFO - Writing to:      .../report_generator/output
INFO - Processing all months found
INFO - Found MTH months: ['202509', '202511']
INFO - Found YTD months: ['202509', '202511']

========================================
--- Processing MTH Reports ---
========================================

Creating MTH report for 202509: Report_NT_202509.xlsx
  - Copied 'PL_COSTTYPE_MTH_BU_ONLY_202509.xlsx' to sheet 'ต้นทุน_กลุ่มธุรกิจ'
  - Copied 'PL_COSTTYPE_MTH_BU_SG_202509.xlsx' to sheet 'ต้นทุน_กลุ่มบริการ'
  ...
Successfully created: .../output/Report_NT_202509.xlsx
```

## ข้อกำหนด
- Python 3.6+
- openpyxl
- pandas

## หมายเหตุ
- ไฟล์ input และ output อยู่ใน folder เดียวกัน (`output/`)
- ถ้าพบไฟล์ output ชื่อซ้ำจะถูก overwrite
- ตรวจสอบ log เพื่อดูรายละเอียดการประมวลผล
