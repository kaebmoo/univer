# Report Generator Execution Flow

เอกสารนี้อธิบายการทำงานของโปรแกรม `report_generator` ตั้งแต่เริ่มต้นจนได้ไฟล์ Excel โดยละเอียด

## ภาพรวมการทำงาน (High-Level Overview)

1.  **Initialization**: รับค่าจาก Command Line Arguments และตั้งค่า Logging
2.  **Data Loading**: ค้นหาและอ่านไฟล์ CSV (จัดการ Encoding ภาษาไทยอัตโนมัติ)
3.  **Data Processing**: ทำความสะอาดข้อมูลและแปลงโครงสร้าง (เช่น การแยกกลุ่มบริการ Satellite)
4.  **Configuration**: กำหนดค่ารายงาน (Report Config) ตามที่ผู้ใช้ระบุ
5.  **Report Building**: สร้างโครงสร้าง Report (Columns/Rows) และเขียนลงไฟล์ Excel
6.  **Finalization**: บันทึกไฟล์และแสดงผลลัพธ์

## ลำดับการทำงานโดยละเอียด (Detailed Execution Flow)

### 1. Entry Point (`generate_report.py`)

โปรแกรมเริ่มต้นทำงานที่ฟังก์ชัน `main()` ใน `generate_report.py`:

1.  **Parse Arguments**: ใช้ `argparse` เพื่อรับค่าต่าง ๆ เช่น `--report-type`, `--period`, `--detail-level`
2.  **Find CSV File**:
    *   ตรวจสอบว่ามีการระบุ `--csv-file` หรือไม่
    *   ถ้าไม่มี จะใช้ฟังก์ชัน `find_csv_file()` เพื่อค้นหาไฟล์ล่าสุดใน `data/` โดยดูจาก Report Type, Period Type และ Month
3.  **Load CSV**:
    *   สร้าง instance ของ `src.data_loader.CSVLoader`
    *   เรียก `loader.load_csv()` ซึ่งจะพยายามอ่านไฟล์ด้วย Encoding ต่าง ๆ (`tis-620`, `cp874`, `utf-8`) เพื่อป้องกันปัญหาภาษาต่างด้าว
4.  **Process Data**:
    *   สร้าง instance ของ `src.data_loader.DataProcessor`
    *   เรียก `processor.process_data(df)`:
        *   แปลง Column `GROUP`, `SUB_GROUP`, `BU` ฯลฯ เป็น String
        *   แยกข้อมูล Satellite Service Group (ถ้าเปิดใช้งาน) ผ่าน `_split_satellite_service_group()`
5.  **Setup Configuration**:
    *   สร้าง `src.report_generator.core.config.ReportConfig`
    *   กำหนดค่า Detail Level (`BU_ONLY`, `BU_SG`, หรือ `BU_SG_PRODUCT`)
    *   กำหนดค่า Common Size (วิเคราะห์แนวดิ่ง)
6.  **Load Remarks**:
    *   เรียก `load_remark_file()` เพื่อหาไฟล์ text หมายเหตุที่คู่กับไฟล์ข้อมูล (เช่น `remark_20251031.txt`)
7.  **Generate Report**:
    *   สร้าง instance ของ `src.report_generator.core.report_builder.ReportBuilder`
    *   เรียก `builder.generate_report(...)` เพื่อเริ่มกระบวนการสร้าง Excel

### 2. Report Generation Logic (`src/report_generator/`)

กระบวนการสร้าง Excel เกิดขึ้นใน `ReportBuilder.generate_report()`:

#### 2.1 Initialization (`__init__`)
*   **Formatter**: สร้าง `CellFormatter` สำหรับจัดการ Font, Border, Number Format
*   **Column Builder**: เลือก Builder ตาม Detail Level:
    *   `BUOnlyBuilder`
    *   `BUSGBuilder`
    *   `BUSGProductBuilder`
*   **Writers**: เตรียม Writer สำหรับส่วนต่าง ๆ (`HeaderWriter`, `DataWriter` etc.)

#### 2.2 Execution (`generate_report`)
1.  **Build Components**:
    *   `column_builder.build_columns(data)`: วิเคราะห์ข้อมูลเพื่อสร้างโครงสร้างคอลัมน์ (เช่น มี BU อะไรบ้าง, มี Service Group อะไรบ้าง)
    *   `row_builder.build_rows()`: สร้างโครงสร้างแถว (รายได้, ต้นทุน, กำไร ฯลฯ)
2.  **Prepare Excel**: สร้าง Workbook และ Worksheet ใหม่
3.  **Prepare Aggregator**: สร้าง `DataAggregator` เพื่อเตรียมคำนวณตัวเลข
4.  **Write Content**:
    *   `HeaderWriter`: เขียนหัวรายงาน (ชื่อบริษัท, ชื่อรายงาน, งวดเวลา)
    *   `ColumnHeaderWriter`: เขียนหัวตาราง (BU headers, Service Group headers)
    *   `DataWriter`: วนลูปตามโครงสร้าง Rows เพื่อเขียนข้อมูลและสูตร Excel
    *   `RemarkWriter`: เขียนหมายเหตุต่อท้ายตาราง
5.  **Finalize**:
    *   `_apply_final_formatting()`: จัดระเบียบหน้า, Freeze Panes

### 3. Data Processing Details (`src/data_loader/`)

#### DataProcessor
*   **Satellite Split**: โปรแกรมมีความสามารถพิเศษในการแยกกลุ่มบริการ "SATELLITE" ออกเป็นย่อย ๆ ตาม `PRODUCT_KEY` โดยอ่านค่าจาก `config/satellite_config.py`

#### CSVLoader
*   **Encoding Fallback**: มีกลไกอัจฉริยะในการลองอ่านไฟล์ด้วย Encoding ภาษาไทยหลายแบบ หากอ่านด้วย `tis-620` ไม่ได้ จะลอง `cp874` และ `utf-8` ตามลำดับ

## โครงสร้างไฟล์ (File Structure Reference)

*   `generate_report.py`: Main script
*   `src/data_loader/`: Module สำหรับจัดการข้อมูล
    *   `csv_loader.py`: อ่านไฟล์
    *   `data_processor.py`: ปรับปรุงข้อมูล แปลงข้อมูล
*   `src/report_generator/`: Module สำหรับสร้างรายงาน
    *   `core/`: Core logic (`ReportBuilder`, `ReportConfig`)
    *   `columns/`: Logic การสร้างคอลัมน์ตาม Detail Level
    *   `rows/`: Logic การสร้างแถว P&L
    *   `writers/`: Logic การเขียนลง Excel แยกตามส่วน (Header, Data, Remark)
    *   `formatters/`: Logic การจัดรูปแบบ Cell
