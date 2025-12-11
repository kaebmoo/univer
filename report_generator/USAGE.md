# Quick Reference: Report Generation

## การใช้งาน

### Syntax
```bash
./run_reports.sh [YYYYMM] [PERIOD]
run_reports.bat [YYYYMM] [PERIOD]
```

**Parameters:**
- `YYYYMM` (optional): เดือนที่ต้องการ เช่น 202509
- `PERIOD` (optional): งวดที่ต้องการ MTH หรือ YTD

---

## ตัวอย่างการใช้งาน

### 1. ทุกเดือน + ทั้ง MTH และ YTD (ค่าเริ่มต้น)

```bash
./run_reports.sh
```

**ผลลัพธ์:** สแกนหา CSV ทุกเดือนใน data/ และสร้างทั้ง MTH และ YTD
- `Report_NT_202509.xlsx`, `Report_NT_202511.xlsx`
- `Report_NT_YTD_202509.xlsx`, `Report_NT_YTD_202511.xlsx`

### 2. เดือนเดียว + ทั้ง MTH และ YTD

```bash
./run_reports.sh 202509
```

**ผลลัพธ์:** สร้างเฉพาะเดือน 202509 ทั้ง MTH และ YTD
- `Report_NT_202509.xlsx`
- `Report_NT_YTD_202509.xlsx`

### 3. ทุกเดือน + เฉพาะ YTD

```bash
./run_reports.sh "" YTD
```

**ผลลัพธ์:** สร้างทุกเดือนแต่เฉพาะ YTD
- `Report_NT_YTD_202509.xlsx`, `Report_NT_YTD_202511.xlsx`

### 4. เดือนเดียว + เฉพาะ MTH

```bash
./run_reports.sh 202509 MTH
```

**ผลลัพธ์:** สร้างเฉพาะเดือน 202509 และเฉพาะ MTH
- `Report_NT_202509.xlsx`

---

## รันเฉพาะการรวมรายงาน (Concatenate Only)

หากมีไฟล์รายงานแยกอยู่แล้ว สามารถรันเฉพาะส่วนรวมรายงานได้:

### ทุกเดือน
```bash
python3 report_concat.py
```

### เฉพาะเดือน
```bash
python3 report_concat.py --month 202509
```

---

## ตัวอย่างผลลัพธ์

```
output/
├── PL_COSTTYPE_MTH_BU_ONLY_202509.xlsx
├── PL_COSTTYPE_MTH_BU_ONLY_202511.xlsx
├── ...
├── Report_NT_202509.xlsx              ← รายงาน MTH เดือน 09
├── Report_NT_202511.xlsx              ← รายงาน MTH เดือน 11
├── Report_NT_YTD_202509.xlsx          ← รายงาน YTD เดือน 09
└── Report_NT_YTD_202511.xlsx          ← รายงาน YTD เดือน 11
```

---

## เมื่อไหร่ควรใช้แบบไหน?

| สถานการณ์ | คำสั่งที่แนะนำ |
|----------|----------------|
| สร้างรายงานทุกเดือน ทั้ง MTH และ YTD | `./run_reports.sh` |
| สร้างรายงานเฉพาะเดือนเดียว | `./run_reports.sh 202509` |
| สร้างเฉพาะ YTD ทุกเดือน | `./run_reports.sh "" YTD` |
| สร้างเฉพาะ MTH เดือนเดียว | `./run_reports.sh 202509 MTH` |
| รวมรายงานใหม่ (ทุกเดือน) | `python3 report_concat.py` |
| รวมรายงานใหม่ (เฉพาะเดือน) | `python3 report_concat.py --month 202509` |

---

## ข้อควรระวัง

1. **ไม่ระบุเดือน**:
   - สร้างรายงานทุกเดือนที่มี CSV ใน data/
   - ใช้เวลานานกว่า (สัดส่วนกับจำนวนเดือน)
   - เหมาะสำหรับการสร้างรายงานครั้งแรกหรืออัปเดตทุกเดือน

2. **ระบุเดือน**:
   - รวดเร็ว สร้างเฉพาะเดือนที่ต้องการ
   - เหมาะสำหรับรายงานย้อนหลังหรือแก้ไขเฉพาะเดือน

3. **Overwrite**: ไฟล์ผลลัพธ์ที่ชื่อซ้ำจะถูกเขียนทับ

---

## ดูเอกสารเพิ่มเติม

- [README_run_reports.md](README_run_reports.md) - คู่มือฉบับเต็ม
- [README_report_concat.md](README_report_concat.md) - รายละเอียด report_concat.py
