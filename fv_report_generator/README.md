# FV Report Generator

สร้างรายงาน VCFC (Variable/Fixed Cost) Y2568 งวด P14 ตามแบบ sheet `Report_P14` ในไฟล์ `Report_FV_Y2568(P14).XLSX` จากข้อมูล data-warehouse CSV `TRN_FV_Datawarehouse_Y*(P*).csv`

Pipeline: CSV (long format) → canonicalize labels → pivot by row_key × col_key → copy template file → clear data area → fill cells. Header formatting, merged cells, สี, font ถูก preserve จาก template

## โครงสร้าง

```
fv_report_generator/
├── generate_fv_report.py       # CLI entry point
├── src/
│   ├── data_loader.py          # CSV loader (reuse report_generator.CSVLoader + fallback encoding)
│   ├── normalizer.py           # Canonical form สำหรับ match label ระหว่าง CSV กับ template
│   ├── template_reader.py      # แกะ row/col hierarchy + merged ranges จาก Report_P14 sheet
│   ├── satellite_split.py      # NT vs ไทยคม split (reuse report_generator/config/satellite_config.py)
│   ├── pivoter.py              # Long → wide pivot, aggregate ที่ทุกระดับ (GRAND / BU / SG / SUBSG / PRODUCT)
│   ├── derived.py              # Compute %กำไรส่วนเกิน = contribution margin / revenue
│   ├── writer.py               # Template-copy writer: clear data area + set cells
│   └── reconciler.py           # เทียบ CSV pivot กับ sheet Data_P14
├── tests/                      # pytest
└── output/                     # generated .xlsx files
```

## การใช้งาน

```bash
python3 generate_fv_report.py \
    --csv-file "/path/TRN_FV_Datawarehouse_Y2568(P14).csv" \
    --template "/path/Report_FV_Y2568(P14).XLSX" \
    --output "output/Report_FV_P14.xlsx" \
    --reconcile
```

- `--period-key` auto-inferred จาก filename (รองรับ Buddhist Era: `Y2568 → 2025`)
- `--reconcile` (optional) เทียบ pivot กับ sheet Data_P14 → log mismatches ถ้ามี
- `--sheet` (default `Report_P14`) กรณี template ใช้ชื่อ sheet อื่น

## Run tests

```bash
python3 -m pytest tests/ -v
```

## Design decisions

- **Template-copy writer** เลือกวิธีนี้แทนการ write workbook ใหม่ทั้งหมด เพราะ header 5 แถว + 78 merged ranges + font TH Sarabun New + สี BU จะ preserve ให้อัตโนมัติ — เราเพียง clear data area (rows 10+, cols C+) แล้ว fill ค่าใหม่เท่านั้น
- **Canonical labels** ใช้ normalizer กลาง (`src/normalizer.py`) ที่ strip numeric prefix (`4.5.1`, `01.`), VC/FC suffix, punctuation differences (`(1)-(2)` vs `(1) (2)`), และ whitespace ให้ CSV กับ template match กัน
- **Reuse จาก `report_generator/`**: `CSVLoader` สำหรับ TIS-620/CP874 encoding fallback, และ `config/satellite_config.py` สำหรับ NT/ไทยคม split mapping
- **Percent row (`%กำไรส่วนเกิน`)** คำนวณหลัง fill row อื่นแล้ว (ratio = row78/row10) เพราะ sum percentage ไม่มี meaning
- **Row label alias** เช่น template row 139 "5. กำไร(ขาดทุน)ก่อนต้นทุนจัดหาเงิน..." จับคู่กับ CSV GROUP "05.ต้นทุนจัดหาเงิน..." ผ่าน explicit map ใน `template_reader._ROW_LABEL_ALIASES`
- **SG truncation alias** template บาง SG (`5.4 APPLICATION & DIGITAL SE`) ถูก truncate เทียบกับ CSV → pivoter build prefix-match alias อัตโนมัติ

## Known differences vs. original Report_P14

รัน `--reconcile` แล้ว 0 value mismatches กับ Data_P14 แต่ output มี diffs กับ Report_P14 ดังนี้ (ไม่ใช่ bug):

- **Row 147 (กำไรสุทธิ) แบ่ง per BU/product**: CSV มีข้อมูลครบ generator จึง populate หมด แต่ template เดิมเว้น cell ส่วนใหญ่ไว้
- **Row 140/141/142 (ผลตอบแทนทางการเงิน + รายได้อื่น)**: template แสดง 716M (318M + 398M) แต่ CSV GROUP 06 ทั้งหมด = 762M → มี 46M ที่ template หักออก (manual adjustment)
- **Row 143 (ค่าใช้จ่ายอื่น)**: คล้ายกัน CSV = 141M vs template = 96M

ถ้าต้องการ match template 1:1 อย่างเคร่ง ต้องเพิ่ม override layer สำหรับ manual adjustments เหล่านี้
