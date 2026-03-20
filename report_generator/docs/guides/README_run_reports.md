# คู่มือการใช้งาน run_reports

## คำอธิบาย
สคริปต์สำหรับรันการสร้างรายงานอัตโนมัติ โดยจะทำงาน 2 ขั้นตอน:
1. สร้างรายงานแยกแต่ละประเภท (MTH, YTD) สำหรับ COSTTYPE และ GLGROUP
2. รวมรายงานทั้งหมดให้เป็นไฟล์เดียว (concatenate)

## รองรับการระบุเดือน
สคริปต์รองรับการระบุเดือนแบบ optional:
- **ไม่ระบุเดือน**: สแกนหาไฟล์ CSV ทุกเดือนใน data/ และสร้างรายงานทุกเดือนที่พบ จากนั้นรวมรายงานทุกเดือนใน output
- **ระบุเดือน**: เลือกไฟล์ CSV ตามเดือนที่กำหนด (รูปแบบ YYYYMM) และสร้างรายงานเฉพาะเดือนนั้น

---

## สำหรับ macOS/Linux: run_reports.sh

### วิธีการใช้งาน

#### 1. รันโดยไม่ระบุเดือน (ใช้ข้อมูลทั้งหมดที่มี)
```bash
chmod +x run_reports.sh
./run_reports.sh
```

**ผลลัพธ์:**
- สร้างรายงานแยกทุกประเภท (12 ไฟล์ต่อเดือน)
- รวมรายงานแยกตามเดือนที่พบ เช่น:
  - `Report_NT_202509.xlsx`
  - `Report_NT_202511.xlsx`
  - `Report_NT_YTD_202509.xlsx`
  - `Report_NT_YTD_202511.xlsx`

#### 2. รันโดยระบุเดือน (เฉพาะเดือนที่กำหนด)
```bash
./run_reports.sh 202509
```

**ผลลัพธ์:**
- สร้างรายงานแยกเฉพาะเดือน 202509 (12 ไฟล์)
- รวมรายงานเฉพาะเดือน 202509:
  - `Report_NT_202509.xlsx`
  - `Report_NT_YTD_202509.xlsx`

### ตัวอย่าง Output
```
--- Starting Report Generation for Month: 202509 ---
Processing YTD Reports...
Processing MTH Reports...
--- Individual Report Files Generated Successfully ---

--- Starting Report Concatenation ---
Creating MTH report for 202509: Report_NT_202509.xlsx
Creating YTD report for 202509: Report_NT_YTD_202509.xlsx

===================================================
--- All Reports Completed Successfully ---
===================================================
```

---

## สำหรับ Windows: run_reports.bat

### วิธีการใช้งาน

#### 1. รันโดยไม่ระบุเดือน (ใช้ข้อมูลทั้งหมดที่มี)
```cmd
run_reports.bat
```
หรือดับเบิลคลิกที่ไฟล์ `run_reports.bat`

**ผลลัพธ์:**
- สแกนหาเดือนทั้งหมดใน data/ (เช่น 202509, 202511)
- สร้างรายงานแยกทุกประเภทสำหรับทุกเดือน
- รวมรายงานแยกตามทุกเดือนที่พบ

#### 2. รันโดยระบุเดือน (เฉพาะเดือนที่กำหนด)
```cmd
run_reports.bat 202509
```

**ผลลัพธ์:**
- สร้างและรวมรายงานเฉพาะเดือน 202509

### ตัวอย่าง Output
```
--- Starting Report Generation for Month: 202509 ---
Processing YTD Reports...
Processing MTH Reports...
--- Individual Report Files Generated Successfully ---

--- Starting Report Concatenation ---
Creating MTH report for 202509: Report_NT_202509.xlsx
Creating YTD report for 202509: Report_NT_YTD_202509.xlsx

===================================================
--- All Reports Completed Successfully ---
===================================================
Press any key to continue . . .
```

---

## การทำงานของสคริปต์

### ขั้นตอนที่ 1: สร้างรายงานแยก
สร้างรายงาน 12 ไฟล์สำหรับแต่ละเดือน:

**YTD (6 ไฟล์):**
1. `PL_COSTTYPE_YTD_BU_SG_PRODUCT_YYYYMM.xlsx`
2. `PL_COSTTYPE_YTD_BU_SG_YYYYMM.xlsx`
3. `PL_COSTTYPE_YTD_BU_ONLY_YYYYMM.xlsx`
4. `PL_GLGROUP_YTD_BU_SG_PRODUCT_YYYYMM.xlsx`
5. `PL_GLGROUP_YTD_BU_SG_YYYYMM.xlsx`
6. `PL_GLGROUP_YTD_BU_ONLY_YYYYMM.xlsx`

**MTH (6 ไฟล์):**
1. `PL_COSTTYPE_MTH_BU_SG_PRODUCT_YYYYMM.xlsx`
2. `PL_COSTTYPE_MTH_BU_SG_YYYYMM.xlsx`
3. `PL_COSTTYPE_MTH_BU_ONLY_YYYYMM.xlsx`
4. `PL_GLGROUP_MTH_BU_SG_PRODUCT_YYYYMM.xlsx`
5. `PL_GLGROUP_MTH_BU_SG_YYYYMM.xlsx`
6. `PL_GLGROUP_MTH_BU_ONLY_YYYYMM.xlsx`

### ขั้นตอนที่ 2: รวมรายงาน (Concatenate)
รวมไฟล์ 6 ไฟล์ให้เป็น 1 ไฟล์ โดยแต่ละไฟล์เป็น sheet แยกกัน:

**ไม่ระบุเดือน:**
- สร้างไฟล์รวมแยกตามทุกเดือนที่พบ

**ระบุเดือน:**
- สร้างไฟล์รวมเฉพาะเดือนที่ระบุ

---

## ข้อกำหนด

### สำหรับ macOS/Linux
- Python 3.6+
- ไลบรารี: pandas, openpyxl
- ให้สิทธิ์ execute: `chmod +x run_reports.sh`

### สำหรับ Windows
- Python 3.6+
- ไลบรารี: pandas, openpyxl
- Python ต้องอยู่ใน PATH

---

## โครงสร้างไฟล์

```
report_generator/
├── run_reports.sh              # สคริปต์สำหรับ macOS/Linux
├── run_reports.bat             # สคริปต์สำหรับ Windows
├── generate_report.py          # สร้างรายงานแยก
├── report_concat.py            # รวมรายงาน
├── data/                       # ข้อมูล input
└── output/                     # ไฟล์รายงานที่สร้าง
    ├── PL_*.xlsx              # รายงานแยก
    ├── Report_NT_*.xlsx       # รายงาน MTH รวม
    └── Report_NT_YTD_*.xlsx   # รายงาน YTD รวม
```

---

## การแก้ไขปัญหา

### ปัญหา: Permission denied (macOS/Linux)
```bash
chmod +x run_reports.sh
```

### ปัญหา: Python not found (Windows)
ตรวจสอบว่า Python อยู่ใน PATH:
```cmd
python --version
```

### ปัญหา: Module not found
ติดตั้ง dependencies:
```bash
pip install pandas openpyxl
```

---

## สรุปความแตกต่าง

| การใช้งาน | คำสั่ง | ผลลัพธ์ |
|----------|--------|---------|
| ไม่ระบุเดือน | `./run_reports.sh` | สร้างรายงานทุกเดือนที่มีในระบบ |
| ระบุเดือน | `./run_reports.sh 202509` | สร้างเฉพาะเดือน 202509 |

**ข้อดีของการไม่ระบุเดือน:**
- สร้างรายงานทุกเดือนในคราวเดียว
- ไม่ต้องรันหลายครั้ง

**ข้อดีของการระบุเดือน:**
- รันเร็วขึ้น (เฉพาะเดือนที่ต้องการ)
- ประหยัดทรัพยากร
- เหมาะสำหรับการสร้างรายงานย้อนหลัง
