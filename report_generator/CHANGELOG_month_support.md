# Changelog: เพิ่มการรองรับ --month parameter

## วันที่: 11 ธันวาคม 2025

## สรุปการเปลี่ยนแปลง

เพิ่มการรองรับ `--month` parameter ใน `generate_report.py` เพื่อให้สามารถเลือกไฟล์ CSV ตามเดือนที่ระบุได้

---

## ไฟล์ที่แก้ไข

### 1. `generate_report.py`

**การเปลี่ยนแปลง:**

#### 1.1 เพิ่ม import
```python
from typing import Optional
```

#### 1.2 เพิ่ม `--month` parameter ใน argparse (line ~180-185)
```python
parser.add_argument(
    '--month',
    '-m',
    type=str,
    help='Specific month to process (YYYYMM format, e.g., 202509). Only used when --csv-file is not specified.'
)
```

#### 1.3 แก้ไข `find_csv_file()` function (line ~52-93)
```python
def find_csv_file(data_dir: Path, report_type: str, period_type: str, month: Optional[str] = None) -> Path:
    """
    Find the most recent CSV file matching criteria

    Args:
        data_dir: Directory to search for CSV files
        report_type: Report type (COSTTYPE or GLGROUP)
        period_type: Period type (MTH or YTD)
        month: Optional month filter in YYYYMM format (e.g., '202509')

    Returns:
        Path to the selected CSV file
    """
    pattern = f"*{report_type}*{period_type}*.csv"
    files = sorted(data_dir.glob(pattern), reverse=True)

    if not files:
        raise FileNotFoundError(...)

    # If month is specified, filter files by month
    if month:
        filtered_files = [f for f in files if month in f.name]

        if not filtered_files:
            raise FileNotFoundError(
                f"No CSV file found for month {month}\n"
                f"Available files: {[f.name for f in files[:3]]}"
            )

        return filtered_files[0]

    # No month filter - return most recent file
    return files[0]
```

#### 1.4 ส่ง month parameter ไปยัง find_csv_file() (line ~260-262)
```python
if args.month:
    logging.info(f"   Month Filter: {args.month}")
csv_path = find_csv_file(args.data_dir, args.report_type, args.period, args.month)
```

---

## การทำงานใหม่

### กรณีไม่ระบุ `--month` (Backward Compatible)
```bash
python generate_report.py --report-type GLGROUP --period YTD --detail-level BU_ONLY
```

**พฤติกรรม:**
- ค้นหาไฟล์ CSV ทั้งหมดที่ตรง pattern `*GLGROUP*YTD*.csv`
- เรียงลำดับจากมากไปน้อย (reverse=True)
- **เลือกไฟล์แรก = ไฟล์ล่าสุด**
- ตัวอย่าง: มีไฟล์ `20250930.csv` และ `20251130.csv` → เลือก `20251130.csv`

### กรณีระบุ `--month 202509`
```bash
python generate_report.py --report-type GLGROUP --period YTD --detail-level BU_ONLY --month 202509
```

**พฤติกรรม:**
- ค้นหาไฟล์ CSV ที่ตรง pattern `*GLGROUP*YTD*.csv`
- **กรองเฉพาะไฟล์ที่มี `202509` ในชื่อไฟล์**
- เลือกไฟล์แรกจากผลการกรอง
- ตัวอย่าง: เลือก `TRN_PL_GLGROUP_NT_YTD_TABLE_20250930.csv`

### กรณี Error (ไม่พบเดือนที่ระบุ)
```bash
python generate_report.py --month 202412
```

**Output:**
```
❌ Error: No CSV file found for month 202412
Pattern: *GLGROUP*YTD*.csv
Search directory: data
Available files: ['TRN_PL_GLGROUP_NT_YTD_TABLE_20251130.csv', 'TRN_PL_GLGROUP_NT_YTD_TABLE_20250930.csv']
```

---

## การทดสอบ

### ✅ Test Case 1: ไม่ระบุเดือน (Backward Compatible)
```bash
python3 generate_report.py --report-type GLGROUP --period YTD --detail-level BU_ONLY
```
**ผลลัพธ์:** ✅ เลือก `TRN_PL_GLGROUP_NT_YTD_TABLE_20251130.csv` (ไฟล์ล่าสุด)

### ✅ Test Case 2: ระบุเดือน 202509
```bash
python3 generate_report.py --report-type GLGROUP --period YTD --detail-level BU_ONLY --month 202509
```
**ผลลัพธ์:** ✅ เลือก `TRN_PL_GLGROUP_NT_YTD_TABLE_20250930.csv` และสร้าง `PL_GLGROUP_YTD_BU_ONLY_202509.xlsx`

### ✅ Test Case 3: ระบุเดือน 202511
```bash
python3 generate_report.py --report-type GLGROUP --period YTD --detail-level BU_ONLY --month 202511
```
**ผลลัพธ์:** ✅ เลือก `TRN_PL_GLGROUP_NT_YTD_TABLE_20251130.csv` และสร้าง `PL_GLGROUP_YTD_BU_ONLY_202511.xlsx`

### ✅ Test Case 4: เดือนที่ไม่มี (Error Handling)
```bash
python3 generate_report.py --report-type GLGROUP --period YTD --detail-level BU_ONLY --month 202412
```
**ผลลัพธ์:** ✅ แสดง error message พร้อมรายการไฟล์ที่มีอยู่

---

## Backward Compatibility

✅ **100% Backward Compatible**

- การทำงานแบบเดิม (ไม่ระบุ `--month`) ยังคงทำงานเหมือนเดิมทุกประการ
- `--month` เป็น optional parameter (default = None)
- ไม่กระทบกับ `--csv-file` parameter (ถ้าระบุ `--csv-file` จะไม่ใช้ `--month`)

---

## การใช้งานร่วมกับ run_reports.sh

สคริปต์ `run_reports.sh` และ `run_reports.bat` ได้รับการปรับปรุงให้:
1. สแกนหาเดือนทั้งหมดจากไฟล์ CSV ใน data/
2. สร้างรายงานทุกเดือนหรือเฉพาะเดือนที่ระบุ
3. รวมรายงานทุกเดือนหรือเฉพาะเดือนที่ระบุ

**ตัวอย่าง:**
```bash
# ไม่ระบุเดือน - สแกนหาทุกเดือนใน data/ และสร้างทุกเดือน
./run_reports.sh
# Output: สร้าง 202509 และ 202511 (ถ้ามี CSV ทั้ง 2 เดือน)

# ระบุเดือน - สร้างเฉพาะเดือน 202509
./run_reports.sh 202509
# Output: สร้างเฉพาะ 202509
```

**การทำงานของ run_reports.sh แบบไม่ระบุเดือน:**
1. สแกนไฟล์ CSV ใน data/ → พบ 202509, 202511
2. รัน generate_report.py 12 ครั้งต่อเดือน (6 YTD + 6 MTH) × 2 เดือน = 24 ไฟล์
3. รัน report_concat.py → รวมเป็น 4 ไฟล์ (2 MTH + 2 YTD)

---

## ข้อควรระวัง

1. **Format ของ --month**: ต้องเป็น YYYYMM (6 หลัก) เท่านั้น
2. **Case Sensitive**: การค้นหาเป็น case-sensitive
3. **Partial Match**: ค้นหาจาก substring ไม่ใช่ exact match (เช่น `202509` จะตรงกับ `20250930`)
4. **ลำดับความสำคัญ**: ถ้าระบุทั้ง `--csv-file` และ `--month` → ใช้ `--csv-file` (ignore `--month`)

---

## สรุป

การเพิ่ม `--month` parameter ทำให้:
- ✅ สามารถเลือกไฟล์ CSV ตามเดือนได้
- ✅ รองรับการสร้างรายงานย้อนหลัง
- ✅ ไม่กระทบกับการทำงานเดิม (Backward Compatible)
- ✅ Error handling ชัดเจน
- ✅ ทำงานร่วมกับ `run_reports.sh` ได้สมบูรณ์
