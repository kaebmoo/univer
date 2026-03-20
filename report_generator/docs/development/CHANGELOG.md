# Changelog

## [Unreleased] - 2024-11-30

### Added ✨
- **Common Size Feature** - เพิ่มการคำนวณ Common Size (% ต่อรายได้รวม) เฉพาะกลุ่มธุรกิจ
  - คำนวณโดยหารตัวเลขแต่ละบรรทัดด้วย "รายได้รวม"
  - แสดงผล: 0 = blank, บวก = 42.00%, ลบ = (42.00%) สีแดง
  - ตำแหน่ง: Column Common Size อยู่ถัดจาก column จำนวนเงิน
  - ยกเว้นบรรทัด "สัดส่วนต่อรายได้"
  - รองรับทั้ง COSTTYPE และ GLGROUP
  
- **Command Line Options**
  - `--common-size`: บังคับเปิด Common Size
  - `--no-common-size`: ปิด Common Size
  - Default: BU_ONLY มี Common Size อัตโนมัติ, ระดับอื่นไม่มี

### Changed 🔄
- **ReportConfig** (`src/report_generator/core/config.py`)
  - เพิ่ม field `include_common_size: Optional[bool]`
  - แก้ไข `__post_init__()` ให้ auto-detect ตาม detail_level

- **BaseColumnBuilder** (`src/report_generator/columns/base_column_builder.py`)
  - เพิ่ม method `_create_common_size_column()`

- **BUOnlyBuilder** (`src/report_generator/columns/bu_only_builder.py`)
  - แก้ไข `build_columns()` เพื่อเพิ่ม common size columns

- **ColumnHeaderWriter** (`src/report_generator/writers/column_header_writer.py`)
  - แก้ไข Grand Total header ให้เป็น 2-level (เมื่อมี Common Size)
  - แก้ไข BU Total header ให้เป็น 2-level
  - Common Size column อยู่ row 2-4 (เป็น sub-header)
  - Row 1: "รวมทั้งสิ้น" / "รวม BU" merge ข้าม 2 columns
  - Row 2-4: "จำนวนเงิน" | "Common Size"

- **DataWriter** (`src/report_generator/writers/data_writer.py`)
  - เพิ่ม case `col_type == 'common_size'` ใน `_get_cell_value()`
  - เพิ่ม method `_calculate_common_size()` สำหรับคำนวณ Common Size
  - รองรับหลาย format ของชื่อรายได้รวม: "รายได้รวม", "1 รวมรายได้", "1.รายได้"
  - Return None สำหรับค่า 0 (จะแสดงเป็น blank)
  - แก้ไข `is_percentage` ให้รวม Common Size columns

- **CellFormatter** (`src/report_generator/formatters/cell_formatter.py`)
  - แก้ไข percentage format จาก `'0.00%'` เป็น `'0.00%;[Red](0.00%);""'`
  - ผลลัพธ์: 0 = blank, ลบ = (42.00%) สีแดง

- **generate_report.py**
  - เพิ่ม arguments `--common-size` และ `--no-common-size`
  - ส่งค่า `include_common_size` ไปยัง ReportConfig

### Fixed 🐛
- ไม่มี (feature ใหม่)

### Documentation 📚
- เพิ่ม `docs/COMMON_SIZE_FEATURE.md` - เอกสารอธิบายคุณสมบัติ Common Size
- เพิ่ม `test_common_size.py` - Script ทดสอบคุณสมบัติ Common Size
- อัพเดท `README.md` - เพิ่มส่วน Common Size และตัวอย่างการใช้งาน
- สร้าง `CHANGELOG.md` - บันทึกการเปลี่ยนแปลง

### Technical Details 🔧
- **ColumnDef Type**: เพิ่ม `'common_size'` เป็น column type ใหม่
- **Number Format**: ใช้ Excel custom format `'0.00%;[Red](0.00%);""'`
- **Calculation Logic**: 
  - ดึง "รายได้รวม" (COSTTYPE) หรือ "1 รวมรายได้" (GLGROUP)
  - คำนวณ `current_value / total_revenue`
  - ยกเว้นบรรทัดที่มีคำว่า "สัดส่วนต่อรายได้"
- **Column Position**: 
  - Grand Total → Common Size → BU1 → Common Size → BU2 → Common Size → ...

### Testing 🧪
- ทดสอบ Configuration (auto-detect, force enable/disable)
- ทดสอบ Column Building (มี/ไม่มี common size)
- ทดสอบ COSTTYPE MTH BU_ONLY
- ทดสอบ GLGROUP YTD BU_ONLY

### Breaking Changes 🚨
- ไม่มี - backward compatible 100%
- BU_ONLY จะมี Common Size โดย default แต่สามารถปิดได้ด้วย `--no-common-size`

### Migration Guide 📖
- ไม่ต้องทำอะไร - ใช้งานได้ทันทีหลัง pull code ใหม่
- ถ้าไม่ต้องการ Common Size ใน BU_ONLY ให้เพิ่ม `--no-common-size`

---

## [Previous Versions]

_ไม่มี changelog ก่อนหน้านี้_
