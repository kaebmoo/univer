# Profit and Loss Report Generator

ระบบสร้างรายงาน P&L (Profit & Loss) แบบ Excel จากไฟล์ CSV โดยรองรับการทำงานทั้งแบบ Command Line และ Web Application

## คุณสมบัติ

### 📊 Core Features
- สร้างรายงาน P&L Excel ที่มีการจัดรูปแบบครบถ้วนตามข้อกำหนด
- รองรับไฟล์ CSV ที่ encode เป็น Thai (TIS-620, Windows-874)
- รองรับรายงานทั้ง 2 มิติ:
  - มิติประเภทต้นทุน (COSTTYPE)
  - มิติหมวดบัญชี (GLGROUP)
- รองรับทั้งรายงานรายเดือน (MTH) และสะสม (YTD)

### 🎨 Excel Formatting
- Font: TH Sarabun New (18pt)
- สีพื้นหลังตามกลุ่มธุรกิจ (8 กลุ่ม)
- สีสำหรับแต่ละ section
- รูปแบบตัวเลข:
  - บวก: `1,234.00`
  - ลบ: `(1,234.00)` สีแดง
  - ศูนย์: ค่าว่าง
- ตีเส้นตาราง
- Freeze panes

### 📈 Financial Calculations
- กำไรขั้นต้น (Gross Profit)
- EBITDA
- กำไรก่อนหักภาษี (EBT)
- กำไรสุทธิ (Net Profit)
- สัดส่วนต้นทุนบริการต่อรายได้
- จัดการ division by zero

### 🌐 Web Application
- Authentication ด้วย Email + OTP
- Login ได้เฉพาะ email ตาม domain ที่กำหนด
- OTP 6 หลัก (อายุ 5 นาที)
- Development mode: แสดง OTP บนหน้าจอ
- Production mode: ส่ง OTP ทาง email
- JWT token สำหรับ session management

### 📧 Email Features
- ส่งรายงานทาง email (SMTP SSL)
- ระบุผู้รับได้หลายคน
- แก้ไข subject และ body ได้
- แนบไฟล์รายงาน

### 💻 Command Line Interface
- สร้างรายงานผ่าน command line
- Auto-detect report type
- รองรับการระบุวันที่

## โครงสร้างโปรเจกต์

```
report_generator/
├── config/                 # Configuration files
│   ├── settings.py        # Settings และ configuration
│   ├── row_order.py       # COSTTYPE row structure
│   ├── row_order_glgroup.py  # GLGROUP row structure
│   ├── data_mapping.py    # COSTTYPE data mapping
│   └── data_mapping_glgroup.py  # GLGROUP data mapping
├── src/
│   ├── data_loader/       # Data loading modules
│   │   ├── csv_loader.py  # CSV file loader (Thai encoding)
│   │   ├── data_processor.py  # Data processing
│   │   └── data_aggregator.py # Data aggregation
│   ├── report_generator/  # Modular report generation (NEW!)
│   │   ├── core/          # Core components
│   │   │   ├── config.py  # Report configuration
│   │   │   └── report_builder.py  # Main orchestrator
│   │   ├── columns/       # Column builders (Strategy pattern)
│   │   │   ├── bu_only_builder.py
│   │   │   ├── bu_sg_builder.py
│   │   │   └── bu_sg_product_builder.py
│   │   ├── rows/          # Row builders
│   │   ├── writers/       # Excel writers
│   │   │   ├── header_writer.py
│   │   │   ├── column_header_writer.py
│   │   │   ├── data_writer.py
│   │   │   └── remark_writer.py
│   │   ├── formatters/    # Cell formatting
│   │   └── calculators/   # Calculations
│   ├── cli/               # Command-line interface
│   │   └── cli.py
│   └── web/               # Web application
│       ├── main.py        # FastAPI app
│       ├── routes/        # API routes
│       ├── models/        # Pydantic models
│       └── utils/         # Utilities (OTP, Email, JWT)
├── tests/                 # All test files (NEW location!)
│   ├── test_*.py          # Test suites
│   ├── check_*.py         # Data validation scripts
│   └── run_all_tests.py   # Master test runner
├── docs/                  # Documentation (NEW location!)
│   ├── USAGE.md           # Usage guide
│   ├── TESTING_GUIDE.md   # Testing procedures
│   ├── REFACTOR_PLAN.md   # Refactoring documentation
│   └── *.md               # Other documentation files
├── data/                  # Data files (CSV)
├── output/                # Generated reports
├── archive/               # Archived old implementations
├── generate_report.py     # ⭐ Simple CLI entry point (RECOMMENDED!)
├── main.py                # Main entry point (CLI or Web mode)
├── main_generator.py      # Standalone generator (legacy)
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Installation

### 1. Clone repository
```bash
cd /Users/seal/Documents/GitHub/univer/report_generator
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and configure your settings
```

## Usage

### ⭐ Simple CLI (แนะนำ - Recommended!)

โปรแกรม `generate_report.py` เป็นวิธีที่ง่ายที่สุดในการสร้างรายงาน Excel

#### Quick start (ใช้ค่า default)
```bash
python generate_report.py
```

#### ระบุประเภทรายงานและระยะเวลา
```bash
# COSTTYPE รายเดือน
python generate_report.py --report-type COSTTYPE --period MTH

# GLGROUP สะสม
python generate_report.py --report-type GLGROUP --period YTD
```

#### ระบุระดับความละเอียด
```bash
# แสดงเฉพาะ BU Total
python generate_report.py --detail-level BU_ONLY

# แสดง BU + Service Group Total
python generate_report.py --detail-level BU_SG

# แสดงครบทุกระดับ (BU + SG + Products) - ค่า default
python generate_report.py --detail-level BU_SG_PRODUCT
```

#### ระบุไฟล์ข้อมูลเอง
```bash
python generate_report.py --csv-file data/TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv
```

#### Full options
```bash
python generate_report.py \\
    --csv-file data/TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv \\
    --output output/my_report.xlsx \\
    --report-type COSTTYPE \\
    --period MTH \\
    --detail-level BU_SG_PRODUCT \\
    --verbose
```

#### ดูตัวเลือกทั้งหมด
```bash
python generate_report.py --help
```

### Advanced CLI (แบบเดิม)

#### Basic usage (auto-detect)
```bash
python -m src.cli.cli --data-dir ../data --output-dir ./output
```

#### Generate specific report type
```bash
python -m src.cli.cli --data-dir ../data --output-dir ./output --type COSTTYPE
```

#### Generate for specific date
```bash
python -m src.cli.cli --data-dir ../data --output-dir ./output --date 20251031
```

### Web Application

#### Start server
```bash
python -m src.web.main
# หรือ
uvicorn src.web.main:app --host 0.0.0.0 --port 8000 --reload
```

#### API Endpoints

**Authentication:**
- `POST /api/auth/request-otp` - Request OTP for email
- `POST /api/auth/verify-otp` - Verify OTP and get token
- `GET /api/auth/me` - Get current user info

**Report:**
- `GET /api/report/files` - List available data files
- `POST /api/report/generate` - Generate report
- `GET /api/report/download/{filename}` - Download report
- `POST /api/report/send-email` - Send report via email

**Documentation:**
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Configuration

### Email Setup (Gmail example)

1. Enable 2-factor authentication in your Google account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Add to `.env`:
```
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Allowed Email Domains

Edit `.env`:
```
ALLOWED_EMAIL_DOMAINS=company.com,company.co.th,example.com
```

## Data Files

ระบบรองรับไฟล์ CSV ดังต่อไปนี้:

- `TRN_PL_COSTTYPE_NT_MTH_TABLE_YYYYMMDD.csv` - มิติประเภทต้นทุน รายเดือน
- `TRN_PL_COSTTYPE_NT_YTD_TABLE_YYYYMMDD.csv` - มิติประเภทต้นทุน สะสม
- `TRN_PL_GLGROUP_NT_MTH_TABLE_YYYYMMDD.csv` - มิติหมวดบัญชี รายเดือน
- `TRN_PL_GLGROUP_NT_YTD_TABLE_YYYYMMDD.csv` - มิติหมวดบัญชี สะสม
- `remark_YYYYMMDD.txt` - หมายเหตุประกอบรายงาน

**Note:** ไฟล์ CSV ต้อง encode เป็น TIS-620 หรือ Windows-874

## Development

### Run tests

#### Quick test (แนะนำ)
```bash
# Run single test
cd tests
python test_1_imports.py

# Run report generation test
python test_2_generate.py

# Run all tests
python run_all_tests.py
```

#### Using pytest
```bash
pytest tests/
```

### Test files ที่สำคัญ
- `tests/test_1_imports.py` - ทดสอบการ import modules
- `tests/test_2_generate.py` - ทดสอบการสร้างรายงาน
- `tests/test_3_compare.py` - เปรียบเทียบ old vs new implementation
- `tests/test_all_reports.py` - สร้างรายงานทุกแบบ
- `tests/test_phase2c.py` - ทดสอบระดับความละเอียดต่างๆ
- `tests/test_glgroup.py` - ทดสอบรายงาน GLGROUP
- `tests/test_ytd_reports.py` - ทดสอบรายงาน YTD

### Run with auto-reload (development)
```bash
uvicorn src.web.main:app --reload
```

### Enable debug mode
Edit `.env`:
```
DEBUG=True
APP_ENV=development
```

## Documentation

เอกสารเพิ่มเติมอยู่ในโฟลเดอร์ `docs/`:

- 📖 [`docs/USAGE.md`](docs/USAGE.md) - คู่มือการใช้งานแบบละเอียด
- 🧪 [`docs/TESTING_GUIDE.md`](docs/TESTING_GUIDE.md) - คู่มือการทดสอบ
- 🏗️ [`docs/REFACTOR_PLAN.md`](docs/REFACTOR_PLAN.md) - แผน refactoring
- 📋 [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md) - สถานะการพัฒนา
- 🔄 [`docs/REPORT_GENERATOR_WORKFLOW.md`](docs/REPORT_GENERATOR_WORKFLOW.md) - Workflow การสร้างรายงาน
- ✅ [`docs/CHECKLIST.md`](docs/CHECKLIST.md) - Development checklist

### เอกสาร GLGROUP
- [`docs/GLGROUP_IMPLEMENTATION_GUIDE.md`](docs/GLGROUP_IMPLEMENTATION_GUIDE.md)
- [`docs/GLGROUP_IMPLEMENTATION_COMPLETE.md`](docs/GLGROUP_IMPLEMENTATION_COMPLETE.md)
- [`docs/GLGROUP_TODO.md`](docs/GLGROUP_TODO.md)

### เอกสาร Phase Development
- [`docs/PHASE1_PROGRESS.md`](docs/PHASE1_PROGRESS.md)
- [`docs/PHASE2A_COMPLETE.md`](docs/PHASE2A_COMPLETE.md)
- [`docs/PHASE2B_COMPLETE.md`](docs/PHASE2B_COMPLETE.md)
- [`docs/PHASE2C_TODO.md`](docs/PHASE2C_TODO.md)

## Troubleshooting

### CSV Encoding Issues
ถ้าอ่านไฟล์ CSV ไม่ได้ ให้ลองเปลี่ยน encoding:
```bash
python -m src.cli.cli --data-dir ../data --output-dir ./output --encoding windows-874
```

### Email Not Sending
1. ตรวจสอบ SMTP credentials ใน `.env`
2. ตรวจสอบว่า App Password ถูกต้อง (สำหรับ Gmail)
3. ตรวจสอบ firewall/network settings

### OTP Not Received
- Development mode: OTP จะแสดงใน API response
- Production mode: ตรวจสอบ spam folder

## License

MIT License

## Support

For issues and questions, please contact the development team.

---

**Version:** 2.0.0
**Last Updated:** 2025-11-28

## Changelog

### Version 2.0.0 (2025-11-28)
- 🗂️ Reorganized project structure
  - Moved all test files to `tests/` directory
  - Moved all documentation to `docs/` directory
- ⭐ Added `generate_report.py` - Simple CLI entry point (recommended)
- 📊 Support for 3 detail levels: BU_ONLY, BU_SG, BU_SG_PRODUCT
- 🏗️ Modular architecture with Strategy pattern
- 📖 Updated documentation structure
