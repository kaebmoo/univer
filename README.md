# 📊 ระบบรายงานผลดำเนินงานด้วย Univer

ระบบรายงานผลดำเนินงาน (P&L Report) แบบ Interactive บนเว็บที่ให้ความรู้สึกเหมือนใช้ Excel

## ✨ Features

- 📈 แสดงรายงานผลดำเนินงานแบบ Excel-like บนเว็บ
- 🔍 Filter ข้อมูลแบบยืดหยุ่น (เดือน, ไตรมาส, กลุ่มธุรกิจ)
- 📊 คำนวณอัตราส่วนทางการเงิน (EBIT, EBITDA, Common Size)
- 💾 Export เป็นไฟล์ Excel
- 🔐 Authentication ด้วย Email + OTP
- 🔄 รองรับ MCP Server
- 📱 Responsive Design

## 🚀 Quick Start

### Prerequisites

- Node.js >= 18
- Python >= 3.11
- npm หรือ yarn

### Backend Setup

```bash
# ไปที่โฟลเดอร์ backend
cd backend

# สร้าง virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt

# สร้างไฟล์ .env
cp .env.example .env
# แก้ไขค่า config ใน .env

# รัน development server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
# ไปที่โฟลเดอร์ frontend
cd frontend

# ติดตั้ง dependencies
npm install

# สร้างไฟล์ .env
cp .env.example .env
# แก้ไขค่า config ใน .env

# รัน development server
npm run dev
```

เปิดเบราว์เซอร์ที่ http://localhost:5173

## 📁 โครงสร้างโปรเจกต์

```
univer/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # FastAPI application
│   │   ├── routers/     # API routes
│   │   ├── services/    # Business logic
│   │   └── models/      # Pydantic models
│   ├── data/            # CSV data files
│   └── tests/           # Backend tests
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API services
│   │   └── types/       # TypeScript types
│   └── public/
├── docs/                # Documentation
└── README.md
```

## 🎯 การใช้งาน

### 1. Login
- กรอก email ที่อยู่ใน domain ที่อนุญาต
- กด "ส่ง OTP"
- กรอก OTP ที่ได้รับทาง email (valid 5 นาที)

### 2. เลือก Filter
- **เดือน**: เลือกเดือนที่ต้องการดู (สามารถเลือกหลายเดือน)
- **ไตรมาส**: เลือก Q1, Q2, Q3, Q4
- **ปี**: เลือกปีที่ต้องการ
- **กลุ่มธุรกิจ**: เลือกกลุ่มธุรกิจที่ต้องการดู
- **รูปแบบการแสดงผล**:
  - รายเดือน (Monthly)
  - สะสม (YTD)
  - ทั้งสองแบบ (Both)
- **แสดง Common Size**: เปิด/ปิดการแสดงเปอร์เซ็นต์

### 3. สร้างรายงาน
- กดปุ่ม "สร้างรายงาน"
- รอระบบประมวลผล (2-3 วินาที)
- รายงานจะแสดงในรูปแบบ Excel-like

### 4. ใช้งานรายงาน
- **ดูข้อมูล**: เลื่อนดูข้อมูลในตาราง
- **หุบ/ขยายรายการ**: คลิกที่ไอคอน +/- เพื่อหุบหรือขยายรายการ
- **แก้ไขข้อมูล**: สามารถแก้ไขและคำนวณบน browser ได้ (ไม่ส่งกลับ server)
- **Export**: กดปุ่ม "Export to Excel" เพื่อดาวน์โหลดไฟล์

## 📊 รายงานที่แสดง

### โครงสร้างรายงาน P&L
1. **รายได้** (7 กลุ่มธุรกิจ)
2. **ต้นทุนบริการและต้นทุนขาย** (14 รายการ)
3. **กำไรขั้นต้น**
4. **ค่าใช้จ่ายขายและการตลาด** (10 รายการ)
5. **กำไรหลังหักค่าใช้จ่ายขาย**
6. **ค่าใช้จ่ายบริหารและสนับสนุน** (11 รายการ)
7. **EBIT**
8. **รายได้อื่นและค่าใช้จ่ายอื่น**
9. **EBT**
10. **ภาษีและกำไรสุทธิ**
11. **EBITDA**
12. **อัตราส่วนต้นทุนบริการต่อรายได้**

### อัตราส่วนที่คำนวณ
- **Common Size**: % เทียบกับรายได้
- **EBIT**: Earnings Before Interest and Tax
- **EBITDA**: Earnings Before Interest, Tax, Depreciation and Amortization
- **Gross Profit Margin**: อัตรากำไรขั้นต้น
- **Cost to Revenue Ratio**: อัตราส่วนต้นทุนต่อรายได้

## 🔐 Authentication

ระบบใช้ Email + OTP authentication:

1. ผู้ใช้กรอก email
2. ระบบตรวจสอบว่า email อยู่ใน allowed domain หรือไม่
3. ส่ง OTP 6 หลักไปยัง email (valid 5 นาที)
4. ผู้ใช้กรอก OTP
5. ระบบออก JWT token (valid 24 ชั่วโมง)

### กำหนด Allowed Email Domains

แก้ไขไฟล์ `backend/.env`:
```env
ALLOWED_EMAIL_DOMAINS=company.com,company.co.th,example.com
```

## 🔄 MCP Server Integration

ระบบรองรับ Model Context Protocol (MCP) สำหรับการเชื่อมต่อกับ AI Agents

### เริ่มใช้งาน MCP Server

```bash
cd backend
python -m app.mcp_server.server
```

### MCP Tools Available

1. **get_report_data**: ดึงข้อมูลรายงานตาม filter
2. **get_filter_options**: ดึงตัวเลือกสำหรับ filter
3. **calculate_metrics**: คำนวณอัตราส่วนทางการเงิน

### ตัวอย่างการใช้งานผ่าน Claude Desktop

```
User: "ช่วยดึงรายงานผลดำเนินงานเดือนมกราคม 2025 ของกลุ่มธุรกิจ Fixed Line"

Claude: [เรียก MCP tool get_report_data]
{
  "months": [1],
  "year": 2025,
  "business_groups": ["Fixed Line & Broadband"]
}

[ได้ผลลัพธ์กลับมา]
```

## 📝 API Documentation

เมื่อรัน backend แล้ว สามารถดู API documentation ได้ที่:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### สำคัญ API Endpoints

#### Authentication
```
POST /auth/send-otp
POST /auth/verify-otp
POST /auth/logout
```

#### Report
```
POST /api/report/generate
GET /api/filters/options
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# รัน backend และ frontend ก่อน
npm run test:e2e
```

## 📦 Deployment

### Docker Deployment

```bash
# Build images
docker-compose build

# Run containers
docker-compose up -d
```

### Manual Deployment

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm run build
# Deploy dist/ folder to CDN/web server
```

## 🔧 Configuration

### Backend (.env)
```env
# Database
DATABASE_URL=sqlite:///./data/app.db

# Email (for OTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# JWT
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION=1440  # minutes (24 hours)

# OTP
OTP_LENGTH=6
OTP_EXPIRATION=300  # seconds (5 minutes)

# Allowed Email Domains
ALLOWED_EMAIL_DOMAINS=company.com,company.co.th

# CORS
CORS_ORIGINS=http://localhost:5173,https://your-domain.com
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=ระบบรายงานผลดำเนินงาน
```

## 📚 Documentation

- [Project Plan](./PROJECT_PLAN.md) - แผนการพัฒนาโปรเจกต์
- [Data Structure](./docs/DATA_STRUCTURE.md) - โครงสร้างข้อมูลและการคำนวณ
- [API Documentation](http://localhost:8000/docs) - API reference
- [Univer Docs](https://univer.ai/docs) - Univer documentation

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Team

- **Project Owner**: [Your Name]
- **Backend Developer**: [Name]
- **Frontend Developer**: [Name]
- **Data Analyst**: [Name]

## 🐛 Known Issues

- [ ] การแสดงผล Common Size บนมือถืออาจจะเล็กเกินไป
- [ ] Export ขนาดใหญ่ (>100MB) อาจจะช้า

## 🚧 Roadmap

- [ ] เพิ่มการแสดงผลแบบกราฟ (Charts)
- [ ] เพิ่มการเปรียบเทียบระหว่างปี (Year-over-Year)
- [ ] เพิ่มการแสดง Variance Analysis
- [ ] เพิ่มการ Drill-down เข้าไปดูรายละเอียด
- [ ] เพิ่ม Dashboard สำหรับผู้บริหาร

## 📞 Support

หากพบปัญหาหรือมีคำถาม:
- 📧 Email: support@company.com
- 💬 Teams/Slack: #univer-support
- 📝 Create an issue: [GitHub Issues](https://github.com/your-repo/issues)

---

Made with ❤️ by [Your Company]
