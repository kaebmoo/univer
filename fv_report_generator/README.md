# FV Report Generator

สร้างรายงานต้นทุนคงที่/ผันแปร (VCFC) แบบ **data-driven** จาก CSV ของ data-warehouse `TRN_FV_Datawarehouse_Y*(P*).csv` โครงสร้างของรายงาน — ทั้ง row, column, header, สี BU, format ตัวเลข — สร้างจากข้อมูลใน CSV ทั้งหมด ไม่ต้องใช้ template Excel เลย

เมื่อข้อมูลใน CSV เปลี่ยน (มี product เพิ่ม/ลด, มี row ใหม่ เช่น ER, มี SG/BU เปลี่ยน) รายงานจะปรับโครงสร้างให้อัตโนมัติ ไม่ต้องแก้ template ด้วยมือ

## ติดตั้ง

ต้องการ Python 3.10 ขึ้นไป

```bash
cd fv_report_generator

# (แนะนำ) สร้าง virtual environment
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate            # Windows

# ติดตั้ง dependency
pip install -r requirements.txt
```

`requirements.txt` มีแค่ 3 ตัว: `pandas`, `openpyxl`, `pytest`

## การใช้งาน

```bash
python3 generate_fv_report.py \
    --csv-file "/path/to/TRN_FV_Datawarehouse_Y2568(P14).csv" \
    --output output/Report_FV_P14.xlsx
```

- `--period-key` (optional) — TIME_KEY ที่จะ filter เช่น `202514` ถ้าไม่ระบุจะ infer จากชื่อไฟล์ (รองรับ Buddhist Era: `Y2568 → 2025`)
- `--encoding` (default `tis-620`) — encoding ของ CSV; มี fallback อัตโนมัติเป็น `cp874` / `utf-8-sig` / `utf-8`
- `--reconcile-against <Report_FV_*.XLSX>` (optional) — เทียบค่า pivot กับ sheet `Data_P14` ของไฟล์ template เพื่อ QA หา value mismatch
- `--sheet` (default `Report_P14`) — ชื่อ sheet ที่จะเขียนใน workbook ใหม่
- `-v` — verbose log

ตัวอย่างพร้อม reconcile:

```bash
python3 generate_fv_report.py \
    --csv-file "/path/to/TRN_FV_Datawarehouse_Y2568(P14).csv" \
    --output output/Report_FV_P14.xlsx \
    --reconcile-against "/path/to/Report_FV_Y2568(P14).XLSX"
```

## โครงสร้าง

```
fv_report_generator/
├── generate_fv_report.py       # CLI entry point
├── src/
│   ├── data_loader.py          # CSV loader (รองรับ TIS-620 / CP874 / UTF-8)
│   ├── normalizer.py           # canonical(label) / canonical_product_key()
│   ├── satellite_split.py      # 4.5 SATELLITE → NT / ไทยคม mapping
│   ├── aggregator.py           # CSV → {(row_key, col_key): value} + enumerate helpers
│   ├── column_builder.py       # BU → SG → SUBSG → PRODUCT column structure
│   ├── row_builder.py          # GROUP → SUB_GROUP1 → SUB_GROUP2 row structure
│   ├── derived.py              # %กำไรส่วนเกิน = section3 / section1 ต่อ column
│   ├── config.py               # FVConfig (font, BU colors, layout)
│   ├── report_builder.py       # Orchestrator
│   ├── reconciler.py           # QA: เทียบกับ sheet Data_P14
│   └── writers/                # cell_formatter, header_writer, column_header_writer, data_writer
├── tests/
└── output/
```

## รัน tests

```bash
python3 -m pytest tests/ -v
```

ถ้ามีไฟล์ CSV + Report_FV ที่ `/Users/seal/Documents/NT/Report/vcfc/` test `test_reconcile_end_to_end.py` จะรัน end-to-end เทียบกับ Data_P14 ด้วย; ถ้าไม่มีจะถูก skip โดยอัตโนมัติ

## Design decisions

- **Data-driven structure** — โครงรายงานสร้างจากเนื้อหาใน CSV ทั้งหมด ไม่อ่าน template ตอน runtime ทำให้รายงานสะท้อนข้อมูลจริงเสมอ และรองรับ schema ที่เปลี่ยนไปตามงวด
- **Permissive row/column emission** — ถ้า CSV มี row/product ใหม่ที่ไม่เคยมี → emit เพิ่มท้าย section ที่ตรง; ถ้า CSV ไม่มี product/row ที่เคยมี → ไม่ emit เลย (ไม่มี cell ว่างทิ้ง)
- **Percent row recomputation** — `%กำไรส่วนเกิน` คำนวณ per column จาก `section3 / section1` แทนที่จะ sum (CSV's GROUP `33.` เก็บ % per-product ที่ไม่ summable จึงถูก drop ออก)
- **Satellite split** — SG `4.5 SATELLITE` ถูกแยกเป็น 4.5.1 (NT) / 4.5.2 (ไทยคม) ตาม `report_generator/config/satellite_config.py` (reuse ผ่าน `satellite_split.py`)
- **Reuse จาก `report_generator/`** — `CSVLoader` (Thai encoding fallback) และ `satellite_config` (NT/ไทยคม mapping) ใช้ผ่าน `sys.path` injection
- **Reconciliation ยังเป็น optional** — `--reconcile-against` ใช้ template สำหรับ QA เท่านั้น ไม่ใช่ในการ generate

## Output format

- 5-row column header: BU / SG / SUBSG / PRODUCT_KEY / PRODUCT_NAME
- Number format: accounting style — positive `1,234.00`, negative red `(1,234.00)`, zero blank
- Percent row: `0.00%`
- Font: TH Sarabun New 14
- BU coloring + merged header cells preserved
- Title rows (B1/B2/B3) ชิดซ้าย
