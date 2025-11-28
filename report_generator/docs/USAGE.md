# Univer Report Generator - Usage Guide

## 📚 ภาพรวม

ระบบสร้างรายงาน P&L Excel จากไฟล์ CSV รองรับการทำงาน 2 รูปแบบ:
- **CLI Mode**: สร้างรายงานผ่าน command line
- **Web API Mode**: สร้างรายงานผ่าน REST API

---

## 🖥️ CLI Mode

### การใช้งานพื้นฐาน

```bash
# สร้างรายงานแบบอัตโนมัติ (auto-detect report type)
python -m src.cli.cli --data-dir ../data --output-dir ./output

# ระบุวันที่
python -m src.cli.cli --data-dir ../data --output-dir ./output --date 20251031

# ระบุประเภทรายงาน
python -m src.cli.cli --data-dir ../data --output-dir ./output --type COSTTYPE
python -m src.cli.cli --data-dir ../data --output-dir ./output --type GLGROUP

# ระบุทั้งประเภทและวันที่
python -m src.cli.cli --data-dir ../data --output-dir ./output --type COSTTYPE --date 20251031
```

### Parameters

- `--data-dir`: โฟลเดอร์ที่เก็บไฟล์ CSV (required)
- `--output-dir`: โฟลเดอร์สำหรับบันทึกไฟล์ Excel (default: ./output)
- `--date`: วันที่ในรูปแบบ YYYYMMDD (optional)
- `--type`: ประเภทรายงาน COSTTYPE หรือ GLGROUP (optional)
- `--encoding`: encoding ของไฟล์ CSV (default: tis-620)
- `--verbose`: แสดงข้อมูล debug

### ไฟล์ที่รองรับ

```
TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv  # มิติประเภทต้นทุน รายเดือน
TRN_PL_COSTTYPE_NT_YTD_TABLE_20251031.csv  # มิติประเภทต้นทุน สะสม
TRN_PL_GLGROUP_NT_MTH_TABLE_20251031.csv   # มิติหมวดบัญชี รายเดือน
TRN_PL_GLGROUP_NT_YTD_TABLE_20251031.csv   # มิติหมวดบัญชี สะสม
remark_20251031.txt                         # ไฟล์หมายเหตุ (optional)
```

### ผลลัพธ์

ไฟล์ Excel จะถูกสร้างในโฟลเดอร์ output:
```
P&L_COSTTYPE_MTH_202510.xlsx
P&L_COSTTYPE_YTD_202510.xlsx
P&L_GLGROUP_MTH_202510.xlsx
P&L_GLGROUP_YTD_202510.xlsx
```

---

## 🌐 Web API Mode

### เริ่มต้น Server

```bash
cd /Users/seal/Documents/GitHub/univer/report_generator
uvicorn src.web.main:app --reload --port 8000
```

### API Endpoints

#### 1. Authentication

**Request OTP**
```bash
POST /api/auth/request-otp
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Verify OTP**
```bash
POST /api/auth/verify-otp
Content-Type: application/json

{
  "email": "user@example.com",
  "otp": "123456"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 2. Report Generation

**List Available Files**
```bash
GET /api/report/files?data_dir=../data
Authorization: Bearer <token>
```

**Generate Report**
```bash
POST /api/report/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "data_dir": "../data",
  "date_str": "20251031",
  "report_type": "COSTTYPE"
}
```

**Download Report**
```bash
GET /api/report/download/<filename>
Authorization: Bearer <token>
```

**Send Report via Email**
```bash
POST /api/report/send-email
Authorization: Bearer <token>
Content-Type: application/json

{
  "report_path": "output/P&L_COSTTYPE_MTH_202510.xlsx",
  "recipient_email": "recipient@example.com",
  "subject": "รายงาน P&L ประจำเดือน ต.ค. 2568",
  "body": "เรียน ผู้รับรายงาน..."
}
```

---

## 🔧 Configuration

### Environment Variables

สร้างไฟล์ `.env` ในโฟลเดอร์ root:

```env
# Application
APP_ENV=development  # or production

# Paths
DATA_DIR=../data
OUTPUT_DIR=./output

# CSV Encoding
CSV_ENCODING=tis-620

# Excel Settings
EXCEL_FONT_NAME=TH Sarabun New
EXCEL_FONT_SIZE=18

# Email Settings (for production)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com

# Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OTP Settings
OTP_LENGTH=6
OTP_EXPIRY_MINUTES=5
OTP_MAX_ATTEMPTS=3

# Email Whitelist
ALLOWED_EMAIL_DOMAINS=example.com,company.com
```

### Development Mode

ใน development mode:
- OTP จะแสดงใน response (ไม่ต้องส่ง email)
- SMTP settings ไม่จำเป็น

### Production Mode

ใน production mode:
- ต้องตั้งค่า SMTP
- OTP จะถูกส่งทาง email
- ต้องระบุ allowed email domains

---

## 📊 ตัวอย่างการใช้งาน

### ตัวอย่าง 1: สร้างรายงาน 1 ไฟล์

```bash
python -m src.cli.cli \
  --data-dir ../data \
  --output-dir ./output \
  --type COSTTYPE \
  --date 20251031
```

### ตัวอย่าง 2: สร้างรายงานทั้งหมด

```bash
python test_all_reports.py
```

### ตัวอย่าง 3: ทดสอบแบบง่าย

```bash
python generate_report_simple.py
```

---

## ⚠️ ข้อควรระวัง

### Thai Encoding

ไฟล์ CSV ต้องเป็น encoding TIS-620 หรือ CP874:
- ❌ **ไม่ใช่** UTF-8
- ✅ **ใช้** TIS-620, CP874

### Pre-calculated Data

โปรแกรมจะ:
- ✅ **อ่าน** ข้อมูลที่คำนวณมาแล้วจาก CSV (กำไรขั้นต้น, EBIT, EBT, กำไรสุทธิ)
- ✅ **คำนวณเฉพาะ** บรรทัดสรุป (EBITDA, รายได้รวม, ค่าใช้จ่ายรวม, สัดส่วน)
- ❌ **ไม่คำนวณซ้ำ** ข้อมูลที่มีในไฟล์แล้ว

### File Structure

โครงสร้างไฟล์ CSV ต้องมี columns:
- `TIME_KEY` - ปีเดือน (YYYYMM)
- `GROUP` - หมวดหลัก (01-14)
- `SUB_GROUP` - หมวดย่อย
- `BU` - Business Unit
- `SERVICE_GROUP` - กลุ่มบริการ
- `VALUE` - มูลค่า

---

## 🐛 Troubleshooting

### ปัญหา: UnicodeDecodeError

**สาเหตุ:** ไฟล์ CSV encoding ไม่ถูกต้อง

**แก้ไข:**
```bash
python -m src.cli.cli --encoding cp874 ...
```

### ปัญหา: ไม่พบไฟล์

**สาเหตุ:** ชื่อไฟล์หรือวันที่ไม่ตรงกัน

**แก้ไข:**
```bash
# ตรวจสอบไฟล์ในโฟลเดอร์
ls -la ../data/TRN_PL_*.csv

# ใช้ wildcard
python -m src.cli.cli --data-dir ../data
```

### ปัญหา: Font ไม่ถูกต้อง

**สาเหตุ:** ไม่มี font TH Sarabun New

**แก้ไข:** ติดตั้ง font หรือเปลี่ยนใน config/settings.py

---

## 📝 License

Copyright © 2025 Univer Report Generator
