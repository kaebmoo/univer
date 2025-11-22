# 📋 Development Checklist - Univer Report System

> **สถานะโครงการ**: 🚀 เริ่มพัฒนา
> **วันที่เริ่ม**: 2025-01-22
> **เป้าหมาย**: สร้างระบบรายงานผลดำเนินงานแบบ Excel-like บนเว็บ

---

## 📊 ความคืบหน้ารวม

- [ ] Phase 1: Project Setup (0/8)
- [ ] Phase 2: Backend Development (0/12)
- [ ] Phase 3: Frontend Development (0/10)
- [ ] Phase 4: Advanced Features (0/6)
- [ ] Phase 5: Testing & Optimization (0/8)
- [ ] Phase 6: Deployment (0/4)

**Progress**: 0/48 tasks (0%)

---

## 🎯 Phase 1: Project Setup (Day 1-2)

### 1.1 Environment Setup
- [ ] ติดตั้ง Python 3.11+
- [ ] ติดตั้ง Node.js 18+
- [ ] ติดตั้ง Git
- [ ] เตรียม IDE (VS Code / PyCharm)

### 1.2 Backend Setup
- [ ] สร้าง virtual environment
  ```bash
  cd backend
  python -m venv venv
  source venv/bin/activate  # macOS/Linux
  ```
- [ ] ติดตั้ง dependencies
  ```bash
  pip install -r requirements.txt
  ```
- [ ] สร้างไฟล์ `.env` จาก `.env.example`
- [ ] ทดสอบรัน FastAPI
  ```bash
  uvicorn app.main:app --reload
  ```
- [ ] ตรวจสอบ http://localhost:8000/docs

### 1.3 Frontend Setup
- [ ] สร้าง React project ด้วย Vite
  ```bash
  npm create vite@latest frontend -- --template react-ts
  ```
- [ ] ติดตั้ง Univer packages
  ```bash
  npm install @univerjs/core @univerjs/sheets @univerjs/sheets-ui
  ```
- [ ] ติดตั้ง additional packages
  ```bash
  npm install axios antd
  ```
- [ ] สร้างไฟล์ `.env` และตั้งค่า `VITE_API_BASE_URL`
- [ ] ทดสอบรัน dev server
  ```bash
  npm run dev
  ```
- [ ] ตรวจสอบ http://localhost:5173

### 1.4 Data Preparation
- [ ] เตรียมไฟล์ `backend/data/profit_loss.csv`
- [ ] เตรียมไฟล์ `backend/data/other_income_expense.csv`
- [ ] ตรวจสอบ CSV format และ encoding (UTF-8)
- [ ] สร้าง sample data สำหรับทดสอบ

---

## 🎯 Phase 2: Backend Development (Day 3-7)

### 2.1 Configuration & Models (Day 3)
- [ ] สร้าง `app/config.py` - การตั้งค่าจาก environment
- [ ] สร้าง `app/models/auth.py` - Pydantic models สำหรับ auth
  - [ ] EmailRequest model
  - [ ] OTPVerifyRequest model
  - [ ] TokenResponse model
- [ ] สร้าง `app/models/report.py` - Pydantic models สำหรับ report
  - [ ] ReportFilters model
  - [ ] ReportResponse model
- [ ] สร้าง `app/models/filters.py` - Pydantic models สำหรับ filter options

### 2.2 Authentication System (Day 3)
- [ ] สร้าง `app/utils/otp_generator.py`
  - [ ] ฟังก์ชันสร้าง OTP 6 หลัก
  - [ ] ฟังก์ชันตรวจสอบ OTP expiration
- [ ] สร้าง `app/utils/email_sender.py`
  - [ ] ตั้งค่า SMTP connection
  - [ ] Template สำหรับส่ง OTP
  - [ ] ฟังก์ชันส่ง email
- [ ] สร้าง `app/services/auth_service.py`
  - [ ] validate email domain
  - [ ] generate และ store OTP (in-memory หรือ Redis)
  - [ ] verify OTP
  - [ ] generate JWT token
- [ ] สร้าง `app/routers/auth.py`
  - [ ] POST `/auth/send-otp`
  - [ ] POST `/auth/verify-otp`
  - [ ] POST `/auth/logout`
- [ ] ทดสอบ auth flow ด้วย Postman/curl

### 2.3 Data Loading Service (Day 4)
- [ ] สร้าง `app/services/data_loader.py`
  - [ ] ฟังก์ชัน load CSV files
  - [ ] Data validation (columns, types, ranges)
  - [ ] Data cleaning (handle NaN, duplicates)
  - [ ] Cache mechanism (optional)
- [ ] ทดสอบการโหลดข้อมูล
- [ ] จัดการ error cases (file not found, invalid format)

### 2.4 Report Calculator Service (Day 5-6)
- [ ] ปรับปรุง `app/services/report_calculator.py`
  - [ ] เพิ่ม method `calculate_revenue_by_group()`
  - [ ] เพิ่ม method `calculate_cost_of_service_detail()`
  - [ ] เพิ่ม method `calculate_selling_expense_detail()`
  - [ ] เพิ่ม method `calculate_admin_expense_detail()`
  - [ ] เพิ่ม method `get_other_income_expense()` (จาก CSV อื่น)
  - [ ] เพิ่ม method `calculate_full_pl_statement()`
- [ ] เพิ่ม support สำหรับ view types
  - [ ] Monthly view
  - [ ] Quarterly view
  - [ ] Yearly view
  - [ ] YTD (Year-to-Date)
- [ ] เพิ่ม support สำหรับ business group filtering
- [ ] ทดสอบการคำนวณด้วย pytest

### 2.5 Univer Converter Service (Day 6-7)
- [ ] ปรับปรุง `app/services/univer_converter.py`
  - [ ] สร้าง row structure สำหรับ P&L ครบ 67 แถว
  - [ ] เพิ่มการ format ตัวเลข (currency, percentage)
  - [ ] เพิ่มการกำหนดสี ตัวหนา ตามแต่ละส่วน
  - [ ] เพิ่ม column headers (dynamic ตาม filter)
  - [ ] เพิ่ม row grouping metadata
- [ ] สร้าง method สำหรับ Common Size columns
- [ ] ทดสอบ snapshot output

### 2.6 Report API (Day 7)
- [ ] สร้าง `app/routers/report.py`
  - [ ] POST `/api/report/generate`
  - [ ] GET `/api/filters/options`
- [ ] เชื่อม services ทั้งหมดเข้าด้วยกัน
- [ ] เพิ่ม authentication middleware
- [ ] ทดสอบ API ด้วย real data
- [ ] จัดการ error handling

### 2.7 Testing & Documentation
- [ ] เขียน unit tests สำหรับ `report_calculator.py`
- [ ] เขียน unit tests สำหรับ `auth_service.py`
- [ ] อัพเดท API documentation (FastAPI auto-docs)

---

## 🎯 Phase 3: Frontend Development (Day 8-12)

### 3.1 Project Structure (Day 8)
- [ ] สร้างโครงสร้างโฟลเดอร์
  ```
  src/
  ├── components/
  │   ├── Auth/
  │   ├── Filters/
  │   ├── Report/
  │   └── Layout/
  ├── services/
  ├── types/
  ├── hooks/
  └── utils/
  ```
- [ ] ติดตั้ง และตั้งค่า React Router
- [ ] ติดตั้ง และตั้งค่า Ant Design
- [ ] สร้าง global styles

### 3.2 Authentication UI (Day 8)
- [ ] สร้าง `components/Auth/LoginForm.tsx`
  - [ ] Input สำหรับ email
  - [ ] Validation email format
  - [ ] Validation email domain
  - [ ] ปุ่ม "ส่ง OTP"
- [ ] สร้าง `components/Auth/OTPVerification.tsx`
  - [ ] Input OTP (6 digits)
  - [ ] Countdown timer (5 minutes)
  - [ ] ปุ่ม "ยืนยัน OTP"
  - [ ] ปุ่ม "ส่ง OTP อีกครั้ง"
- [ ] สร้าง `services/authService.ts`
  - [ ] sendOTP()
  - [ ] verifyOTP()
  - [ ] logout()
- [ ] สร้าง `hooks/useAuth.ts`
  - [ ] Store JWT token in localStorage
  - [ ] Check authentication status
- [ ] สร้าง Protected Route wrapper

### 3.3 Layout Components (Day 9)
- [ ] สร้าง `components/Layout/Header.tsx`
  - [ ] Logo
  - [ ] User info
  - [ ] Logout button
- [ ] สร้าง `components/Layout/Sidebar.tsx`
  - [ ] Filter panel (collapsible)
- [ ] สร้าง `components/Layout/MainLayout.tsx`
  - [ ] Header + Sidebar + Content area

### 3.4 Filter Components (Day 9)
- [ ] สร้าง `components/Filters/MonthSelector.tsx`
  - [ ] Multi-select checkboxes (Jan - Dec)
- [ ] สร้าง `components/Filters/QuarterSelector.tsx`
  - [ ] Buttons Q1, Q2, Q3, Q4
- [ ] สร้าง `components/Filters/YearSelector.tsx`
  - [ ] Dropdown select
- [ ] สร้าง `components/Filters/ViewTypeSelector.tsx`
  - [ ] Radio: รายเดือน / รายไตรมาส / รายปี
- [ ] สร้าง `components/Filters/DisplayTypeSelector.tsx`
  - [ ] Radio: เดือน / สะสม (YTD) / ทั้งคู่
- [ ] สร้าง `components/Filters/BusinessGroupSelector.tsx`
  - [ ] Tree select (hierarchical)
- [ ] สร้าง `components/Filters/FilterPanel.tsx`
  - [ ] รวม filters ทั้งหมด
  - [ ] ปุ่ม "สร้างรายงาน"
  - [ ] Switch "แสดง Common Size"

### 3.5 Univer Integration (Day 10-11)
- [ ] สร้าง `components/Report/UniverReport.tsx`
  - [ ] Initialize Univer instance
  - [ ] Load snapshot from API
  - [ ] Handle resize
  - [ ] Cleanup on unmount
- [ ] สร้าง `services/reportService.ts`
  - [ ] generateReport()
  - [ ] getFilterOptions()
- [ ] สร้าง `hooks/useReport.ts`
  - [ ] Manage report state
  - [ ] Handle loading state
  - [ ] Handle error state
- [ ] เชื่อมต่อ filters กับ Univer report
- [ ] ทดสอบการแสดงผลรายงาน

### 3.6 Export Feature (Day 11)
- [ ] สร้าง `components/Report/ExportButton.tsx`
- [ ] Implement export to Excel functionality
  - [ ] ใช้ Univer API export
  - [ ] Generate filename with timestamp
  - [ ] Trigger browser download
- [ ] ทดสอบ export ด้วยข้อมูลจริง

### 3.7 UI Polish & Error Handling (Day 12)
- [ ] เพิ่ม loading spinners
- [ ] เพิ่ม error messages (Toast notifications)
- [ ] เพิ่ม empty states
- [ ] ปรับปรุง responsive design
- [ ] ทดสอบ UX flow ทั้งหมด

---

## 🎯 Phase 4: Advanced Features (Day 13-15)

### 4.1 Row/Column Grouping (Day 13)
- [ ] Research Univer grouping API
- [ ] Implement row grouping สำหรับ:
  - [ ] กลุ่มรายได้ (rows 2-9)
  - [ ] กลุ่มต้นทุนบริการ (rows 11-24)
  - [ ] กลุ่มค่าใช้จ่ายขาย (rows 27-36)
  - [ ] กลุ่มค่าใช้จ่ายบริหาร (rows 39-49)
- [ ] เพิ่ม expand/collapse icons
- [ ] ทดสอบการหุบ/ขยายรายการ

### 4.2 Conditional Formatting (Day 13)
- [ ] กำหนดสีแถวหัวข้อหลัก
- [ ] กำหนดสีแถวผลรวม
- [ ] กำหนดสีสำหรับค่าติดลบ (แสดงสีแดง)
- [ ] กำหนดสีสำหรับ Common Size columns

### 4.3 Number Formatting (Day 14)
- [ ] ตรวจสอบ number format ในทุก cell
- [ ] Format currency (#,##0.00)
- [ ] Format percentage (0.00%)
- [ ] Handle negative numbers display

### 4.4 MCP Server Integration (Day 14-15)
- [ ] ติดตั้ง MCP SDK
  ```bash
  pip install mcp
  ```
- [ ] สร้าง `backend/mcp_server/server.py`
- [ ] สร้าง MCP Tools:
  - [ ] `get_report_data` tool
  - [ ] `get_filter_options` tool
  - [ ] `calculate_metrics` tool
- [ ] เขียน MCP server startup script
- [ ] ทดสอบกับ Claude Desktop
- [ ] เขียนเอกสารการใช้งาน MCP

---

## 🎯 Phase 5: Testing & Optimization (Day 16-18)

### 5.1 Backend Testing (Day 16)
- [ ] เขียน pytest สำหรับ auth service
- [ ] เขียน pytest สำหรับ data loader
- [ ] เขียน pytest สำหรับ report calculator
- [ ] เขียน pytest สำหรับ univer converter
- [ ] รัน tests และแก้ไข bugs
- [ ] ตรวจสอบ test coverage (ควร > 80%)

### 5.2 Frontend Testing (Day 16)
- [ ] ติดตั้ง Vitest
- [ ] เขียน tests สำหรับ auth components
- [ ] เขียน tests สำหรับ filter components
- [ ] เขียน tests สำหรับ report service
- [ ] รัน tests และแก้ไข bugs

### 5.3 Integration Testing (Day 17)
- [ ] ทดสอบ auth flow แบบ end-to-end
- [ ] ทดสอบ report generation flow
- [ ] ทดสอบ export functionality
- [ ] ทดสอบ error scenarios
- [ ] ทดสอบ edge cases

### 5.4 Performance Optimization (Day 17-18)
- [ ] เพิ่ม caching สำหรับ CSV data
- [ ] เพิ่ม caching สำหรับ report ที่สร้างแล้ว (Redis)
- [ ] Optimize pandas operations
- [ ] Optimize Univer rendering
- [ ] ทดสอบ performance กับข้อมูลขนาดใหญ่
- [ ] ตรวจสอบ memory leaks

### 5.5 User Acceptance Testing (Day 18)
- [ ] เตรียม test scenarios
- [ ] ทดสอบกับ real users (2-3 คน)
- [ ] รวบรวม feedback
- [ ] แก้ไขตาม feedback ที่สำคัญ

---

## 🎯 Phase 6: Deployment (Day 19-20)

### 6.1 Docker Setup (Day 19)
- [ ] สร้าง `Dockerfile` สำหรับ backend
- [ ] สร้าง `Dockerfile` สำหรับ frontend
- [ ] สร้าง `docker-compose.yml`
- [ ] ทดสอบ build images
- [ ] ทดสอบรัน containers locally

### 6.2 Production Configuration (Day 19)
- [ ] สร้าง `.env.production`
- [ ] ตั้งค่า production database (ถ้ามี)
- [ ] ตั้งค่า production email server
- [ ] ตั้งค่า CORS สำหรับ production domain
- [ ] ตั้งค่า JWT secret ใหม่

### 6.3 Deployment (Day 20)
- [ ] เลือก platform (AWS / GCP / Azure / Heroku)
- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] ตั้งค่า environment variables
- [ ] ทดสอบ production deployment
- [ ] ตั้งค่า custom domain (ถ้ามี)
- [ ] ตั้งค่า SSL certificate

### 6.4 Monitoring & Documentation (Day 20)
- [ ] ตั้งค่า logging
- [ ] ตั้งค่า monitoring (Sentry / Datadog)
- [ ] สร้าง deployment documentation
- [ ] สร้าง user manual
- [ ] Handover to team

---

## 📝 Notes & Issues

### ปัญหาที่พบระหว่างการพัฒนา
```
วันที่     | ปัญหา                          | แก้ไขอย่างไร
-----------|--------------------------------|------------------
           |                                |
           |                                |
```

### Technical Decisions
```
Decision                    | Reason                    | Date
----------------------------|---------------------------|----------
ใช้ React แทน Vue          | Ecosystem ใหญ่กว่า         | 2025-01-22
ใช้ FastAPI แทน Flask      | Performance ดีกว่า         | 2025-01-22
```

### การเปลี่ยนแปลง Scope
```
Change                              | Impact        | Approved By
------------------------------------|---------------|-------------
                                    |               |
```

---

## 🎉 Completion Criteria

### Definition of Done
- [ ] ทุก features ตาม requirements ทำงานได้
- [ ] Unit tests pass ทั้งหมด (coverage > 80%)
- [ ] Integration tests pass ทั้งหมด
- [ ] User acceptance testing สำเร็จ
- [ ] Performance ตาม requirement (< 3 วินาที)
- [ ] Security audit pass
- [ ] Documentation ครบถ้วน
- [ ] Deployment to production สำเร็จ
- [ ] Handover to team เสร็จสิ้น

### Next Steps After Launch
- [ ] Monitor production errors
- [ ] Gather user feedback
- [ ] Plan for Phase 2 features
- [ ] Schedule maintenance windows

---

**Last Updated**: 2025-01-22
**Updated By**: Claude (AI Assistant)
