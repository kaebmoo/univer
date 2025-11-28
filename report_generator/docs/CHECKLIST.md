# Univer Report Generator - Development Checklist

## Project Overview
สร้างระบบสร้างรายงาน P&L แบบ Excel จากไฟล์ CSV โดยรองรับการทำงานทั้งแบบ Command Line และ Web Application

---

## ✅ Phase 1: Project Setup & Configuration (COMPLETED)

### 1.1 Project Structure
- [x] สร้างโครงสร้างโฟลเดอร์หลัก
  - [x] `/config` - ไฟล์ configuration
  - [x] `/src` - Source code หลัก
    - [x] `/data_loader` - โมดูลอ่านข้อมูล
    - [x] `/excel_generator` - โมดูลสร้าง Excel
    - [x] `/calculators` - โมดูลคำนวณ
    - [x] `/web` - Web application
    - [x] `/cli` - Command-line interface
  - [x] `/tests` - Unit tests
  - [x] `/data` - ข้อมูลตัวอย่าง
  - [x] `/output` - ไฟล์รายงานที่สร้าง

### 1.2 Configuration Files
- [x] `config/settings.py` - ตั้งค่าหลักของระบบ
  - [x] การตั้งค่า data paths และ file patterns
  - [x] การตั้งค่า encoding (TIS-620, Windows-874)
  - [x] การตั้งค่า fonts และ colors
  - [x] การตั้งค่า email/SMTP
  - [x] การตั้งค่า authentication
- [x] `config/row_order.py` - กำหนดลำดับและโครงสร้างของ rows
  - [x] ROW_ORDER configuration
  - [x] Calculation formulas
  - [x] Depreciation และ Personnel categories

---

## ✅ Phase 2: Data Loading Module (COMPLETED)

### 2.1 CSV Loader
- [x] `src/data_loader/csv_loader.py`
  - [x] รองรับ Thai encoding (TIS-620, Windows-874, CP874)
  - [x] Auto-detect encoding with fallback
  - [x] โหลดไฟล์ตาม pattern (COSTTYPE_MTH, COSTTYPE_YTD, GLGROUP_MTH, GLGROUP_YTD)
  - [x] โหลด remark file
  - [x] Extract date from filename
  - [x] Parse TIME_KEY (ปีเดือน)

### 2.2 Data Processor
- [x] `src/data_loader/data_processor.py`
  - [x] Process และ clean raw data
  - [x] Create pivot tables (BU, SERVICE_GROUP)
  - [x] Aggregate by Business Unit
  - [x] Filter by period (year, months)
  - [x] Get period description (Thai format)
  - [x] Handle YTD vs MTH reports

### 2.3 Data Aggregator
- [x] `src/data_loader/data_aggregator.py`
  - [x] Build lookup dictionary from GROUP/SUB_GROUP structure
  - [x] Read pre-calculated data directly from CSV
  - [x] Calculate only summary rows (EBITDA, totals, ratios)
  - [x] Handle depreciation and personnel categories
  - [x] Fast data access with nested dictionaries

---

## ✅ Phase 3: Excel Formatting Module (COMPLETED)

### 3.1 Excel Formatter
- [x] `src/excel_generator/excel_formatter.py`
  - [x] Font formatting (TH Sarabun New, size 18)
  - [x] Color scheme implementation
    - [x] BU colors (8 กลุ่มธุรกิจ)
    - [x] Row section colors
    - [x] Info box color
  - [x] Number formatting
    - [x] Positive: `1,234.00`
    - [x] Negative: `(1,234.00)` in red
    - [x] Zero: empty cell
  - [x] Border formatting
  - [x] Cell alignment
  - [x] Header styles
  - [x] Info box formatting
  - [x] Remark section formatting
  - [x] Column width และ row height
  - [x] Freeze panes

---

## ✅ Phase 4: Excel Generator Core (COMPLETED)

### 4.1 Excel Calculator
- [x] `src/excel_generator/excel_calculator.py`
  - [x] คำนวณกำไรขั้นต้น (Gross Profit)
  - [x] คำนวณ EBITDA
  - [x] คำนวณ EBT
  - [x] คำนวณกำไรสุทธิ (Net Profit)
  - [x] คำนวณรายได้รวม
  - [x] คำนวณค่าใช้จ่ายรวม (ไม่รวม/รวมต้นทุนทางการเงิน)
  - [x] คำนวณสัดส่วนต้นทุนบริการต่อรายได้
    - [x] ต้นทุนบริการรวม
    - [x] ต้นทุนบริการ - ค่าเสื่อมราคาฯ
    - [x] ต้นทุนบริการ - ไม่รวมบุคลากรและค่าเสื่อมราคาฯ
  - [x] Handle division by zero (#DIV/0!)

### 4.2 Excel Generator Main
- [x] `src/excel_generator/excel_generator.py`
  - [x] สร้าง workbook และ worksheet
  - [x] เขียน header (3 บรรทัด)
    - [x] บรรทัด 1: ชื่อบริษัท
    - [x] บรรทัด 2: ชื่อรายงาน (มิติประเภทต้นทุน/มิติหมวดบัญชี)
    - [x] บรรทัด 3: งวดเวลา (YTD/MTH)
  - [x] สร้าง column structure
    - [x] Column "รายละเอียด" (Column B)
    - [x] กลุ่มธุรกิจ (BU) columns
    - [x] กลุ่มบริการ (SERVICE_GROUP) columns
    - [x] PRODUCT_KEY และ PRODUCT_NAME columns (ถ้ามี)
    - [x] Total columns (รวม BU, รวม SERVICE_GROUP, รวมทั้งสิ้น)
  - [x] สร้าง row structure ตาม row_order.py
    - [x] Section headers
    - [x] Detail rows
    - [x] Calculated rows
    - [x] Summary rows
  - [x] Apply formatting
    - [x] Colors (BU, sections, rows)
    - [x] Fonts และ borders
    - [x] Number formats
  - [x] เขียนข้อมูล framework
    - [x] ข้อมูลจาก CSV
    - [x] ค่าที่คำนวณ
    - [x] Totals และ subtotals
  - [x] เพิ่ม Info Box (ด้านบนขวา)
    - [x] วัตถุประสงค์ของรายงาน
    - [x] คำอธิบายการใช้งาน
  - [x] เพิ่ม Remarks (ด้านล่างสุด)
    - [x] อ่านจาก remark file
    - [x] Format ตามข้อกำหนด
  - [x] Set freeze panes
  - [x] บันทึกไฟล์

---

## ✅ Phase 5: Command-Line Interface (COMPLETED)

### 5.1 CLI Main
- [x] `src/cli/cli.py`
  - [x] รับ arguments (data path, output path, report type)
  - [x] เรียก data loader
  - [x] เรียก excel generator
  - [x] แสดงผลความคืบหน้า
  - [x] Error handling

### 5.2 CLI Entry Point
- [x] สร้าง `main.py` หรือ `generate_report.py`
- [x] รองรับ command-line arguments
- [x] Documentation และ help message

---

## ✅ Phase 6: Web Application (COMPLETED)

### 6.1 FastAPI Backend
- [x] `src/web/main.py` - FastAPI application
- [x] `src/web/routes/` - API endpoints
  - [x] `/auth` - Authentication endpoints
  - [x] `/report` - Report generation endpoints
  - [x] `/download` - File download endpoints
- [x] `src/web/models/` - Pydantic models
- [x] `src/web/services/` - Business logic

### 6.2 Authentication System
- [x] Email validation (domain whitelist)
- [x] OTP generation และส่งทาง email
  - [x] Development mode: แสดง OTP บนหน้าจอ
  - [x] Production mode: ส่งทาง email
- [x] JWT token management
- [x] Session management

### 6.3 Report Generation API
- [x] List available data files
- [x] Select report parameters
  - [x] File selection
  - [x] Report type (COSTTYPE/GLGROUP, MTH/YTD)
- [x] Generate report
- [x] Download report

### 6.4 Email Functionality
- [x] SMTP SSL configuration
- [x] Email template
  - [x] Subject (ตามเดือน/งวด)
  - [x] Body message (แก้ไขได้)
- [x] Send report via email
  - [x] ระบุ email ผู้รับเอง
  - [x] เลือกจาก list (via API)

---

## 🎨 Phase 7: Frontend (PENDING)

### 7.1 Web UI
- [ ] Framework: Tailwind CSS หรือ Semantic UI
- [ ] Login page
  - [ ] Email input
  - [ ] OTP verification
- [ ] Dashboard/Main page
  - [ ] แสดง available reports
  - [ ] Report selection
  - [ ] Parameter configuration
- [ ] Report generation page
  - [ ] Progress indicator
  - [ ] Download button
  - [ ] Email sending form
- [ ] Settings page
  - [ ] Email recipients management
  - [ ] Email template editing

---

## 🧪 Phase 8: Testing & Quality Assurance (PENDING)

### 8.1 Unit Tests
- [ ] Test data loader
  - [ ] Encoding detection
  - [ ] File parsing
  - [ ] Data processing
- [ ] Test excel generator
  - [ ] Formatting
  - [ ] Calculations
  - [ ] File creation
- [ ] Test calculators
  - [ ] Financial calculations
  - [ ] Division by zero handling

### 8.2 Integration Tests
- [ ] End-to-end report generation
- [ ] Web API endpoints
- [ ] Authentication flow
- [ ] Email sending

### 8.3 Test with Actual Data
- [x] Test with provided CSV files
  - [x] TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv ✓ (26KB)
  - [x] TRN_PL_COSTTYPE_NT_YTD_TABLE_20251031.csv ✓ (28KB)
  - [x] TRN_PL_GLGROUP_NT_MTH_TABLE_20251031.csv ✓ (18KB)
  - [x] TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv ✓ (18KB)
- [x] Verify calculations (using pre-calculated data from CSV)
- [x] Verify formatting (Thai fonts, number formats, colors)
- [x] DataAggregator implementation (reads pre-calculated values directly)

---

## 📦 Phase 9: Deployment & Documentation (PENDING)

### 9.1 Dependencies
- [ ] `requirements.txt`
  - [ ] pandas
  - [ ] openpyxl
  - [ ] fastapi
  - [ ] uvicorn
  - [ ] pydantic-settings
  - [ ] python-multipart
  - [ ] python-jose[cryptography]
  - [ ] passlib
  - [ ] python-dotenv
  - [ ] aiosmtplib (for async email)

### 9.2 Configuration Files
- [ ] `.env.example`
- [ ] `README.md`
  - [ ] Project description
  - [ ] Installation instructions
  - [ ] Usage guide (CLI + Web)
  - [ ] Configuration guide
- [ ] `DEPLOYMENT.md` (deployment guide)

### 9.3 Docker Support (Optional)
- [ ] Dockerfile
- [ ] docker-compose.yml
- [ ] .dockerignore

---

## 📊 Current Progress Summary

- ✅ **Completed:** 7 phases
  - Phase 1: Project Setup & Configuration
  - Phase 2: Data Loading Module (with DataAggregator)
  - Phase 3: Excel Formatting Module
  - Phase 4: Excel Generator Core (updated with DataAggregator)
  - Phase 5: Command-Line Interface
  - Phase 6: Web Application
  - Phase 8.3: Testing with Actual Data (all 4 report types verified)
- 📋 **Pending:** 2 phases (Frontend UI, Full Testing Suite)

**Overall Progress:** ~85% Complete

**Backend Complete:** CLI และ Web API พร้อมใช้งานเต็มรูปแบบ
- ✅ ทดสอบกับข้อมูลจริง 4 ไฟล์แล้ว
- ✅ ใช้ข้อมูลที่คำนวณมาแล้วจาก CSV
- ✅ คำนวณเฉพาะบรรทัดสรุป (EBITDA, totals, ratios)
**Remaining:** Frontend UI และ Full Integration Testing

---

## 🎯 Next Steps

1. ✅ Complete Excel Calculator module
2. ✅ Complete Excel Generator main module
3. ✅ Create CLI interface
4. ✅ Build Web application
5. ✅ Implement authentication
6. ✅ Add email functionality
7. ✅ Test with actual data files (all 4 types)
8. ✅ Implement DataAggregator for pre-calculated data
9. ⬜ Create frontend UI (HTML/Tailwind CSS)
10. ⬜ Full integration testing
11. ⬜ Deployment documentation

---

## 📝 Notes

- ไฟล์ข้อมูล encode เป็น Thai (TIS-620/CP874) ไม่ใช่ UTF-8
- TIME_KEY คือ column ปีเดือน (format: YYYYMM เช่น 202510)
- รายงานต้องรองรับทั้ง MTH (รายเดือน) และ YTD (สะสม)
- รายงานมี 2 มิติ: มิติประเภทต้นทุน (COSTTYPE) และ มิติหมวดบัญชี (GLGROUP)

### ⚠️ สำคัญมาก: การคำนวณข้อมูล

**ข้อมูลที่มีในไฟล์ CSV แล้ว (ไม่ต้องคำนวณ):**
- กำไรขั้นต้น (GROUP 03)
- กำไรหลังหักค่าใช้จ่ายขาย (GROUP 05)
- EBIT (GROUP 08)
- EBT (GROUP 12)
- กำไรสุทธิ (GROUP 14)

**ข้อมูลที่ต้องคำนวณเอง:**
- รายได้รวม (sum ของ GROUP 01)
- ค่าใช้จ่ายรวม (sum ของ GROUP 02, 04, 06, 07, 11)
- EBITDA (EBIT + ค่าเสื่อมราคา + ค่าตัดจำหน่าย)
- ต้นทุนบริการรวม และสัดส่วน
- ต้นทุนบริการ - ค่าเสื่อมราคาฯ และสัดส่วน
- ต้นทุนบริการ - ไม่รวมบุคลากรและค่าเสื่อมราคาฯ และสัดส่วน

**DataAggregator:**
- ใช้ `config/data_mapping.py` เพื่อ map row labels ไปยัง GROUP/SUB_GROUP
- อ่านข้อมูลที่คำนวณมาแล้วจากไฟล์ CSV โดยตรง
- คำนวณเฉพาะบรรทัดสรุปที่ไม่มีในไฟล์

---

**Last Updated:** 2025-11-25
**Version:** 1.0.0 (Backend Complete + Data Testing Complete)
