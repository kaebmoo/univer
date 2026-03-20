# คู่มือใช้งานโปรแกรม Reconciliation (ตรวจกระทบยอด P&L)

## ภาพรวม

มีโปรแกรม 5 ตัว ทำงานเสริมกัน ตรวจกระทบยอดระหว่าง CSV source data กับ Excel report ของ NT P&L:

| โปรแกรม | ไฟล์ | ระดับการตรวจ |
| ------- | ---- | ----------- |
| โปรแกรม 1 | `reconcile_nt_pl.py` | ระดับ กลุ่มธุรกิจ (BU) + ข้ามชีต + พันธมิตร |
| โปรแกรม 2 | `reconcile_sg_svc_v2.py` | ระดับ กลุ่มบริการ (Service Group) + บริการ/ผลิตภัณฑ์ (Product) + EBIT + EBITDA + Cross-column |
| โปรแกรม 3 | `pl_reconciliation.py` | ตรวจกับงบการเงิน (basic 4 checkpoints) |
| โปรแกรม 4 | `pl_reconciliation_enhanced.py` | ตรวจกับงบการเงิน (enhanced, 3 validation modes) |
| โปรแกรม 5 | `pl_reconciliation_combined.py` | ตรวจ combined output |

- โปรแกรม 1-2 ตรวจ **CSV vs Excel report** ทั้ง MTH (รายเดือน) และ YTD (สะสม) พร้อมกัน
- โปรแกรม 3-5 ตรวจ **Excel report vs งบการเงิน** (pld_nt_*.txt)

---

## 1. สิ่งที่ต้องเตรียม

### 1.1 ติดตั้ง Python และ Library

ต้องติดตั้ง Python 3.7 ขึ้นไป และ Library ดังนี้:

| Library | ใช้ทำอะไร |
| ------- | --------- |
| `pandas` | อ่านไฟล์ CSV, รวมยอด (aggregate), สร้าง DataFrame ผลลัพธ์ |
| `openpyxl` | อ่าน/เขียนไฟล์ Excel (.xlsx) |

ติดตั้งทั้งหมดด้วยคำสั่งเดียว:

```bash
pip install pandas openpyxl
```

> **หมายเหตุ:** Library อื่นที่ใช้ในโค้ด (`pathlib`, `dataclasses`, `datetime`, `json`, `re`, `typing`) เป็น built-in ของ Python อยู่แล้ว ไม่ต้องติดตั้งเพิ่ม

### 1.2 เตรียมโครงสร้างโฟลเดอร์

โครงสร้างโฟลเดอร์:

```text
reconciliation/
├── reconcile_nt_pl.py             # โปรแกรม 1
├── reconcile_sg_svc_v2.py         # โปรแกรม 2
├── pl_reconciliation.py           # โปรแกรม 3
├── pl_reconciliation_enhanced.py  # โปรแกรม 4
├── pl_reconciliation_combined.py  # โปรแกรม 5
├── data/                          # <<< วางไฟล์ CSV และงบการเงินที่นี่
│   ├── TRN_PL_COSTTYPE_NT_MTH_TABLE_20251231.csv
│   ├── TRN_PL_COSTTYPE_NT_YTD_TABLE_20251231.csv
│   ├── TRN_PL_GLGROUP_NT_MTH_TABLE_20251231.csv
│   ├── TRN_PL_GLGROUP_NT_YTD_TABLE_20251231.csv
│   ├── pld_nt_20251231.txt        # งบการเงิน (ใช้โดยโปรแกรม 3-5)
│   └── pl_combined_output_*.xlsx  # combined output (ใช้โดยโปรแกรม 5)
├── report/                        # <<< วาง Excel Report ที่นี่
│   ├── Report_NT_202512.xlsx      #     (copy จาก report_generator/output/)
│   └── Report_NT_YTD_202512.xlsx
└── output/                        # <<< ผลลัพธ์จะถูกสร้างที่นี่ (สร้างอัตโนมัติ)
    ├── reconciliation_report_202512.xlsx
    └── reconciliation_sg_svc_v2_202512.xlsx
```

> **หมายเหตุ:** โฟลเดอร์ `output/` ไม่ต้องสร้างเอง โปรแกรมจะสร้างให้อัตโนมัติ

### 1.3 เตรียมไฟล์ CSV Source Data

**สำคัญ:** ไฟล์ CSV ใน `data/` ต้อง**ใช้ไฟล์เดียวกัน**กับที่ report generator ใช้ (`report_generator/data/`) เพื่อให้ข้อมูลตรงกับ report ที่ generate ออกมา:

```bash
# copy CSV จาก report_generator/data/ มาที่ reconciliation/data/
cp ../data/TRN_PL_*_20260131.csv data/
```

**ข้อควรระวัง encoding:** ไฟล์ CSV จาก SAP ต้องเป็น **TIS-620 หรือ CP874** ถ้า encoding ผิด (เช่น ถูก save เป็น UTF-8 แล้วภาษาไทยกลายเป็น `๏ฟฝ` หรือ `�`) จะทำให้:

- Report generator สร้าง report ที่มีค่า 0 ทั้งหมด
- Reconciliation match GROUP/BU/SERVICE_GROUP ไม่ได้
- ต้อง export ใหม่จาก SAP ด้วย encoding ที่ถูกต้อง

### 1.4 เตรียมไฟล์ Excel Report

**ขั้นตอนสำคัญ:** ก่อนรัน reconciliation ต้อง copy ไฟล์ Excel report จากที่ report generator สร้างไว้มาใส่ `report/`:

```bash
cp ../output/Report_NT_202601.xlsx report/
cp ../output/Report_NT_YTD_202601.xlsx report/
```

ทุกโปรแกรมใช้ `report/` เป็นที่อ่าน Excel report เหมือนกันหมด

---

## 2. วิธีตั้งค่า PATH (สำคัญ)

### 2.1 โปรแกรม 1-2: แก้ config ด้านบนของไฟล์

เปิดไฟล์ script แต่ละตัว แก้ไขส่วน **PATH CONFIGURATION** ด้านบนของไฟล์:

#### ตั้งค่าโฟลเดอร์

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

# ตัวอย่าง absolute Windows:
DATA_DIR   = Path(r'C:\Users\somchai\Documents\PL_Data')

# ตัวอย่าง absolute macOS / Linux:
DATA_DIR   = Path('/Users/somchai/Documents/PL_Data')
```

#### ตั้งค่าชื่อไฟล์ CSV

เปลี่ยนวันที่ `20251231` เป็นงวดที่ต้องการตรวจ:

```python
CSV_FILENAMES = {
    'COSTTYPE_MTH': 'TRN_PL_COSTTYPE_NT_MTH_TABLE_20251231.csv',
    'COSTTYPE_YTD': 'TRN_PL_COSTTYPE_NT_YTD_TABLE_20251231.csv',
    'GLGROUP_MTH':  'TRN_PL_GLGROUP_NT_MTH_TABLE_20251231.csv',
    'GLGROUP_YTD':  'TRN_PL_GLGROUP_NT_YTD_TABLE_20251231.csv',
}
```

#### ตั้งค่าชื่อไฟล์ Excel Report

เปลี่ยนชื่อไฟล์ให้ตรงกับไฟล์ที่ copy มาไว้ใน `report/`:

```python
EXCEL_FILENAMES = {
    'MTH': 'Report_NT_202512.xlsx',
    'YTD': 'Report_NT_YTD_202512.xlsx',
}
```

#### ตั้งค่าชื่อไฟล์ผลลัพธ์

```python
OUTPUT_FILENAME = 'reconciliation_report_202512.xlsx'
```

### 2.2 โปรแกรม 3-4: ใช้ --date argument (ไม่ต้องแก้โค้ด)

`pl_reconciliation.py` และ `pl_reconciliation_enhanced.py` รับ parameter `--date` ทำให้ไม่ต้องแก้โค้ด:

```bash
python pl_reconciliation.py --date 20260131
python pl_reconciliation_enhanced.py --date 20260131
```

โปรแกรมจะสร้างชื่อไฟล์อัตโนมัติตามวันที่ที่ระบุ ถ้าไม่ระบุ `--date` จะหยุดทำงานและแจ้งให้ระบุ

### 2.4 โปรแกรม 5: แก้ config ใน main()

เปิด `pl_reconciliation_combined.py` แก้ชื่อไฟล์ใน function `main()`:

```python
config = CombinedFileConfig(
    combined_file=str(data_dir / 'pl_combined_output_202512.xlsx'),
    source_gl_csv_mth=str(data_dir / 'TRN_PL_GLGROUP_NT_MTH_TABLE_20251231.csv'),
    source_gl_csv_ytd=str(data_dir / 'TRN_PL_GLGROUP_NT_YTD_TABLE_20251231.csv'),
    financial_stmt_txt=str(data_dir / 'pld_nt_20251231.txt')
)
```

---

## 3. วิธีรัน

```bash
# โปรแกรม 1 - ตรวจระดับ BU + ข้ามชีต + พันธมิตร
python reconcile_nt_pl.py

# โปรแกรม 2 - ตรวจระดับ Service Group + Product + EBIT/EBITDA
python reconcile_sg_svc_v2.py

# โปรแกรม 3 - ตรวจกับงบการเงิน (basic)
python pl_reconciliation.py --date 20260131

# โปรแกรม 4 - ตรวจกับงบการเงิน (enhanced)
python pl_reconciliation_enhanced.py --date 20260131

# โปรแกรม 4 - เลือก validation mode
python pl_reconciliation_enhanced.py --date 20260131 --mode basic
python pl_reconciliation_enhanced.py --date 20260131 --mode enhanced
python pl_reconciliation_enhanced.py --date 20260131 --mode comprehensive

# โปรแกรม 5 - ตรวจ combined output
python pl_reconciliation_combined.py
```

> **หมายเหตุ:** สามารถ `cd` ไปที่โฟลเดอร์ไหนก็ได้แล้วรัน ไม่จำเป็นต้องอยู่ในโฟลเดอร์ script เพราะโปรแกรมใช้ `Path(__file__)` อ้างอิงตำแหน่ง script เสมอ

---

## 4. รายละเอียดการตรวจสอบของแต่ละโปรแกรม

### 4.1 โปรแกรม 1: `reconcile_nt_pl.py`

ตรวจ 5 ด้าน ระหว่าง CSV source กับ Excel report:

#### (A) CSV vs Excel - ยอดรวมทั้งสิ้น (Total)

- ใช้ CSV COSTTYPE เทียบกับ Excel ชีต **ต้นทุน_กลุ่มธุรกิจ**
- ใช้ CSV GLGROUP เทียบกับ Excel ชีต **หมวดบัญชี_กลุ่มธุรกิจ**
- ตรวจทุก GROUP row เช่น รายได้รวม, ต้นทุนบริการ, กำไรขั้นต้น, กำไรสุทธิ ฯลฯ (14 รายการ COSTTYPE, 5 รายการ GLGROUP)
- เทียบกับคอลัมน์ "รวมทั้งสิ้น" ใน Excel

#### (B) CSV vs Excel - รายกลุ่มธุรกิจ (per-BU)

- เทียบ **ทุก GROUP row** แยกตาม **กลุ่มธุรกิจ** ทั้ง 8 กลุ่ม:
  1-6. กลุ่มธุรกิจ HARD INFRASTRUCTURE, INTERNATIONAL, MOBILE, FIXED LINE, DIGITAL, ICT SOLUTION
  7. กลุ่มบริการอื่นไม่ใช่โทรคมนาคม
  8. รายได้อื่น/ค่าใช้จ่ายอื่น
- ตรวจทุกรายการ (รายได้, ต้นทุน, กำไรขั้นต้น, ค่าใช้จ่ายขาย, EBIT, EBT, กำไรสุทธิ ฯลฯ) ไม่ใช่แค่รายได้กับกำไรสุทธิ

#### (C) Cross-sheet - ต้นทุน vs หมวดบัญชี

- เทียบตัวเลขข้าม Sheet ภายใน Excel เดียวกัน:
  - ต้นทุน_กลุ่มธุรกิจ vs หมวดบัญชี_กลุ่มธุรกิจ
  - ต้นทุน_กลุ่มบริการ vs หมวดบัญชี_กลุ่มบริการ
  - ต้นทุน_บริการ vs หมวดบัญชี_บริการ
- ตรวจทั้ง **ยอดรวมทั้งสิ้น** และ **รายกลุ่มธุรกิจ (per-BU)**:
  - รายได้รวม, ค่าใช้จ่ายรวม, EBITDA, กำไรสุทธิ

#### (D) Column-Total: sum(BU columns) = รวมทั้งสิ้น

- ตรวจว่า ผลรวมของทุก BU column (8 กลุ่ม) = column "รวมทั้งสิ้น"
- ตรวจบนชีต: ต้นทุน_กลุ่มธุรกิจ, หมวดบัญชี_กลุ่มธุรกิจ
- ตรวจ 4 rows: รายได้รวม, EBITDA, EBT, กำไรสุทธิ

#### (E) Alliance check - พันธมิตร + ไม่รวมพันธมิตร = รวมทั้งสิ้น

- ตรวจว่า คอลัมน์ พันธมิตร + คอลัมน์ ไม่รวมพันธมิตร = คอลัมน์ รวมทั้งสิ้น
- ตรวจบนชีต: ต้นทุน_กลุ่มธุรกิจ, หมวดบัญชี_กลุ่มธุรกิจ, ต้นทุน_กลุ่มบริการ, หมวดบัญชี_กลุ่มบริการ

### 4.2 โปรแกรม 2: `reconcile_sg_svc_v2.py`

ตรวจ 8 ด้าน ที่ละเอียดกว่า:

#### (A) CSV vs Excel - ระดับกลุ่มบริการ (Service Group)

- ใช้ CSV COSTTYPE เทียบกับ Excel ชีต **ต้นทุน_กลุ่มบริการ**
- ใช้ CSV GLGROUP เทียบกับ Excel ชีต **หมวดบัญชี_กลุ่มบริการ**
- ตรวจทุก SERVICE_GROUP ที่มีใน CSV (เช่น 1.1 บริการโครงข่าย, 2.1 บริการระหว่างประเทศ ฯลฯ)
- เทียบรายการ: รายได้, ต้นทุนบริการ, กำไรขั้นต้น, กำไรหลังหักค่าใช้จ่ายขาย, กำไรก่อนต้นทุนจัดหาเงิน, กำไรก่อนภาษี, กำไรสุทธิ

#### (B) CSV vs Excel - ระดับบริการ/ผลิตภัณฑ์ (Product)

- ใช้ CSV COSTTYPE เทียบกับ Excel ชีต **ต้นทุน_บริการ**
- ใช้ CSV GLGROUP เทียบกับ Excel ชีต **หมวดบัญชี_บริการ**
- ตรวจทุก PRODUCT_KEY ที่มีใน CSV (จับคู่กับเลข product key ในหัวตาราง Excel)

#### (C) EBIT (calculated check)

- **COSTTYPE**: คำนวณจาก CSV → Revenue(01) - Expense(02,04,06,07)
- **GLGROUP**: คำนวณจาก CSV → Revenue(01) - Expense(02) + FinanceOp(SUB_GROUP 19)
- เทียบค่าที่คำนวณได้กับค่า EBIT ใน Excel ทั้งระดับ SG และ Product

#### (D) EBITDA (calculated check)

- **COSTTYPE**: Revenue(01,09) - Expense(02,04,06,10) + Depreciation(SUB_GROUP 12,13)
- **GLGROUP**: EBIT + Depreciation(SUB_GROUP 12,13)
- เทียบค่าที่คำนวณได้กับค่า EBITDA ใน Excel ทั้งระดับ SG และ Product

#### (E) Cross-column consistency

- ตรวจว่าคอลัมน์สรุป (เช่น "รวม 4.5 SATELLITE") = ผลรวมของคอลัมน์ย่อย (4.5.1 + 4.5.2)
- ครอบคลุมทุก "รวม X.X" column ที่มีใน Excel ทุกแถว
- ข้าม row ที่เป็นอัตราส่วน (สัดส่วนต่อรายได้) เพราะ ratio บวกข้ามคอลัมน์ไม่ได้

#### (F) Column-Total: sum(columns) = รวมทั้งสิ้น

- ตรวจว่า ผลรวมของทุก column ย่อย (BU-level) = column "รวมทั้งสิ้น" ภายในแต่ละ sheet
- ตรวจทุก sheet (ต้นทุน + หมวดบัญชี × กลุ่มบริการ + บริการ = 4 sheets)
- ตรวจ 4 rows: รายได้รวม, EBITDA, EBT, กำไรสุทธิ
- ข้าม Common Size columns (สัดส่วนร้อยละ) และ sub-total columns

#### (G) Cross-sheet Total: รวมทั้งสิ้น ต้นทุน vs หมวดบัญชี

- เทียบ column "รวมทั้งสิ้น" ระหว่าง ต้นทุน sheet กับ หมวดบัญชี sheet
- ตรวจ: รายได้รวม, EBITDA, EBT, กำไรสุทธิ
- ทำทั้งระดับ กลุ่มบริการ และ บริการ

> **หลักการ:** ถ้า (F) PASS → ทุก column ย่อยรวมกันถูกต้อง
> ถ้า (G) PASS → ยอดรวมสุทธิข้ามประเภทตรงกัน
> ถ้าทั้ง (F) + (G) PASS → **มั่นใจได้ว่าข้อมูลถูกต้องทั้ง 2 มุมมอง**

#### (H) Cross-sheet - ต้นทุน vs หมวดบัญชี (per-SG & per-Product)

- เทียบ **กำไรก่อนภาษี (EBT)** และ **กำไรสุทธิ** ข้ามชีตภายใน Excel:
  - ต้นทุน_กลุ่มบริการ row 12 (EBT) vs หมวดบัญชี_กลุ่มบริการ row 3 (EBT) → ทุก SG column
  - ต้นทุน_บริการ row 12 (EBT) vs หมวดบัญชี_บริการ row 3 (EBT) → ทุก Product column
- ยอดสุทธิเหล่านี้ต้องตรงกันทั้ง 2 มุมมอง เพราะเป็นข้อมูลเดียวกัน จัดแสดงต่างมิติ

> **หมายเหตุ — สิ่งที่ยังไม่ได้ตรวจ:**
>
> Cross-sheet per-SG/Product ตรวจเฉพาะ **ยอดสุทธิ** (EBT, กำไรสุทธิ) เท่านั้น
> ยังไม่ได้ตรวจ revenue, expense per-SG/Product ข้ามประเภท เพราะ:
> - ต้นทุน (COSTTYPE) มี GROUP ละเอียด 14 กลุ่ม (01-14)
> - หมวดบัญชี (GLGROUP) มี GROUP รวม 5 กลุ่ม (01-05)
> - การเทียบ revenue/expense ต้อง aggregate SUB_GROUP ของ COSTTYPE
>   ให้ตรงกับ GLGROUP ก่อน (เช่น COSTTYPE GROUP 01+09 = GLGROUP GROUP 01)
>   ซึ่งยังไม่ได้ implement

### 4.3 โปรแกรม 3: `pl_reconciliation.py`

ใช้ `--date YYYYMMDD` (ไม่ต้องแก้โค้ด) ตรวจ 3 checkpoints:

| Check | เปรียบเทียบ |
| ----- | ----------- |
| 1. Consistency | กำไรสุทธิใน Cost Sheet vs GL Sheet (ข้ามชีต) |
| 2. Accuracy | กำไรสุทธิจาก CSV vs Excel report |
| 3. Tie-out | Excel report vs งบการเงิน pld_nt_*.txt (ข้ามถ้าไม่มีไฟล์) |

### 4.4 โปรแกรม 4: `pl_reconciliation_enhanced.py`

ตรวจเหมือนโปรแกรม 3 แต่มี 3 validation modes:

| Mode | รายละเอียด |
| ---- | ---------- |
| **BASIC** | เฉพาะ Net Profit check (Phase 1) |
| **ENHANCED** | Revenue, Expense, Net Profit + Internal Math (Phase 2) |
| **COMPREHENSIVE** | ทุกรายการ + drill-down analysis (Phase 3) |

ใช้งาน:

```bash
python pl_reconciliation_enhanced.py --date 20260131 --mode comprehensive
```

### 4.5 โปรแกรม 5: `pl_reconciliation_combined.py`

ตรวจไฟล์ `pl_combined_output` ที่รวม revenue_gl_group + expense_gl_group + summary_other:

- Net Profit = Revenue - Expense + Financial Income + Other Revenue - Other Expense
- ตรวจทั้ง MTH และ YTD

---

## 5. ระดับความน่าเชื่อถือ และสิ่งที่ยังไม่ได้ตรวจ

### 5.1 สิ่งที่ตรวจแล้ว (ความมั่นใจสูง)

| การตรวจ | โปรแกรม | ความครอบคลุม |
| ------- | ------- | ------------ |
| CSV vs Excel ทุก GROUP row (Total) | 1, 2 | COSTTYPE 14 rows + GLGROUP 5 rows |
| CSV vs Excel ทุก GROUP row (per-BU) | 1 | ทุก GROUP × 8 BU |
| CSV vs Excel ทุก GROUP row (per-SG) | 2 | ทุก GROUP × ~30 SG |
| CSV vs Excel ทุก GROUP row (per-Product) | 2 | ทุก GROUP × ~160 Product |
| EBIT/EBITDA คำนวณจาก CSV (per-SG, per-Product) | 2 | ทั้ง COSTTYPE + GLGROUP |
| Cross-column: summary = sum(children) | 2 | ทุก "รวม X.X" column × ทุก row |
| Column-Total: sum(BU columns) = รวมทั้งสิ้น | 1, 2 | โปรแกรม 1: 2 sheets (กลุ่มธุรกิจ), โปรแกรม 2: 4 sheets (กลุ่มบริการ+บริการ) × 4 key rows |
| Cross-sheet Total: รวมทั้งสิ้น ต้นทุน = หมวดบัญชี | 2 | 2 ระดับ × 4 key rows |
| Cross-sheet EBT + กำไรสุทธิ (Total + per-BU) | 1 | ยอดรวม + 8 BU |
| Cross-sheet EBT + กำไรสุทธิ (per-SG + per-Product) | 2 | ทุก SG + ทุก Product |
| Alliance: พันธมิตร + ไม่รวมพันธมิตร = รวมทั้งสิ้น | 1 | 4 sheets |
| Excel vs งบการเงิน SAP (pld_*.txt) | 3, 4 | Net Profit + Revenue |

**ถ้าทุกรายการข้างต้น PASS** → มั่นใจได้ว่า:

- ข้อมูลจาก CSV ถูกนำไปใส่ Excel report ถูกต้องทุก cell ทุก product
- EBIT/EBITDA คำนวณถูกต้อง
- คอลัมน์สรุปรวมถูกต้อง (sum ของ sub-group = summary)
- ต้นทุนบริการ กับ หมวดบัญชี ให้ยอดสุทธิตรงกัน (ดูข้อมูลต่างมุมแต่ bottom line เท่ากัน)
- Excel report ตรงกับงบการเงินจาก SAP

### 5.2 สิ่งที่ยังไม่ได้ตรวจ (ข้อจำกัด)

| สิ่งที่ยังไม่ได้ตรวจ | เหตุผล | ผลกระทบ |
| ------------------- | ------ | ------- |
| Cross-sheet revenue/expense per-SG/Product | ต้นทุน มี 14 GROUP, หมวดบัญชี มี 5 GROUP → ต้อง aggregate SUB_GROUP ก่อนถึงเทียบได้ | ถ้า EBT/กำไรสุทธิ per-SG ตรงกันแล้ว ความเสี่ยงต่ำ แต่อาจมี revenue/expense สลับกันได้โดย net ยังถูก |
| SUB_GROUP level (รายละเอียดย่อยในแต่ละ GROUP) | จำนวน check จะเพิ่มขึ้นมาก | CSV vs Excel ระดับ GROUP ครอบคลุมอยู่แล้ว — ถ้า GROUP ตรง SUB_GROUP ก็ต้องตรง (เว้นแต่มีการ map SUB_GROUP ผิด) |
| Common Size (สัดส่วนร้อยละ) | เป็นค่าที่คำนวณจากตัวเลข ไม่ใช่ข้อมูลต้นทาง | ถ้าตัวเลขถูก สัดส่วนก็ถูกอัตโนมัติ |
| แนวตั้ง: Product sum = SG sum = BU (จาก CSV) | ทำแค่ cross-column ใน Excel | ถ้า CSV vs Excel ถูกทั้ง Product และ SG level แล้ว ก็เท่ากับตรวจโดยอ้อม |

### 5.3 ระดับความมั่นใจ

| ระดับ | ความหมาย | เมื่อไหร่ |
| ----- | -------- | --------- |
| **สูงมาก** | ข้อมูลถูกต้องทุก cell | โปรแกรม 1+2 PASS ทั้งหมด (CSV vs Excel ทุกระดับ + EBIT/EBITDA + cross-column + column-total + cross-sheet) |
| **สูง** | ยอดรวมถูก แต่อาจมี cell ย่อยผิด | โปรแกรม 1 PASS (Total + per-BU) แต่ยังไม่ได้รัน โปรแกรม 2 |
| **ปานกลาง** | ยอดสุทธิตรงกับงบการเงิน | โปรแกรม 3-4 PASS แต่ยังไม่ได้รัน โปรแกรม 1-2 |
| **ต่ำ** | มีรายการ FAIL | ต้องตรวจสอบรายการที่ FAIL ทุกรายการ |

---

## 6. การอ่านผลลัพธ์

### 6.1 ผลลัพธ์บนหน้าจอ

```text
--- CSV vs Excel (MTH) - ต้นทุน_กลุ่มธุรกิจ ---
Check                                                | Source           | Excel            | Diff
-------------------------------------------------------------+------------------+------------------+---------------
รายได้รวมจากการให้บริการ (รวมทั้งสิ้น)                  | 1,500,000.00     | 1,500,000.00     | 0.00
กำไร(ขาดทุน) สุทธิ (รวมทั้งสิ้น)                       |   300,000.00     |   300,000.00     | 0.00
...
==========
Summary: 85 PASSED / 2 FAILED / 87 Total checks
```

- **PASS** = ผลต่างไม่เกิน 0.001 บาท (tolerance สำหรับ floating point)
- **FAIL** = ผลต่างเกิน tolerance -> ต้องตรวจสอบข้อมูลต้นทาง

### 6.2 ไฟล์ Excel ผลลัพธ์

ไฟล์ output จะมีหลาย Sheet:

| Sheet | เนื้อหา |
| ----- | ------- |
| **Summary** | จำนวน PASS / FAIL / อัตราผ่าน |
| **All Checks** | ผลตรวจสอบทุกรายการ |
| **Failed Checks** | เฉพาะรายการที่ FAIL (ถ้ามี) |

---

## 7. การแก้ไขปัญหา (Troubleshooting)

| อาการ | สาเหตุ | วิธีแก้ |
| ----- | ------ | ------- |
| `FileNotFoundError` | ไฟล์ไม่อยู่ในโฟลเดอร์ที่กำหนด | ตรวจสอบว่าวางไฟล์ใน `data/` และ `report/` แล้ว และชื่อไฟล์ตรงกับ config |
| `KeyError: 'ต้นทุน_กลุ่มธุรกิจ'` | ชื่อ Sheet ใน Excel ไม่ตรง | เปิด Excel ตรวจชื่อ Tab ด้านล่างให้ตรงกับค่าในโค้ด |
| ค่าเป็น 0 ทั้งหมด | ตำแหน่ง row/column เปลี่ยน | โครงสร้าง Excel เปลี่ยน ให้ตรวจ header row ใน Excel |
| `UnicodeDecodeError` | Encoding ไฟล์ CSV ไม่ตรง | โปรแกรมลอง utf-8, cp874, tis-620 อัตโนมัติ แต่ถ้ายังไม่ได้ให้ save CSV ใหม่เป็น UTF-8 |
| `ModuleNotFoundError` | ยังไม่ติดตั้ง library | รัน `pip install pandas openpyxl` |
| `--date` ไม่ได้ระบุ (โปรแกรม 4) | ต้องระบุ `--date` เสมอ | เพิ่ม `--date YYYYMMDD` เช่น `--date 20251231` |

---

## 8. ข้อมูลอ้างอิง

### ชีต Excel ที่ใช้

| ชื่อ Sheet | ใช้โดยโปรแกรม |
| ---------- | ------------- |
| ต้นทุน_กลุ่มธุรกิจ | 1 + 2 |
| ต้นทุน_กลุ่มบริการ | 1 + 2 |
| ต้นทุน_บริการ | 1 + 2 |
| หมวดบัญชี_กลุ่มธุรกิจ | 1 + 2 |
| หมวดบัญชี_กลุ่มบริการ | 1 + 2 |
| หมวดบัญชี_บริการ | 1 + 2 |

### Tolerance

ค่า tolerance = **0.001 บาท** (ยอมรับผลต่างจาก floating point) หากต้องการเปลี่ยน แก้ที่ `TOLERANCE = 0.001` ด้านบนของแต่ละไฟล์

### สูตรการคำนวณ

#### EBIT (Earnings Before Interest and Tax)

```text
COSTTYPE:
  EBIT = Revenue(GROUP 01) - Cost(02) - Selling(04) - Admin(06) - FinanceOp(07)

GLGROUP:
  EBIT = Revenue(GROUP 01) - Expense(GROUP 02) + FinanceOp(SUB_GROUP 19)
  (GROUP 02 รวม finance cost อยู่แล้ว → ต้องบวกกลับ)
```

#### EBITDA (Earnings Before Interest, Tax, Depreciation and Amortization)

```text
COSTTYPE:
  EBITDA = Revenue(GROUP 01,09) - Expense(GROUP 02,04,06,10) + Depreciation
  Depreciation = SUB_GROUP 12 (ค่าเสื่อมราคาฯ) + SUB_GROUP 13 (ค่าตัดจำหน่ายฯ)
                 จาก GROUP 02, 04, 06

GLGROUP:
  EBITDA = EBIT + Depreciation
  Depreciation = SUB_GROUP 12 + SUB_GROUP 13 จาก GROUP 02
```

---

## 9. ขั้นตอนการใช้งานสรุป (Quick Start)

```bash
# 1. เตรียมข้อมูล - copy CSV และ Excel report
cp ../data/TRN_PL_*_20260131.csv data/
cp ../output/Report_NT_202601.xlsx report/
cp ../output/Report_NT_YTD_202601.xlsx report/

# 2. แก้ config ใน reconcile_nt_pl.py และ reconcile_sg_svc_v2.py
#    (เปลี่ยนชื่อไฟล์ CSV และ Excel ให้ตรงกับงวด)

# 3. รัน
python reconcile_nt_pl.py
python reconcile_sg_svc_v2.py
python pl_reconciliation.py --date 20260131
python pl_reconciliation_enhanced.py --date 20260131

# 4. ดูผลลัพธ์
#    - หน้าจอ: ดู Summary ว่า PASS/FAIL เท่าไหร่
#    - ไฟล์: เปิด output/reconciliation_report_202512.xlsx
```
