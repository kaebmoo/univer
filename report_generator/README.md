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

\`\`\`
report_generator/
├── config/                 # Configuration files
│   ├── settings.py        # Settings และ configuration
│   └── row_order.py       # Row structure definition
├── src/
│   ├── data_loader/       # Data loading modules
│   │   ├── csv_loader.py  # CSV file loader (Thai encoding)
│   │   └── data_processor.py  # Data processing
│   ├── excel_generator/   # Excel generation modules
│   │   ├── excel_generator.py  # Main generator
│   │   ├── excel_formatter.py  # Formatting
│   │   └── excel_calculator.py # Calculations
│   ├── cli/               # Command-line interface
│   │   └── cli.py
│   └── web/               # Web application
│       ├── main.py        # FastAPI app
│       ├── routes/        # API routes
│       ├── models/        # Pydantic models
│       └── utils/         # Utilities (OTP, Email, JWT)
├── data/                  # Data files (CSV)
├── output/                # Generated reports
├── tests/                 # Unit tests
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── CHECKLIST.md          # Development checklist
└── README.md             # This file
\`\`\`

## Installation

### 1. Clone repository
\`\`\`bash
cd /Users/seal/Documents/GitHub/univer/report_generator
\`\`\`

### 2. Create virtual environment
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
\`\`\`

### 3. Install dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Configure environment
\`\`\`bash
cp .env.example .env
# Edit .env and configure your settings
\`\`\`

## Usage

### Command-Line Interface

#### Basic usage (auto-detect)
\`\`\`bash
python -m src.cli.cli --data-dir ../data --output-dir ./output
\`\`\`

#### Generate specific report type
\`\`\`bash
python -m src.cli.cli --data-dir ../data --output-dir ./output --type COSTTYPE
\`\`\`

#### Generate for specific date
\`\`\`bash
python -m src.cli.cli --data-dir ../data --output-dir ./output --date 20251031
\`\`\`

#### Full options
\`\`\`bash
python -m src.cli.cli \\
    --data-dir ../data \\
    --output-dir ./output \\
    --type COSTTYPE \\
    --date 20251031 \\
    --encoding tis-620 \\
    --verbose
\`\`\`

### Web Application

#### Start server
\`\`\`bash
python -m src.web.main
# หรือ
uvicorn src.web.main:app --host 0.0.0.0 --port 8000 --reload
\`\`\`

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
\`\`\`
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
\`\`\`

### Allowed Email Domains

Edit `.env`:
\`\`\`
ALLOWED_EMAIL_DOMAINS=company.com,company.co.th,example.com
\`\`\`

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
\`\`\`bash
pytest
\`\`\`

### Run with auto-reload (development)
\`\`\`bash
uvicorn src.web.main:app --reload
\`\`\`

### Enable debug mode
Edit `.env`:
\`\`\`
DEBUG=True
APP_ENV=development
\`\`\`

## Troubleshooting

### CSV Encoding Issues
ถ้าอ่านไฟล์ CSV ไม่ได้ ให้ลองเปลี่ยน encoding:
\`\`\`bash
python -m src.cli.cli --data-dir ../data --output-dir ./output --encoding windows-874
\`\`\`

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

**Version:** 1.0.0
**Last Updated:** 2025-11-25
