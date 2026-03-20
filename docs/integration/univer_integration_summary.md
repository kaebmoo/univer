# สรุปการทำงาน: การนำไฟล์ Excel ขึ้นแสดงผลบนเว็บด้วย Univer

เอกสารนี้สรุปขั้นตอนและรายละเอียดการปรับปรุงระบบ Backend และ Frontend ของโปรเจกต์ Univer เพื่อให้สามารถนำไฟล์ Excel (.xlsx) ที่สร้างโดย `report_generator` มาแสดงผลผ่าน Web Interface ด้วยไลบรารี Univer ได้อย่างถูกต้องและคงรูปแบบต้นฉบับไว้

---

## วัตถุประสงค์

*   แสดงผลไฟล์ Excel (.xlsx) ที่อยู่ใน `/Users/seal/Documents/GitHub/univer/report_generator/output` ผ่าน Web Application
*   คงรูปแบบและการจัดวางของไฟล์ Excel ต้นฉบับไว้ทุกประการ (เช่น สไตล์เซลล์, การรวมเซลล์, ความกว้างคอลัมน์, ความสูงแถว)
*   ใช้ไลบรารี Univer ในการแสดงผลบน Frontend
*   Backend ต้องรองรับการดึงและแปลงไฟล์ Excel
*   Frontend ต้องรองรับการแสดงผลรายการไฟล์และเรียกดูไฟล์
*   ระบบ Authentication ด้วย OTP ต้องยังคงทำงานได้ตามเดิม
*   คำนึงถึงประสิทธิภาพในการเรียกดูข้อมูล
*   **ห้ามแก้ไขโปรเจกต์ `/Users/seal/Documents/GitHub/univer/report_generator` โดยเด็ดขาด**

---

## ส่วนที่ 1: การปรับปรุง Backend (`/Users/seal/Documents/GitHub/univer/backend`)

**เป้าหมาย:** สร้าง API สำหรับดึงรายชื่อไฟล์ Excel และ API สำหรับแปลงไฟล์ Excel เป็นโครงสร้าง JSON ที่ Univer เข้าใจ

### ไฟล์ที่ถูกแก้ไข/สร้าง:

1.  **`app/services/excel_to_univer.py` (ไฟล์ใหม่):**
    *   **วัตถุประสงค์:** ทำหน้าที่หลักในการแปลงไฟล์ `.xlsx` (ที่อ่านด้วย `openpyxl`) ให้เป็นโครงสร้าง JSON แบบ Univer Snapshot
    *   **รายละเอียด:**
        *   คลาส `ExcelToUniverConverter` มีเมธอด `convert_file_to_snapshot` ซึ่งจะโหลดไฟล์ Excel ทั้ง Workbook
        *   วนลูปผ่านทุกชีตใน Workbook เพื่อดึงข้อมูล:
            *   ค่าและประเภทของเซลล์
            *   การจัดรูปแบบเซลล์ (Font, Fill, Alignment, Number Format) และแปลงเป็น Univer Style Object
            *   การรวมเซลล์ (Merged Cells)
            *   ความสูงของแถวและความกว้างของคอลัมน์
        *   ใช้ `styles_registry` เพื่อจัดการสไตล์ไม่ให้ซ้ำซ้อน ลดขนาด JSON payload
        *   ประกอบข้อมูลทั้งหมดเป็น Univer Snapshot JSON ที่สมบูรณ์

2.  **`app/routers/report.py` (ไฟล์ที่ถูกแก้ไข):**
    *   **วัตถุประสงค์:** เพิ่ม API endpoint ใหม่ 2 ตัว และเชื่อมต่อกับ `excel_to_univer.py`
    *   **รายละเอียด:**
        *   เพิ่ม `REPORTS_DIR` เพื่อชี้ไปยังโฟลเดอร์ `/Users/seal/Documents/GitHub/univer/report_generator/output`
        *   เพิ่ม `workbook_cache` (in-memory dictionary) เพื่อเก็บผลการแปลงไฟล์ Excel เป็น JSON ชั่วคราว เพิ่มประสิทธิภาพ
        *   **`GET /report/reports/list`**:
            *   อ่านไฟล์ทั้งหมดใน `REPORTS_DIR`
            *   กรองเฉพาะไฟล์ `.xlsx`
            *   ส่งคืนรายชื่อไฟล์ Excel เป็น List of strings
            *   มีการป้องกันด้วย `Depends(get_current_user)`
        *   **`GET /report/reports/view/{filename}`**:
            *   รับชื่อไฟล์ Excel ที่ต้องการ
            *   ตรวจสอบ `workbook_cache` ก่อน หากมีใน Cache จะส่งคืนทันที
            *   หากไม่มีใน Cache จะเรียก `excel_to_univer_converter.convert_file_to_snapshot(file_path)` เพื่อแปลงไฟล์
            *   เก็บผลลัพธ์ใน `workbook_cache`
            *   ส่งคืน Univer Snapshot JSON
            *   มีการป้องกันด้วย `Depends(get_current_user)`

---

## ส่วนที่ 2: การปรับปรุง Frontend (`/Users/seal/Documents/GitHub/univer/frontend`)

**เป้าหมาย:** สร้าง UI สำหรับแสดงรายการไฟล์ Excel และแสดงผลไฟล์ที่เลือกด้วย Univer Library

### ไฟล์ที่ถูกแก้ไข/สร้าง:

1.  **`src/services/api.ts` (ไฟล์ที่ถูกแก้ไข):**
    *   **วัตถุประสงค์:** เพิ่มเมธอดสำหรับเรียกใช้ API endpoint ใหม่ของ Backend
    *   **รายละเอียด:**
        *   เพิ่มเมธอด `getReportList(): Promise<string[]>` สำหรับเรียก `GET /report/reports/list`
        *   เพิ่มเมธอด `getReportSnapshot(filename: string): Promise<UniverSnapshot>` สำหรับเรียก `GET /report/reports/view/{filename}`
    *   `apiClient` ที่มีอยู่เดิมถูกนำมาใช้ต่อ โดยยังคงความสามารถในการจัดการ Token และ Authorization Header โดยอัตโนมัติ

2.  **`src/components/ReportListViewer.tsx` (ไฟล์ใหม่):**
    *   **วัตถุประสงค์:** Component หลักที่แสดงผลรายการรายงานและเป็น Viewer สำหรับไฟล์ Excel
    *   **รายละเอียด:**
        *   จัดการสถานะ `view` ('list' หรือ 'viewer') และ `selectedFile` เพื่อสลับการแสดงผล
        *   **ในโหมด 'list':**
            *   เรียก `apiClient.getReportList()` เพื่อดึงรายการไฟล์ Excel
            *   แสดงผลด้วย `antd.List` โดยแต่ละรายการเป็นปุ่มให้คลิกเพื่อ "View"
            *   แสดงสถานะ Loading (`Spin`) และ Error (`Alert`)
        *   **ในโหมด 'viewer':**
            *   แสดง Component ย่อย `UniverSheetViewer` พร้อมส่งชื่อไฟล์ที่เลือกไป
            *   มีปุ่ม "Back to List" เพื่อกลับไปยังหน้ารายการ
        *   `UniverSheetViewer` (ส่วนหนึ่งของไฟล์นี้):
            *   รับ `filename` เป็น prop
            *   เรียก `apiClient.getReportSnapshot(filename)` เพื่อดึง Univer Snapshot JSON
            *   ใช้ `useRef` เพื่ออ้างอิง `div` ที่จะ render Univer
            *   ใช้ `useEffect` เพื่อ khởi tạo Univer instance (`new Univer(...)`) และลงทะเบียน Plugin ที่จำเป็น (`UniverRenderEnginePlugin`, `UniverFormulaEnginePlugin`, `UniverUIPlugin`, `UniverSheetsPlugin` ฯลฯ)
            *   เรียก `univer.createUnit(UniverInstanceType.UNIVER_SHEET, snapshot)` เพื่อ render ตาราง Excel ด้วยข้อมูล JSON ที่ได้มา
            *   มี cleanup function เพื่อ `univer.dispose()` เมื่อ Component unmount เพื่อป้องกัน Memory Leak
            *   แสดงสถานะ Loading (`Spin`) และ Error (`Result`)

3.  **`src/App.tsx` (ไฟล์ที่ถูกแก้ไข):**
    *   **วัตถุประสงค์:** เปลี่ยนหน้าหลักของแอปพลิเคชันให้แสดงผลฟังก์ชันใหม่
    *   **รายละเอียด:**
        *   ลบ `FilterPanel` และ `ReportViewer` เดิมออก
        *   นำ `ReportListViewer` เข้ามาแสดงผลแทนที่
        *   ลบ `ReportProvider` ที่ไม่เกี่ยวข้องออก

---

## ผลลัพธ์ที่ได้

*   เมื่อผู้ใช้เข้าสู่ระบบ (ผ่าน OTP Authentication เดิม) จะเห็นหน้าจอที่แสดงรายการไฟล์ Excel (.xlsx) ทั้งหมดที่อยู่ในโฟลเดอร์ `report_generator/output`
*   ผู้ใช้สามารถคลิกปุ่ม "View" เพื่อเปิดดูไฟล์ Excel ที่เลือก
*   ไฟล์ Excel จะถูกแสดงผลในรูปแบบตาราง Spreadsheet ที่สามารถโต้ตอบได้ โดยยังคงสไตล์, การจัดรูปแบบ, การรวมเซลล์, ความกว้างคอลัมน์ และความสูงแถว ตามต้นฉบับอย่างสมบูรณ์
*   Backend มีระบบ Cache ช่วยเพิ่มความเร็วในการโหลดไฟล์ที่เคยเปิดดูไปแล้ว
*   การทำงานทั้งหมดนี้เป็นไปตามข้อจำกัดที่ว่า **ห้ามแก้ไขโปรเจกต์ `report_generator`**

---
