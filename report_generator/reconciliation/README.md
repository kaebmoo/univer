# Reconciliation - ตรวจกระทบยอด P&L

ระบบตรวจกระทบยอดระหว่าง CSV source data กับ Excel report ของ NT P&L

## โครงสร้างโฟลเดอร์

```text
reconciliation/
├── reconcile_nt_pl.py             # โปรแกรม 1: ระดับ BU + ข้ามชีต + พันธมิตร
├── reconcile_sg_svc_v2.py         # โปรแกรม 2: ระดับ Service Group + Product + EBIT/EBITDA
├── pl_reconciliation.py           # โปรแกรม 3: ตรวจกับงบการเงิน (basic)
├── pl_reconciliation_enhanced.py  # โปรแกรม 4: ตรวจกับงบการเงิน (enhanced, 3 modes)
├── pl_reconciliation_combined.py  # โปรแกรม 5: ตรวจ combined output
├── manual.md                      # คู่มือละเอียด
├── manual.pdf                     # คู่มือ PDF (เวอร์ชันเก่า)
├── README.md                      # คู่มือนี้
│
├── data/                          # ข้อมูล input ทั้งหมด
│   ├── TRN_PL_*_TABLE_*.csv       #   - CSV source data
│   ├── pld_nt_*.txt               #   - งบการเงิน (financial statements)
│   └── pl_combined_output_*.xlsx  #   - combined output files
│
├── report/                        # Excel report ที่จะตรวจ (copy จาก output/ มาที่นี่)
│   ├── Report_NT_*.xlsx           #   - รายเดือน (MTH)
│   └── Report_NT_YTD_*.xlsx       #   - สะสม (YTD)
│
├── output/                        # ผลลัพธ์ (สร้างอัตโนมัติ)
│
└── archive/                       # ไฟล์เก่า
    └── Automated_Reconciliation.py
```

---

## สรุป Python Scripts

### โปรแกรมหลัก (ตรวจ CSV vs Excel Report)

| Script | ระดับการตรวจ | การตั้งค่า |
| ------ | ------------ | ---------- |
| `reconcile_nt_pl.py` | BU total (ทุก GROUP row × 8 BU), ข้ามชีต (ต้นทุน vs หมวดบัญชี ทั้ง total + per-BU), Column-Total, พันธมิตร | `--date YYYYMMDD` |
| `reconcile_sg_svc_v2.py` | Service Group, Product, EBIT, EBITDA, Cross-column, Column-Total, Cross-sheet Total + per-SG/Product | `--date YYYYMMDD` |

### โปรแกรมเสริม (ตรวจกับงบการเงิน)

| Script | หน้าที่ | การตั้งค่า |
| ------ | ------- | ---------- |
| `pl_reconciliation.py` | ตรวจ 3 checkpoints (Consistency, Accuracy, Tie-out) | `--date YYYYMMDD` |
| `pl_reconciliation_enhanced.py` | ตรวจ 3 modes: BASIC / ENHANCED / COMPREHENSIVE | `--date YYYYMMDD` |
| `pl_reconciliation_combined.py` | ตรวจ combined output | แก้ config ใน main() |

---

## การเตรียมไฟล์

### ขั้นตอนที่ 1: วาง CSV source data

Copy CSV จากระบบ SAP มาไว้ใน `data/` (**ต้องเป็น encoding TIS-620 หรือ CP874**):

```text
data/
├── TRN_PL_COSTTYPE_NT_MTH_TABLE_20260131.csv
├── TRN_PL_COSTTYPE_NT_YTD_TABLE_20260131.csv
├── TRN_PL_GLGROUP_NT_MTH_TABLE_20260131.csv
├── TRN_PL_GLGROUP_NT_YTD_TABLE_20260131.csv
└── pld_nt_20260131.txt    (งบการเงิน - ถ้ามี)
```

**สำคัญ:** ไฟล์ CSV ต้อง**ใช้ไฟล์เดียวกัน**กับที่ report generator ใช้ (`report_generator/data/`) เพื่อให้ข้อมูลตรงกัน:

```bash
# copy CSV จาก report_generator/data/ มาที่ reconciliation/data/
cp ../data/TRN_PL_*_20260131.csv data/
```

### ขั้นตอนที่ 2: Copy Excel report

Copy ไฟล์ Excel report ที่ generate แล้วมาไว้ใน `report/`:

```bash
cp ../output/Report_NT_202601.xlsx report/
cp ../output/Report_NT_YTD_202601.xlsx report/
```

ทุกโปรแกรมใช้ `report/` เป็นที่อ่าน Excel report เหมือนกันหมด

---

## วิธีรัน

```bash
cd report_generator/reconciliation

# โปรแกรม 1 - ระดับ BU + ข้ามชีต + Column-Total + พันธมิตร
python reconcile_nt_pl.py --date 20260131

# โปรแกรม 2 - ระดับ SG + Product + EBIT/EBITDA + Cross-column + Column-Total + Cross-sheet
python reconcile_sg_svc_v2.py --date 20260131

# โปรแกรม 3 - ตรวจกับงบการเงิน (basic)
python pl_reconciliation.py --date 20260131

# โปรแกรม 4 - ตรวจกับงบการเงิน (enhanced)
python pl_reconciliation_enhanced.py --date 20260131
python pl_reconciliation_enhanced.py --date 20260131 --mode comprehensive

# โปรแกรม 5 - ตรวจ combined output
python pl_reconciliation_combined.py
```

หมายเหตุ: สามารถ `cd` ไปที่โฟลเดอร์ไหนก็ได้แล้วรัน เพราะโปรแกรมใช้ `Path(__file__)` อ้างอิงตำแหน่ง script เสมอ

---

## การตั้งค่า

### โปรแกรม 1-4: ใช้ --date (ไม่ต้องแก้โค้ด)

```bash
python reconcile_nt_pl.py --date 20260131
python reconcile_sg_svc_v2.py --date 20260131
python pl_reconciliation.py --date 20260131
python pl_reconciliation_enhanced.py --date 20260131
```

โปรแกรมจะสร้างชื่อไฟล์ CSV และ Excel อัตโนมัติจากวันที่ที่ระบุ
สามารถระบุชื่อไฟล์ Excel เองได้ด้วย `--excel-mth` / `--excel-ytd`

### โปรแกรม 5: แก้ config ใน main()

เปิด `pl_reconciliation_combined.py` แก้ชื่อไฟล์ใน function `main()`

---

## การอ่านผลลัพธ์

- **PASS** = ผลต่างไม่เกิน 0.001 บาท (tolerance สำหรับ floating point)
- **FAIL** = ผลต่างเกิน tolerance -> ต้องตรวจสอบข้อมูลต้นทาง

ไฟล์ output Excel (โปรแกรม 1-2) จะมี 3 sheets:

| Sheet | เนื้อหา |
| ----- | ------- |
| Summary | จำนวน PASS / FAIL / อัตราผ่าน |
| All Checks | ผลตรวจสอบทุกรายการ |
| Failed Checks | เฉพาะรายการที่ FAIL (ถ้ามี) |

---

## ระดับความน่าเชื่อถือ

| ระดับ | เมื่อไหร่ | ความหมาย |
| ----- | --------- | -------- |
| **สูงมาก** | โปรแกรม 1+2 PASS ทั้งหมด | ข้อมูลถูกต้องทุก cell ทุก product ทั้ง 2 มุมมอง |
| **สูง** | โปรแกรม 1 PASS | ยอดรวมถูก แต่อาจมี cell ย่อยระดับ SG/Product ผิด |
| **ปานกลาง** | โปรแกรม 3-4 PASS | ยอดสุทธิตรงกับงบการเงิน SAP แต่ยังไม่ได้ตรวจรายละเอียด |

> รายละเอียดสิ่งที่ตรวจ/ไม่ได้ตรวจ ดูที่ `manual.md` section 5

---

## ข้อควรระวัง

### Encoding ของไฟล์ CSV

ไฟล์ CSV จาก SAP ต้องเป็น **TIS-620 หรือ CP874** ถ้า encoding ผิด (เช่น ถูก save เป็น UTF-8 แล้วภาษาไทยเสีย) จะทำให้:

- Report generator สร้าง report ที่มีค่า 0 ทั้งหมด
- Reconciliation match GROUP/BU ไม่ได้

วิธีตรวจ: ถ้าเปิด CSV แล้วเห็น `๏ฟฝ` หรือ `�` แทนภาษาไทย แสดงว่า encoding เสีย ต้อง export ใหม่จาก SAP

### ใช้ CSV ชุดเดียวกัน

**ไฟล์ CSV ใน `reconciliation/data/` ต้องเป็นไฟล์เดียวกันกับที่ `report_generator/data/` ใช้** มิฉะนั้นข้อมูลจะไม่ตรงกับ report ที่ generate ออกมา

---

## Prerequisites

```bash
pip install pandas openpyxl
```

Library อื่นที่ใช้ (pathlib, dataclasses, datetime, argparse, json, re, typing) เป็น built-in ของ Python ไม่ต้องติดตั้งเพิ่ม
