# Getting Started Guide

## 🚀 เริ่มต้นใช้งานระบบรายงานผลดำเนินงาน

### ขั้นตอนที่ 1: เตรียมข้อมูล

#### 1.1 สร้างไฟล์ CSV ตัวอย่าง

สร้างไฟล์ `backend/data/profit_loss.csv` (ตัวอย่าง):
```csv
YEAR,MONTH,DATE,PRODUCT_KEY,หมวดบัญชี,TYPE,NT,PRODUCT_NAME,ITEM,BUSINESS_GROUP,SUB_ITEM,SERVICE_GROUP,BUSINESS,SERVICE,PRODUCT,REPORT_CODE,GL_GROUP,CUSTOMER_GROUP_KEY,EXPENSE_VALUE,AMOUNT,REVENUE_VALUE
2025,1,2025-01-01,102010401,C01 ค่าใช้จ่ายตอบแทนแรงงาน,02 ต้นทุนบริการ,NT,บริการ NT,4,Fixed Line & Broadband,4.5,Satellite,4 Fixed Line,4.5 Satellite,102010401,C01,Labor,,1379788.05,1379788.05,0
```

สร้างไฟล์ `backend/data/other_income_expense.csv`:
```csv
YEAR,MONTH,financial_income_month,financial_income_ytd,other_income_month,other_income_ytd,other_expense_month,other_expense_ytd,financial_cost_month,financial_cost_ytd,corporate_tax_month,corporate_tax_ytd
2025,1,50000,50000,100000,100000,30000,30000,20000,20000,150000,150000
2025,2,52000,102000,105000,205000,32000,62000,21000,41000,160000,310000
```

#### 1.2 สร้างไฟล์ user whitelist

สร้างไฟล์ `backend/data/user_whitelist.json`:
```json
{
  "allowed_domains": [
    "company.com",
    "company.co.th"
  ],
  "allowed_emails": [
    "admin@example.com"
  ]
}
```

---

### ขั้นตอนที่ 2: ตั้งค่า Backend

```bash
# 1. ไปที่โฟลเดอร์ backend
cd backend

# 2. สร้าง virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. ติดตั้ง dependencies
pip install -r requirements.txt

# 5. สร้างไฟล์ .env
cp .env.example .env

# 6. แก้ไขค่าใน .env
# เปิดไฟล์ .env และแก้ไข:
# - SMTP_USERNAME, SMTP_PASSWORD (สำหรับส่ง OTP)
# - JWT_SECRET (สร้าง secret key ใหม่)
# - ALLOWED_EMAIL_DOMAINS

# 7. รัน development server
uvicorn app.main:app --reload --port 8000
```

ตรวจสอบว่า backend ทำงาน: เปิด http://localhost:8000/docs

---

### ขั้นตอนที่ 3: ตั้งค่า Frontend

เปิด terminal ใหม่:

```bash
# 1. สร้าง React project
npm create vite@latest frontend -- --template react-ts

cd frontend

# 2. ติดตั้ง dependencies
npm install

# 3. ติดตั้ง Univer packages
npm install @univerjs/core @univerjs/design @univerjs/docs @univerjs/docs-ui @univerjs/engine-formula @univerjs/engine-render @univerjs/sheets @univerjs/sheets-formula @univerjs/sheets-ui @univerjs/ui

# 4. ติดตั้ง additional packages
npm install axios antd

# 5. สร้างไฟล์ .env
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# 6. รัน development server
npm run dev
```

เปิด http://localhost:5173

---

### ขั้นตอนที่ 4: ทดสอบระบบ

#### 4.1 ทดสอบ Backend API

```bash
# ทดสอบ health check
curl http://localhost:8000/health

# ทดสอบ send OTP
curl -X POST http://localhost:8000/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@company.com"}'
```

#### 4.2 ทดสอบ Frontend

1. เปิดเบราว์เซอร์ที่ http://localhost:5173
2. กรอก email ที่อยู่ใน allowed domain
3. กด "ส่ง OTP"
4. ตรวจสอบ email และกรอก OTP
5. เลือก filter และสร้างรายงาน

---

### ขั้นตอนที่ 5: การพัฒนาต่อ

#### 5.1 เพิ่มฟีเจอร์ใหม่

1. **Backend**: เพิ่ม API endpoint ใน `backend/app/routers/`
2. **Frontend**: เพิ่ม component ใน `frontend/src/components/`
3. **Business Logic**: เพิ่ม service ใน `backend/app/services/`

#### 5.2 แก้ไขการคำนวณ

แก้ไขไฟล์ `backend/app/services/report_calculator.py`:
- เพิ่มการคำนวณใหม่ใน `calculate_profit_metrics()`
- เพิ่มหมวดบัญชีใหม่ใน `calculate_cost_by_type()`

#### 5.3 ปรับแต่งรูปแบบรายงาน

แก้ไขไฟล์ `backend/app/services/univer_converter.py`:
- เปลี่ยนสีใน `COLORS`
- เปลี่ยน number format ใน `NUMBER_FORMATS`
- เพิ่มแถวใหม่ในรายงาน

---

## 🔧 Troubleshooting

### ปัญหาที่พบบ่อย

#### 1. Backend ไม่สามารถส่ง OTP ได้

**สาเหตุ**: SMTP configuration ผิด

**แก้ไข**:
```env
# ใช้ Gmail App Password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
```

ขั้นตอนสร้าง Gmail App Password:
1. ไป Google Account Settings
2. Security > 2-Step Verification
3. App Passwords
4. Generate new app password

#### 2. Frontend ไม่สามารถเชื่อมต่อ Backend

**สาเหตุ**: CORS configuration

**แก้ไข** `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 3. Univer ไม่แสดงผล

**สาเหตุ**: Container ไม่มี height

**แก้ไข**:
```css
#univer-container {
  width: 100%;
  height: 100vh; /* ต้องกำหนด height */
}
```

#### 4. ข้อมูลในรายงานไม่ถูกต้อง

**สาเหตุ**: CSV file format ผิด

**แก้ไข**:
- ตรวจสอบว่ามี column ครบทุกตัว
- ตรวจสอบ encoding เป็น UTF-8
- ตรวจสอบ date format เป็น YYYY-MM-DD

---

## 📊 ตัวอย่างการใช้งาน

### ตัวอย่างที่ 1: ดูรายงานรายเดือน

```
Filter:
- เดือน: มกราคม
- ปี: 2025
- รูปแบบ: รายเดือน
- แสดง Common Size: เปิด

ผลลัพธ์:
| รายการ              | มกราคม    | %      |
|---------------------|-----------|--------|
| รายได้รวม            | 1,850,000 | 100.00%|
| - Fixed Line        |   500,000 |  27.03%|
| - Mobile            |   800,000 |  43.24%|
| ต้นทุนรวม            |   800,000 |  43.24%|
| กำไรขั้นต้น          | 1,050,000 |  56.76%|
```

### ตัวอย่างที่ 2: ดูรายงานสะสม (YTD)

```
Filter:
- เดือน: มกราคม, กุมภาพันธ์, มีนาคม
- ปี: 2025
- รูปแบบ: สะสม (YTD)

ผลลัพธ์:
| รายการ       | ม.ค. YTD | ก.พ. YTD | มี.ค. YTD |
|--------------|----------|----------|-----------|
| รายได้รวม     | 1,850,000| 3,700,000| 5,550,000 |
| ต้นทุนรวม     |   800,000| 1,600,000| 2,400,000 |
| กำไรขั้นต้น   | 1,050,000| 2,100,000| 3,150,000 |
```

### ตัวอย่างที่ 3: ดูรายงานแยกตามกลุ่มธุรกิจ

```
Filter:
- เดือน: มกราคม
- ปี: 2025
- กลุ่มธุรกิจ: Fixed Line & Broadband, Mobile
- รูปแบบ: ตามกลุ่มธุรกิจ

ผลลัพธ์:
| รายการ       | Fixed Line | Mobile    | รวม       |
|--------------|------------|-----------|-----------|
| รายได้        |   500,000  |   800,000 | 1,300,000 |
| ต้นทุน        |   200,000  |   350,000 |   550,000 |
| กำไรขั้นต้น   |   300,000  |   450,000 |   750,000 |
```

---

## 🎓 Next Steps

หลังจากที่ระบบทำงานได้แล้ว ควรทำต่อดังนี้:

1. **เพิ่ม Unit Tests**
   ```bash
   cd backend
   pytest tests/
   ```

2. **เพิ่ม Integration Tests**
   ```bash
   cd frontend
   npm test
   ```

3. **Setup CI/CD**
   - GitHub Actions
   - GitLab CI
   - Jenkins

4. **Deploy to Production**
   - Backend: AWS Lambda / Cloud Run / Heroku
   - Frontend: Vercel / Netlify / AWS S3 + CloudFront

5. **Monitoring & Logging**
   - Backend: Sentry, Datadog
   - Frontend: Google Analytics, LogRocket

---

## 📚 เอกสารเพิ่มเติม

- [PROJECT_PLAN.md](../PROJECT_PLAN.md) - แผนการพัฒนาโปรเจกต์
- [DATA_STRUCTURE.md](./DATA_STRUCTURE.md) - โครงสร้างข้อมูล
- [API Documentation](http://localhost:8000/docs) - FastAPI Swagger UI
- [Univer Documentation](https://univer.ai/docs) - Univer official docs

---

## 💡 Tips

1. **ใช้ Python 3.11+** สำหรับ performance ที่ดีกว่า
2. **ใช้ TypeScript** แทน JavaScript เพื่อ type safety
3. **ใช้ ESLint + Prettier** สำหรับ code formatting
4. **ใช้ Black + MyPy** สำหรับ Python code quality
5. **Commit บ่อยๆ** พร้อม meaningful commit message
6. **เขียน Test** ก่อนเขียน code (TDD)
7. **Review Code** ก่อน merge to main branch

---

## 🆘 ขอความช่วยเหลือ

หากพบปัญหา:
1. ตรวจสอบ [Known Issues](../README.md#-known-issues)
2. ดู [Troubleshooting](#-troubleshooting) ด้านบน
3. ติดต่อทีม: support@company.com
4. สร้าง GitHub Issue

Good luck! 🚀
