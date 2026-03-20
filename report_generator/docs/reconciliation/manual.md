# คู่มือใช้งานโปรแกรม Reconciliation (ตรวจกระทบยอด P&L)

## ภาพรวม

มีโปรแกรม 2 ตัว ทำงานเสริมกัน ตรวจกระทบยอดระหว่าง **CSV source data** กับ **Excel report** ของ NT P&L:

| โปรแกรม | ไฟล์ | ระดับการตรวจ |
|---------|------|-------------|
| **โปรแกรม 1** | `reconcile_nt_pl.py` | ระดับ **กลุ่มธุรกิจ (BU)** + ข้ามชีต + พันธมิตร |
| **โปรแกรม 2** | `reconcile_sg_svc_v2.py` | ระดับ **กลุ่มบริการ (Service Group)** + **บริการ/ผลิตภัณฑ์ (Product)** |

ทั้ง 2 โปรแกรมรองรับ **MTH (รายเดือน)** และ **YTD (สะสม)** พร้อมกัน

---

## 1. สิ่งที่ต้องเตรียม

### 1.1 ติดตั้ง Python และ Library

ต้องติดตั้ง **Python 3.7 ขึ้นไป** และ Library ดังนี้:

| Library | ใช้ทำอะไร |
|---------|----------|
| `pandas` | อ่านไฟล์ CSV, รวมยอด (aggregate), สร้าง DataFrame ผลลัพธ์ |
| `openpyxl` | อ่าน/เขียนไฟล์ Excel (.xlsx) |

ติดตั้งทั้งหมดด้วยคำสั่งเดียว:

```bash
pip install pandas openpyxl
```

> **หมายเหตุ:** Library อื่นที่ใช้ในโค้ด (`pathlib`, `dataclasses`, `datetime`, `json`, `re`, `typing`)
> เป็น built-in ของ Python อยู่แล้ว ไม่ต้องติดตั้งเพิ่ม

### 1.2 เตรียมโครงสร้างโฟลเดอร์

ให้สร้างโฟลเดอร์ `data/` และ `report/` ไว้ข้างในโฟลเดอร์เดียวกับ script:

```
reconciliation/
├── reconcile_nt_pl.py        # โปรแกรม 1
├── reconcile_sg_svc_v2.py    # โปรแกรม 2
├── data/                     # <<< วางไฟล์ CSV ที่นี่
│   ├── TRN_PL_COSTTYPE_NT_MTH_TABLE_20251231.csv
│   ├── TRN_PL_COSTTYPE_NT_YTD_TABLE_20251231.csv
│   ├── TRN_PL_GLGROUP_NT_MTH_TABLE_20251231.csv
│   └── TRN_PL_GLGROUP_NT_YTD_TABLE_20251231.csv
├── report/                   # <<< วางไฟล์ Excel Report ที่นี่
│   ├── Report_NT_ธ.ค.68_(ก่อนผู้สอบบัญชีรับรอง)_T.xlsx
│   └── Report_NT BU_สะสมธ.ค.2568_(ก่อนผู้สอบบัญชีรับรอง) _T.xlsx
└── output/                   # <<< ผลลัพธ์จะถูกสร้างที่นี่ (สร้างอัตโนมัติ)
    ├── reconciliation_report_202512.xlsx
    └── reconciliation_sg_svc_v2_202512.xlsx
```

> **หมายเหตุ:** โฟลเดอร์ `output/` ไม่ต้องสร้างเอง โปรแกรมจะสร้างให้อัตโนมัติ

---

## 2. วิธีตั้งค่า PATH (สำคัญ)

เปิดไฟล์ script แต่ละตัว แก้ไขส่วน **PATH CONFIGURATION** ด้านบนของไฟล์:

### 2.1 ตั้งค่าโฟลเดอร์

ปกติไม่ต้องแก้ เพราะค่า default ชี้ไปที่โฟลเดอร์ย่อยของ script อยู่แล้ว:

```python
DATA_DIR   = SCRIPT_DIR / 'data'      # โฟลเดอร์ CSV
REPORT_DIR = SCRIPT_DIR / 'report'    # โฟลเดอร์ Excel report
OUTPUT_DIR = SCRIPT_DIR / 'output'    # โฟลเดอร์ผลลัพธ์
```

หากต้องการชี้ไปที่อื่น (ใช้ `SCRIPT_DIR` เป็นฐานได้):

```python
# ตัวอย่าง relative (อ้างอิงจากตำแหน่ง script):
DATA_DIR   = SCRIPT_DIR.parent / 'shared_data'
REPORT_DIR = SCRIPT_DIR.parent / 'reports'
OUTPUT_DIR = SCRIPT_DIR.parent / 'results'

# ตัวอย่าง absolute Windows:
DATA_DIR   = Path(r'C:\Users\somchai\Documents\PL_Data')
REPORT_DIR = Path(r'D:\SharedDrive\NT\Report\PL')
OUTPUT_DIR = Path(r'C:\Users\somchai\Desktop\reconciliation_output')

# ตัวอย่าง absolute macOS / Linux:
DATA_DIR   = Path('/Users/somchai/Documents/PL_Data')
REPORT_DIR = Path('/Users/somchai/Documents/NT/Report/PL')
OUTPUT_DIR = Path('/Users/somchai/Desktop/reconciliation_output')
```

### 2.2 ตั้งค่าชื่อไฟล์ CSV

เปลี่ยนวันที่ `20251231` เป็นงวดที่ต้องการตรวจ:

```python
CSV_FILENAMES = {
    'COSTTYPE_MTH': 'TRN_PL_COSTTYPE_NT_MTH_TABLE_20251231.csv',
    'COSTTYPE_YTD': 'TRN_PL_COSTTYPE_NT_YTD_TABLE_20251231.csv',
    'GLGROUP_MTH':  'TRN_PL_GLGROUP_NT_MTH_TABLE_20251231.csv',
    'GLGROUP_YTD':  'TRN_PL_GLGROUP_NT_YTD_TABLE_20251231.csv',
}

# ตัวอย่าง: งวด ม.ค. 2569
# CSV_FILENAMES = {
#     'COSTTYPE_MTH': 'TRN_PL_COSTTYPE_NT_MTH_TABLE_20260131.csv',
#     'COSTTYPE_YTD': 'TRN_PL_COSTTYPE_NT_YTD_TABLE_20260131.csv',
#     'GLGROUP_MTH':  'TRN_PL_GLGROUP_NT_MTH_TABLE_20260131.csv',
#     'GLGROUP_YTD':  'TRN_PL_GLGROUP_NT_YTD_TABLE_20260131.csv',
# }
```

### 2.3 ตั้งค่าชื่อไฟล์ Excel Report

```python
EXCEL_FILENAMES = {
    'MTH': 'Report_NT_ธ.ค.68_(ก่อนผู้สอบบัญชีรับรอง)_T.xlsx',
    'YTD': 'Report_NT BU_สะสมธ.ค.2568_(ก่อนผู้สอบบัญชีรับรอง) _T.xlsx',
}

# ตัวอย่าง: งวด ม.ค. 2569
# EXCEL_FILENAMES = {
#     'MTH': 'Report_NT_ม.ค.69_(ก่อนผู้สอบบัญชีรับรอง)_T.xlsx',
#     'YTD': 'Report_NT BU_สะสมม.ค.2569_(ก่อนผู้สอบบัญชีรับรอง) _T.xlsx',
# }
```

### 2.4 ตั้งค่าชื่อไฟล์ผลลัพธ์

```python
OUTPUT_FILENAME = 'reconciliation_report_202512.xlsx'

# ตัวอย่าง: งวด ม.ค. 2569
# OUTPUT_FILENAME = 'reconciliation_report_202601.xlsx'
```

---

## 3. วิธีรัน

```bash
# โปรแกรม 1 - ตรวจระดับ BU + ข้ามชีต + พันธมิตร
python reconcile_nt_pl.py

# โปรแกรม 2 - ตรวจระดับ Service Group + Product
python reconcile_sg_svc_v2.py
```

> **หมายเหตุ:** สามารถ `cd` ไปที่โฟลเดอร์ไหนก็ได้แล้วรัน ไม่จำเป็นต้องอยู่ในโฟลเดอร์ script
> เพราะโปรแกรมใช้ `Path(__file__)` อ้างอิงตำแหน่ง script เสมอ

---

## 4. รายละเอียดการตรวจสอบของแต่ละโปรแกรม

### 4.1 โปรแกรม 1: `reconcile_nt_pl.py`

ตรวจ **4 ด้าน** ระหว่าง CSV source กับ Excel report:

#### (A) CSV vs Excel — ยอดรวมทั้งสิ้น (Total)
- ใช้ CSV COSTTYPE เทียบกับ Excel ชีต **ต้นทุน_กลุ่มธุรกิจ**
- ใช้ CSV GLGROUP เทียบกับ Excel ชีต **หมวดบัญชี_กลุ่มธุรกิจ**
- ตรวจทุก GROUP row เช่น รายได้, ต้นทุนบริการ, กำไรขั้นต้น, กำไรสุทธิ ฯลฯ (14 รายการ COSTTYPE, 5 รายการ GLGROUP)
- เทียบกับคอลัมน์ **"รวมทั้งสิ้น"** ใน Excel

#### (B) CSV vs Excel — รายกลุ่มธุรกิจ (per-BU)
- เทียบยอดรายได้และกำไรสุทธิ แยกตาม **กลุ่มธุรกิจ** (Hard Infrastructure, International, Mobile, Fixed Line, Digital, ICT Solution ฯลฯ)
- ตรวจว่ายอดรวมในแต่ละ BU column ของ Excel ตรงกับ CSV หรือไม่

#### (C) Cross-sheet — ต้นทุน vs หมวดบัญชี
- เทียบตัวเลขข้าม Sheet ภายใน Excel เดียวกัน:
  - **ต้นทุน_กลุ่มธุรกิจ** vs **หมวดบัญชี_กลุ่มธุรกิจ**
  - **ต้นทุน_กลุ่มบริการ** vs **หมวดบัญชี_กลุ่มบริการ**
  - **ต้นทุน_บริการ** vs **หมวดบัญชี_บริการ**
- ตรวจ: รายได้รวม, EBITDA, กำไรสุทธิ ต้องตรงกันทั้ง 2 มุมมอง

#### (D) Alliance check — พันธมิตร + ไม่รวมพันธมิตร = รวมทั้งสิ้น
- ตรวจว่า คอลัมน์ **พันธมิตร** + คอลัมน์ **ไม่รวมพันธมิตร** = คอลัมน์ **รวมทั้งสิ้น**
- ตรวจบนชีต: ต้นทุน_กลุ่มธุรกิจ, หมวดบัญชี_กลุ่มธุรกิจ, ต้นทุน_กลุ่มบริการ, หมวดบัญชี_กลุ่มบริการ

---

### 4.2 โปรแกรม 2: `reconcile_sg_svc_v2.py`

ตรวจ **2 ระดับ** ที่ละเอียดกว่า:

#### (A) CSV vs Excel — ระดับกลุ่มบริการ (Service Group)
- ใช้ CSV COSTTYPE เทียบกับ Excel ชีต **ต้นทุน_กลุ่มบริการ**
- ใช้ CSV GLGROUP เทียบกับ Excel ชีต **หมวดบัญชี_กลุ่มบริการ**
- ตรวจทุก SERVICE_GROUP ที่มีใน CSV (เช่น 1.1 บริการโครงข่าย, 2.1 บริการระหว่างประเทศ ฯลฯ)
- เทียบรายการ: รายได้, ต้นทุนบริการ, กำไรขั้นต้น, กำไรหลังหักค่าใช้จ่ายขาย, กำไรก่อนต้นทุนจัดหาเงิน, กำไรก่อนภาษี, กำไรสุทธิ
- Matching: ใช้ prefix (เช่น "1.1") หรือ substring เพื่อจับคู่ชื่อ SERVICE_GROUP ระหว่าง CSV กับ Excel

#### (B) CSV vs Excel — ระดับบริการ/ผลิตภัณฑ์ (Product)
- ใช้ CSV COSTTYPE เทียบกับ Excel ชีต **ต้นทุน_บริการ**
- ใช้ CSV GLGROUP เทียบกับ Excel ชีต **หมวดบัญชี_บริการ**
- ตรวจทุก PRODUCT_KEY ที่มีใน CSV (จับคู่กับเลข product key ในหัวตาราง Excel)
- เทียบรายการเดียวกับระดับ Service Group

---

## 5. การอ่านผลลัพธ์

### 5.1 ผลลัพธ์บนหน้าจอ

```
--- CSV vs Excel (MTH) - ต้นทุน_กลุ่มธุรกิจ ---
Check                                                   |         Source |         Target |            Diff | Status
-------------------------------------------------------+-----------------+-----------------+-----------------+-------
รายได้รวมจากการให้บริการ (รวมทั้งสิ้น)                      |  1,500,000.00 |  1,500,000.00 |            0.00 | PASS
กำไร(ขาดทุน) สุทธิ (รวมทั้งสิ้น)                          |    300,000.00 |    300,000.00 |            0.00 | PASS
...
==========
Summary: 85 PASSED / 2 FAILED / 87 Total checks
```

- **PASS** = ผลต่างไม่เกิน 0.02 บาท (tolerance สำหรับ floating point)
- **FAIL** = ผลต่างเกิน tolerance → ต้องตรวจสอบข้อมูลต้นทาง

### 5.2 ไฟล์ Excel ผลลัพธ์

ไฟล์ output จะมีหลาย Sheet:

| Sheet | เนื้อหา |
|-------|---------|
| **Summary** | จำนวน PASS / FAIL / อัตราผ่าน |
| **All Checks** | ผลตรวจสอบทุกรายการ |
| **Failed Checks** | เฉพาะรายการที่ FAIL (ถ้ามี) |

---

## 6. การแก้ไขปัญหา (Troubleshooting)

| อาการ | สาเหตุ | วิธีแก้ |
|-------|--------|---------|
| `FileNotFoundError` | ไฟล์ไม่อยู่ในโฟลเดอร์ที่กำหนด | ตรวจสอบว่าวางไฟล์ใน `data/` และ `report/` แล้ว และชื่อไฟล์ตรงกับ config |
| `KeyError: 'ต้นทุน_กลุ่มธุรกิจ'` | ชื่อ Sheet ใน Excel ไม่ตรง | เปิด Excel ตรวจชื่อ Tab ด้านล่างให้ตรงกับค่าในโค้ด |
| ค่าเป็น 0 ทั้งหมด | ตำแหน่ง row/column เปลี่ยน | โครงสร้าง Excel เปลี่ยน ให้ตรวจ header row ใน Excel |
| `UnicodeDecodeError` | Encoding ไฟล์ CSV ไม่ตรง | โปรแกรมลอง utf-8, cp874, tis-620 อัตโนมัติ แต่ถ้ายังไม่ได้ให้ save CSV ใหม่เป็น UTF-8 |
| `ModuleNotFoundError` | ยังไม่ติดตั้ง library | รัน `pip install pandas openpyxl` |

---

## 7. ข้อมูลอ้างอิง

### ชีต Excel ที่ใช้

| ชื่อ Sheet | ใช้โดยโปรแกรม |
|-----------|--------------|
| ต้นทุน_กลุ่มธุรกิจ | 1 + 2 |
| ต้นทุน_กลุ่มบริการ | 1 + 2 |
| ต้นทุน_บริการ | 1 + 2 |
| หมวดบัญชี_กลุ่มธุรกิจ | 1 + 2 |
| หมวดบัญชี_กลุ่มบริการ | 1 + 2 |
| หมวดบัญชี_บริการ | 1 + 2 |

### Tolerance

ค่า tolerance = **0.001 บาท** (ยอมรับผลต่างจาก floating point)
หากต้องการเปลี่ยน แก้ที่ `TOLERANCE = 0.001` ด้านบนของแต่ละไฟล์
