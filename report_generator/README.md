# Univer Report Generator

ระบบสร้างรายงาน P&L Excel สำหรับ บริษัท โทรคมนาคมแห่งชาติ จำกัด (มหาชน)

## 📋 สารบัญ

- [คุณสมบัติ](#-คุณสมบัติ)
- [โครงสร้างโปรเจค](#-โครงสร้างโปรเจค)
- [การติดตั้ง](#-การติดตั้ง)
- [การใช้งาน](#-การใช้งาน)
- [การกำหนดค่า](#-การกำหนดค่า)
- [ไฟล์ข้อมูล](#-ไฟล์ข้อมูล)
- [การปรับแต่ง](#-การปรับแต่ง)
- [สถานะของไฟล์](#-สถานะของไฟล์)

---

## ✨ คุณสมบัติ

### รองรับ 2 มิติรายงาน
- **COSTTYPE** - มิติประเภทต้นทุน
- **GLGROUP** - มิติหมวดบัญชี

### รองรับ 2 ช่วงเวลา
- **MTH** - รายเดือน (Monthly)
- **YTD** - สะสมตั้งแต่ต้นปี (Year-to-Date)

### รองรับ 3 ระดับรายละเอียด
- **BU_ONLY** - กลุ่มธุรกิจเท่านั้น
- **BU_SG** - กลุ่มธุรกิจ + กลุ่มบริการ
- **BU_SG_PRODUCT** - กลุ่มธุรกิจ + กลุ่มบริการ + รายบริการ (default)

---

## 📁 โครงสร้างโปรเจค

```
report_generator/
├── generate_report.py      # ✅ Entry point หลัก (ใช้งานจริง)
├── main.py                 # ⚠️ สำหรับ CLI/Web mode (ต้อง refactor)
├── main_generator.py       # ❌ Legacy code (ไม่ใช้แล้ว)
├── .env                    # การตั้งค่าแบบ environment
├── requirements.txt        # Dependencies
│
├── config/                 # ⚙️ Configuration files
│   ├── settings.py         # ✅ ตั้งค่าหลัก (อ่านจาก .env)
│   ├── data_mapping.py     # ✅ COSTTYPE: Label → (GROUP, SUB_GROUP)
│   ├── data_mapping_glgroup.py  # ✅ GLGROUP: Label → (GROUP, SUB_GROUP)
│   ├── row_order.py        # ✅ COSTTYPE: ลำดับแถวและ formulas
│   ├── row_order_glgroup.py    # ✅ GLGROUP: ลำดับแถวและ formulas
│   ├── report_config.py    # ⚠️ Legacy (ใช้ core/config.py แทน)
│   └── types.py            # ✅ Enum definitions
│
├── data/                   # 📊 ข้อมูล Input
│   ├── TRN_PL_COSTTYPE_NT_MTH_TABLE_*.csv
│   ├── TRN_PL_COSTTYPE_NT_YTD_TABLE_*.csv
│   ├── TRN_PL_GLGROUP_NT_MTH_TABLE_*.csv
│   ├── TRN_PL_GLGROUP_NT_YTD_TABLE_*.csv
│   └── remark_YYYYMMDD.txt # หมายเหตุ (ชื่อตรงกับวันที่ CSV)
│
├── output/                 # 📤 ไฟล์ Output Excel
│
├── src/
│   ├── data_loader/        # ✅ โหลดและประมวลผลข้อมูล
│   │   ├── csv_loader.py       # อ่าน CSV
│   │   ├── data_processor.py   # ประมวลผล DataFrame
│   │   └── data_aggregator.py  # รวมค่าและคำนวณ
│   │
│   ├── report_generator/   # ✅ สร้างรายงาน Excel
│   │   ├── core/
│   │   │   ├── config.py       # ReportConfig, Enums
│   │   │   └── report_builder.py  # ตัวสร้างรายงานหลัก
│   │   ├── columns/            # สร้างโครงสร้างคอลัมน์
│   │   ├── rows/               # สร้างโครงสร้างแถว
│   │   ├── writers/            # เขียนลง Excel
│   │   └── formatters/         # จัดรูปแบบ cells
│   │
│   ├── cli/               # ⚠️ ต้อง refactor
│   │   ├── cli.py             # ❌ ใช้ ExcelGenerator เก่า
│   │   └── commands.py        # ⚠️ load_remark_file มี bug
│   │
│   ├── web/               # 🚧 ยังไม่ implement
│   └── calculators/       # 🚧 placeholder
│
├── archive/               # 📦 Code เก่าที่เก็บไว้
└── backup_*/              # 💾 Backups
```

---

## 🚀 การติดตั้ง

### 1. Clone และติดตั้ง dependencies

```bash
cd report_generator
pip install -r requirements.txt
```

### 2. ตั้งค่า .env (optional)

คัดลอก `.env.example` เป็น `.env` และปรับแต่งตามต้องการ:

```bash
cp .env.example .env
```

---

## 💻 การใช้งาน

### คำสั่งพื้นฐาน

```bash
# รายงาน COSTTYPE MTH (default)
python generate_report.py

# รายงาน GLGROUP YTD
python generate_report.py --report-type GLGROUP --period YTD

# ระบุระดับรายละเอียด
python generate_report.py --detail-level BU_SG

# ระบุไฟล์ CSV โดยตรง
python generate_report.py --csv-file data/TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv
```

### Options ทั้งหมด

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--csv-file` | | ไฟล์ CSV (auto-detect ถ้าไม่ระบุ) | - |
| `--data-dir` | | Directory ของข้อมูล | `data/` |
| `--output` | `-o` | ไฟล์ Output | auto-generated |
| `--output-dir` | | Directory สำหรับ output | `output/` |
| `--report-type` | `-t` | COSTTYPE หรือ GLGROUP | COSTTYPE |
| `--period` | `-p` | MTH หรือ YTD | MTH |
| `--detail-level` | `-d` | BU_ONLY, BU_SG, BU_SG_PRODUCT | BU_SG_PRODUCT |
| `--encoding` | | CSV encoding | tis-620 |
| `--verbose` | `-v` | แสดงรายละเอียด | False |

---

## ⚙️ การกำหนดค่า

### ไฟล์ .env

```ini
# === Application ===
APP_NAME="Univer Report Generator"
APP_ENV=development
DEBUG=True

# === Data Paths ===
DATA_DIR=data           # Directory ของไฟล์ CSV
OUTPUT_DIR=output       # Directory สำหรับ output

# === CSV Encoding ===
CSV_ENCODING=tis-620    # หรือ windows-874, cp874

# === Excel Formatting ===
EXCEL_FONT_NAME=TH Sarabun New
EXCEL_FONT_SIZE=18

# === Web Server (ถ้าใช้) ===
WEB_HOST=0.0.0.0
WEB_PORT=9000
```

### สิ่งที่อ่านจาก .env

| Variable | Description | Default |
|----------|-------------|---------|
| `DATA_DIR` | Directory ของไฟล์ CSV | `../data` |
| `OUTPUT_DIR` | Directory สำหรับ output | `./output` |
| `CSV_ENCODING` | Encoding ของไฟล์ CSV | `tis-620` |
| `EXCEL_FONT_NAME` | ฟอนต์ใน Excel | `TH Sarabun New` |
| `EXCEL_FONT_SIZE` | ขนาดฟอนต์ | `18` |

---

## 📊 ไฟล์ข้อมูล

### CSV Files (Input)

ไฟล์ CSV ต้องอยู่ใน `data/` directory โดยมีรูปแบบชื่อ:

```
TRN_PL_{REPORT_TYPE}_NT_{PERIOD}_TABLE_{YYYYMMDD}.csv

ตัวอย่าง:
- TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv
- TRN_PL_COSTTYPE_NT_YTD_TABLE_20251031.csv
- TRN_PL_GLGROUP_NT_MTH_TABLE_20251031.csv
- TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv
```

### Remark File

ไฟล์หมายเหตุต้องอยู่ใน `data/` directory โดยมีรูปแบบชื่อ:

```
remark_{YYYYMMDD}.txt

ตัวอย่าง:
- remark_20251031.txt
```

**สำคัญ:** วันที่ใน remark file ต้องตรงกับวันที่ใน CSV file

**Encoding:** รองรับ UTF-8, TIS-620, CP874, Windows-874

---

## 🔧 การปรับแต่ง

### 1. เพิ่ม/แก้ไขแถวรายงาน

#### COSTTYPE: แก้ไข `config/row_order.py`

```python
ROW_ORDER = [
    # (level, label, is_calculated, formula, is_bold)
    (0, "1.รายได้", False, None, True),
    (1, "รายได้บริการ", True, "sum_service_revenue", False),
    (2, "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน", False, None, False),
    ...
]
```

#### GLGROUP: แก้ไข `config/row_order_glgroup.py`

```python
ROW_ORDER_GLGROUP = [
    # (level, label, is_calculated, formula, is_bold)
    (0, "1 รวมรายได้", True, "sum_group_1", True),
    (1, "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน", False, None, False),
    ...
]
```

### 2. Mapping Labels กับ Database

#### COSTTYPE: แก้ไข `config/data_mapping.py`

```python
DATA_MAPPING = {
    "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน": ("01.รายได้", "01.รายได้จากการให้บริการ"),
    ...
}

# Context-dependent mappings
CONTEXT_MAPPING = {
    ("label", "parent_context"): ("GROUP", "SUB_GROUP"),
    ...
}
```

#### GLGROUP: แก้ไข `config/data_mapping_glgroup.py`

```python
DATA_MAPPING_GLGROUP = {
    "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน": ("01.รายได้", "01.รายได้จากการให้บริการ"),
    # บางรายการเป็น 3-tuple:
    "     - ผลตอบแทนทางการเงิน": ("01.รายได้", "10.ผลตอบแทนทางการเงิน", "8.1 ผลตอบแทนทางการเงิน"),
    ...
}
```

### 3. สีของกลุ่มธุรกิจ

แก้ไขใน `config/settings.py` หรือ `src/report_generator/core/config.py`:

```python
bu_colors: Dict[str, str] = {
    '1.กลุ่มธุรกิจ HARD INFRASTRUCTURE': 'E2EFDA',
    '2.กลุ่มธุรกิจ INTERNATIONAL': 'DDEBF7',
    ...
}
```

### 4. Formulas สำหรับ Calculated Rows

Formulas ที่รองรับ (กำหนดใน `row_order*.py`):

**COSTTYPE:**
- `sum_service_revenue` - รวมรายได้บริการ
- `sum_total_revenue` - รวมรายได้ทั้งหมด
- `sum_total_cost` - รวมค่าใช้จ่ายทั้งหมด
- `sum_service_cost_*` - รวมต้นทุนบริการต่างๆ
- `subtract_*` - ผลต่าง (รายได้ - ค่าใช้จ่าย)
- `ebitda` - EBITDA

**GLGROUP:**
- `sum_group_1` - รวมรายได้ (9 รายการ)
- `sum_group_2` - รวมค่าใช้จ่าย (19 รายการ)
- `sum_service_revenue` - รวมรายได้บริการ
- `total_expense_no_finance` - ค่าใช้จ่ายไม่รวมต้นทุนทางการเงิน
- `total_expense_with_finance` - ค่าใช้จ่ายรวมต้นทุนทางการเงิน
- `ebitda` - EBITDA

---

## 📋 สถานะของไฟล์

### ✅ ใช้งานจริง

| File | Description |
|------|-------------|
| `generate_report.py` | Entry point หลัก |
| `config/settings.py` | การตั้งค่าระบบ |
| `config/data_mapping.py` | COSTTYPE mappings |
| `config/data_mapping_glgroup.py` | GLGROUP mappings |
| `config/row_order.py` | COSTTYPE row definitions |
| `config/row_order_glgroup.py` | GLGROUP row definitions |
| `config/types.py` | Enum definitions |
| `src/data_loader/*` | Data loading modules |
| `src/report_generator/*` | Report generation modules |

### ⚠️ ต้องปรับปรุง

| File | Issue |
|------|-------|
| `main.py` | ใช้ cli.py ที่มีปัญหา |
| `src/cli/cli.py` | Import ExcelGenerator ที่ไม่มีแล้ว |
| `src/cli/commands.py` | `load_remark_file()` มี bug |
| `config/report_config.py` | Legacy (ใช้ `core/config.py` แทน) |

### ❌ ไม่ใช้แล้ว (ควรลบหรือย้าย)

| File | Reason |
|------|--------|
| `main_generator.py` | Legacy hardcoded version |
| `src/data_loader/*.bak` | Backup files |
| `archive/` | Old implementations |
| `backup_*/` | Old backups |

### 🚧 ยังไม่ implement

| File | Status |
|------|--------|
| `src/web/*` | Placeholder (FastAPI web interface) |
| `src/calculators/*` | Placeholder |

---

## 🔄 เมื่อข้อมูลเปลี่ยนแปลง

### เมื่อมี CSV ใหม่

1. วางไฟล์ CSV ใน `data/` directory
2. สร้าง remark file ใหม่ (ถ้ามี): `remark_YYYYMMDD.txt`
3. รัน `python generate_report.py` (auto-detect ไฟล์ล่าสุด)

### เมื่อมีแถวรายงานใหม่

1. เพิ่ม mapping ใน `config/data_mapping*.py`
2. เพิ่ม row definition ใน `config/row_order*.py`
3. ถ้าเป็น calculated row ต้องเพิ่ม logic ใน `data_aggregator.py`

### เมื่อมีกลุ่มธุรกิจใหม่

1. เพิ่มสีใน `bu_colors` ของ `config/settings.py`
2. ตรวจสอบว่า CSV มีค่า BU ใหม่

---

## 📝 Notes

- **Encoding:** ไฟล์ CSV จาก SAP ใช้ TIS-620 encoding
- **Font:** ต้องติดตั้ง TH Sarabun New ในเครื่อง
- **Output:** ไฟล์ output จะสร้างชื่ออัตโนมัติพร้อม timestamp

---

## 📞 Support

สำหรับปัญหาหรือคำถาม กรุณาติดต่อทีมพัฒนา
