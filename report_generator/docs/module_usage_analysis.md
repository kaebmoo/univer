# การวิเคราะห์การใช้งานโมดูล

เอกสารนี้สรุปผลการวิเคราะห์การเชื่อมโยงของโมดูลต่างๆ ในโปรเจกต์ `report_generator` โดยมีจุดเริ่มต้นที่ `generate_report.py`

## ภาพรวม

สคริปต์หลัก `generate_report.py` เป็นจุดเริ่มต้น (Entry Point) ของโปรแกรม และได้มีการเรียกใช้งานโมดูลต่างๆ ที่อยู่ใน `src` และ `config` เพื่อสร้างรายงาน Excel

จากการตรวจสอบพบว่า `generate_report.py` เป็นเวอร์ชันใหม่ที่ใช้สถาปัตยกรรมแบบใหม่ที่อยู่ใน `src` เป็นหลัก แต่ยังคงมีการเรียกใช้ไฟล์คอนฟิกจากโฟลเดอร์ `config` อยู่หลายส่วน

---

## การใช้งานไฟล์ในโฟลเดอร์ `config`

ไฟล์คอนฟิกใน `/config` ถูกเรียกใช้โดย `generate_report.py` และโมดูลต่างๆ ใน `src` ดังนี้

### ไฟล์ที่ถูกใช้งาน:

| ไฟล์ | ถูกเรียกใช้ใน | วัตถุประสงค์ |
| :--- | :--- | :--- |
| `settings.py` | `generate_report.py` | เก็บการตั้งค่าหลักของโปรแกรม |
| `data_mapping.py` | `src/data_loader/data_aggregator.py` | กำหนดการจับคู่ระหว่างแถวในรายงานกับ Group/Sub-group ในข้อมูลดิบ (สำหรับ COSTTYPE) |
| | `src/report_generator/writers/data_writer.py` | |
| `data_mapping_glgroup.py`| `src/data_loader/data_aggregator.py` | กำหนดการจับคู่ระหว่างแถวในรายงานกับ Group/Sub-group ในข้อมูลดิบ (สำหรับ GLGROUP) |
| | `src/report_generator/writers/data_writer.py` | |
| `row_order.py` | `src/report_generator/rows/row_builder.py` | กำหนดลำดับแถว, สูตรคำนวณ, และการจัดรูปแบบของรายงานแบบ COSTTYPE |
| `row_order_glgroup.py`| `src/data_loader/data_aggregator.py` | กำหนดลำดับแถวและสูตรคำนวณของรายงานแบบ GLGROUP |
| | `src/report_generator/rows/row_builder.py` | |
| `common_size_rows.py` | `src/report_generator/writers/data_writer.py`| กำหนดแถวที่ต้องมีการคำนวณ Common Size |

### ไฟล์ที่ **ไม่ได้** ถูกใช้งาน:

| ไฟล์ | เหตุผล |
| :--- | :--- |
| `report_config.py` | ถูกแทนที่ด้วยคลาส `ReportConfig` ที่อยู่ใน `src/report_generator/core/config.py` ซึ่งมีการกำหนดค่าต่างๆ ไว้แบบ Hardcoded |
| `types.py` | ถูกแทนที่ด้วย Enum (ReportType, PeriodType, DetailLevel) ที่ถูกนิยามใหม่ใน `src/report_generator/core/config.py` |

---

## สรุปการเชื่อมโยงของ `generate_report.py`

`generate_report.py` เป็นสคริปต์ที่ทำหน้าที่เป็นส่วนติดต่อกับผู้ใช้ (CLI) และเรียกใช้โมดูลหลักๆ ดังนี้:

1.  **`config.settings`**: โหลดการตั้งค่าพื้นฐาน
2.  **`src.data_loader`**:
    *   `CSVLoader`: สำหรับโหลดไฟล์ CSV
    *   `DataProcessor`: สำหรับการประมวลผลข้อมูลเบื้องต้น
3.  **`src.report_generator`**:
    *   `ReportConfig` (จาก `src/report_generator/core/config.py`): สร้างอ็อบเจกต์ที่เก็บการตั้งค่าของรายงาน เช่น ประเภท, ช่วงเวลา, ระดับรายละเอียด ซึ่งเป็นคลาสที่มาแทนที่ `config/report_config.py` และ `config/types.py`
    *   `ReportBuilder` (จาก `src/report_generator/core/report_builder.py`): เป็นตัวหลักในการสร้างรายงาน ซึ่งจะเรียกใช้โมดูลย่อยๆ ต่อไปนี้:
        *   **Column Builders** (`src/report_generator/columns/`): สร้างโครงสร้างคอลัมน์ตาม `DetailLevel`
        *   **Row Builder** (`src/report_generator/rows/row_builder.py`): สร้างโครงสร้างแถว โดยดึงข้อมูลจาก `config/row_order.py` และ `config/row_order_glgroup.py`
        *   **Data Aggregator** (`src/data_loader/data_aggregator.py`): ทำหน้าที่รวม (Aggregate) และคำนวณข้อมูลจาก DataFrame ตามการจับคู่ใน `config/data_mapping.py` และ `config/data_mapping_glgroup.py`
        *   **Writers** (`src/report_generator/writers/`): ทำหน้าที่เขียนข้อมูลลงไฟล์ Excel ซึ่ง `DataWriter` เป็นส่วนที่ซับซ้อนที่สุด โดยมีการเรียกใช้ `config/common_size_rows.py` และ `config/data_mapping.py` เพื่อประกอบการเขียนข้อมูล

## สรุป
โมดูลใน `config` ส่วนใหญ่ยังคงมีความสำคัญและถูกใช้งานในสถาปัตยกรรมใหม่ ยกเว้น `report_config.py` และ `types.py` ที่ถูกแทนที่ด้วยโมดูลใหม่ใน `src` เรียบร้อยแล้ว

---

## การเปรียบเทียบ `core/config.py` และ `config/settings.py`

ไฟล์ทั้งสองทำหน้าที่จัดการการตั้งค่า (Configuration) แต่มีวัตถุประสงค์และขอบเขตต่างกันอย่างชัดเจน

### `src/report_generator/core/config.py`

ไฟล์นี้เปรียบเสมือน **"พิมพ์เขียว" หรือ "แม่แบบ" สำหรับการสร้างรายงาน Excel หนึ่งฉบับ**

*   **หน้าที่หลัก**: กำหนด **โครงสร้าง, เนื้อหา, และหน้าตา** ของรายงานที่จะสร้างขึ้นมาแต่ละครั้ง
*   **ลักษณะข้อมูล**:
    *   เป็นคลาส `ReportConfig` ที่รับค่าตอนสร้างอ็อบเจกต์ เพื่อกำหนดคุณสมบัติของรายงานนั้นๆ
    *   เก็บการตั้งค่าที่เปลี่ยนแปลงได้ตามการเรียกใช้งาน เช่น ประเภทรายงาน (`report_type`), ช่วงเวลา (`period_type`), ระดับความละเอียด (`detail_level`)
    *   เก็บการตั้งค่าด้านการจัดรูปแบบ เช่น สี, ฟอนต์, ขนาดตัวอักษร, การวางตำแหน่งแถวและคอลัมน์
*   **การใช้งาน**:
    *   `generate_report.py` สร้างอ็อบเจกต์ `ReportConfig` ขึ้นมาตามพารามิเตอร์ที่ผู้ใช้ป้อนเข้ามา
    *   อ็อบเจกต์นี้จะถูกส่งต่อไปยังโมดูลต่างๆ ใน `src/report_generator/` (เช่น `ReportBuilder`, `DataWriter`, `CellFormatter`) เพื่อให้โมดูลเหล่านั้นรู้ว่าจะต้องสร้างและจัดรูปแบบรายงานอย่างไร

### `config/settings.py`

ไฟล์นี้เปรียบเสมือน **"แผงควบคุมหลัก" ของทั้งแอปพลิเคชัน**

*   **หน้าที่หลัก**: กำหนดการตั้งค่า **ระดับแอปพลิเคชันและสภาพแวดล้อม (Environment)** โดยรวม ซึ่งเป็นการตั้งค่าที่มักจะคงที่ ไม่ได้เปลี่ยนไปทุกครั้งที่สร้างรายงาน
*   **ลักษณะข้อมูล**:
    *   ใช้ Pydantic `BaseSettings` เพื่อโหลดค่ามาจากไฟล์ `.env` ได้
    *   เก็บการตั้งค่าของโปรแกรมโดยรวม เช่น ชื่อแอป (`app_name`), โหมดดีบัก (`debug`)
    *   เก็บตำแหน่งไฟล์และโฟลเดอร์ (Path) เช่น `data_dir`, `output_dir`
    *   เก็บการตั้งค่าที่เกี่ยวกับระบบอื่นๆ ที่อาจมีในโปรเจกต์ เช่น Web server, JWT, การส่งอีเมล
*   **การใช้งาน**:
    *   ถูก import และใช้งานใน `generate_report.py` เพื่อรับค่าตั้งต้นบางอย่าง เช่น ตำแหน่งของโฟลเดอร์
    *   ถูกใช้งานในส่วนอื่นๆ ของโปรเจกต์ที่ต้องการเข้าถึงการตั้งค่ากลางของแอปพลิเคชัน เช่น ส่วนเว็บ API (`src/web/`)

### สรุปตารางเปรียบเทียบ

| คุณสมบัติ | `src/report_generator/core/config.py` | `config/settings.py` |
| :--- | :--- | :--- |
| **ขอบเขต** | **สำหรับรายงาน 1 ฉบับ** (Report-specific) | **สำหรับทั้งแอปพลิเคชัน** (Application-wide) |
| **หน้าที่** | กำหนดโครงสร้างและหน้าตาของ Excel | กำหนดสภาพแวดล้อมและที่อยู่ไฟล์ |
| **การเปลี่ยนแปลง** | เปลี่ยนแปลงค่าได้ทุกครั้งที่รันโปรแกรม | ค่าค่อนข้างคงที่, เปลี่ยนเมื่อแก้ไข `.env` |
| **ตัวอย่าง** | `detail_level`, `bu_colors`, `font_size` | `data_dir`, `output_dir`, `csv_encoding` |
| **ถูกใช้ที่ไหน** | `generate_report.py`, `src/report_generator/*` | `generate_report.py`, `src/web/*` |

---

## การใช้งานค่าต่าง ๆ ใน `config/settings.py`

จากการตรวจสอบ พบว่าค่าหลายอย่างในไฟล์ `settings.py` ไม่ได้ถูกใช้งานโดยสคริปต์ `generate_report.py` โดยตรง เนื่องจากสคริปต์เวอร์ชันใหม่นี้รับค่าผ่าน Command-line arguments หรือใช้ค่าที่กำหนดไว้ใน `src/report_generator/core/config.py` เป็นหลัก

### ค่าที่ไม่ได้ถูกใช้งานโดย `generate_report.py`

1.  **กลุ่ม Web/Email/API (`smtp_*`, `otp_*`, `jwt_*`, `web_*`, `allowed_email_domains`)**
    *   **เหตุผล**: ค่าเหล่านี้ถูกออกแบบมาเพื่อใช้กับส่วนที่เป็น Web Application (ในโฟลเดอร์ `src/web/`) ไม่ได้เกี่ยวข้องกับสคริปต์สร้างรีพอร์ตแบบ CLI

2.  **กลุ่มการจัดรูปแบบ Excel (`excel_*`, `report_*`, `bu_colors`, `row_colors`, `info_box_color`)**
    *   **เหตุผล**: `generate_report.py` ใช้ค่าที่กำหนดไว้ตายตัว (hardcoded) ในคลาส `ReportConfig` (`src/report_generator/core/config.py`) แทนที่ค่าเหล่านี้ทั้งหมด ค่าใน `settings.py` จึงถูกใช้โดยโค้ดเก่าในโฟลเดอร์ `archive/` เท่านั้น

3.  **กลุ่มตำแหน่งและชื่อไฟล์ (`data_dir`, `output_dir`, `..._pattern`, `remark_file`)**
    *   **เหตุผล**: สคริปต์ `generate_report.py` รับค่า Path เหล่านี้จาก Command-line arguments (`--data-dir`, `--output-dir`) ซึ่งมีค่าปริยาย (default) เป็น `data/` และ `output/` ส่วนการค้นหาไฟล์ก็สร้าง pattern ขึ้นมาเอง ไม่ได้ใช้ค่าจาก `settings.py` (อย่างไรก็ตาม `data_dir` และ `output_dir` ยังถูกใช้ในส่วนของ `src/web/`)

4.  **ค่าอื่น ๆ (`app_name`, `app_env`, `debug`, `csv_encoding`)**
    *   **เหตุผล**: ค่าเหล่านี้ไม่ได้ถูกเรียกใช้ใน `generate_report.py` โดยตรง โดย `csv_encoding` จะถูกรับค่าจาก Argument `--encoding` ซึ่งมีค่าปริยายเป็น `tis-620`

### สรุป

สำหรับสคริปต์ **`generate_report.py`** โดยเฉพาะ **แทบจะไม่มีการใช้ค่าจาก `settings.py` เลย** ถึงแม้จะมีการ `import` เข้ามาก็ตาม ค่าส่วนใหญ่ที่จำเป็นจะถูกกำหนดผ่าน Command-line arguments หรือถูกกำหนดไว้ใน `ReportConfig` ที่ทันสมัยกว่า ค่าใน `settings.py` จึงมีความสำคัญสำหรับส่วน Web Application และเป็นส่วนหนึ่งของโค้ดที่เคยใช้ในอดีตมากกว่า
