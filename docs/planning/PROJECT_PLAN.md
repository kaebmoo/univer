# แผนการจัดทำระบบรายงานผลดำเนินงานด้วย Univer

## 📋 สรุปความต้องการ

### เป้าหมาย
สร้างระบบรายงานผลดำเนินงานบนเว็บที่ให้ความรู้สึกเหมือนใช้ Excel โดยผู้ใช้สามารถ:
- ดูรายงานที่มีรูปแบบสวยงามเหมือน Excel
- เลือกดูข้อมูลตามเงื่อนไข (เดือน, ไตรมาส, กลุ่มธุรกิจ, etc.)
- Export ไฟล์ออกไปใช้งานต่อ
- คำนวณข้อมูลเบื้องต้นบน browser (แต่ไม่ save กลับ database)

### Technology Stack
- **Frontend**: React + TypeScript + Vite + Univer
- **Backend**: Python + FastAPI + Pandas
- **Authentication**: Email Domain + OTP
- **MCP Server**: สำหรับการเชื่อมต่อข้อมูล
- **Data Source**: CSV files

---

## 🏗️ สถาปัตยกรรมระบบ

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  React App (Frontend)                                │  │
│  │  - Authentication UI (Email + OTP)                   │  │
│  │  - Filter Controls (Month, Quarter, Business Group)  │  │
│  │  - Univer Spreadsheet Display                        │  │
│  │  - Export to Excel                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↕ HTTP/JSON
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Backend (Python)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Endpoints:                                      │  │
│  │  - POST /auth/send-otp                              │  │
│  │  - POST /auth/verify-otp                            │  │
│  │  - POST /api/report/generate                        │  │
│  │  - GET /api/filters/options                         │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Data Processing (Pandas):                          │  │
│  │  - Load CSV files                                   │  │
│  │  - Filter data by criteria                          │  │
│  │  - Calculate EBIT, EBITDA, Common Size              │  │
│  │  - Create crosstab structure                        │  │
│  │  - Convert to Univer snapshot format                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────────┐
│                     Data Storage                             │
│  - profit_loss.csv (main data)                              │
│  - other_income_expense.csv (month, ytd)                    │
│  - user_whitelist.json (allowed email domains)              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 โครงสร้างข้อมูล

### 1. ไฟล์ CSV หลัก (profit_loss.csv)
```
Columns:
- YEAR, MONTH, DATE
- PRODUCT_KEY, PRODUCT_NAME
- BUSINESS_GROUP, SERVICE_GROUP, BUSINESS, SERVICE, PRODUCT
- หมวดบัญชี (Account Category)
- TYPE (02 ต้นทุนบริการ, 03 ค่าใช้จ่ายขายฯ, 04 ค่าใช้จ่ายสนับสนุน)
- EXPENSE_VALUE, AMOUNT, REVENUE_VALUE
```

### 2. ไฟล์รายได้/ค่าใช้จ่ายอื่น (other_income_expense.csv)
```
Columns:
- YEAR, MONTH
- other_income_month, other_income_ytd
- other_expense_month, other_expense_ytd
- financial_cost_month, financial_cost_ytd
```

### 3. โครงสร้างรายงาน (Crosstab)
**Rows** (ประมาณ 50+ แถว):
1. รายได้ (แยกตามกลุ่มธุรกิจ 7 กลุ่ม)
2. ต้นทุนบริการและต้นทุนขาย (14 รายการ)
3. กำไรขั้นต้น
4. ค่าใช้จ่ายขายและการตลาด (10 รายการ)
5. กำไรหลังหักค่าใช้จ่ายขาย
6. ค่าใช้จ่ายบริหาร (11 รายการ)
7. EBIT, EBITDA
8. รายได้อื่น, ค่าใช้จ่ายอื่น
9. EBT, ภาษี, กำไรสุทธิ
10. อัตราส่วนต่างๆ (Common Size)

**Columns** (แบบ Dynamic):
- แสดงตามเงื่อนไขที่เลือก:
  - รายเดือน (Jan, Feb, ..., Dec)
  - สะสม (Jan YTD, Feb YTD, ...)
  - รายไตรมาส (Q1, Q2, Q3, Q4)
  - รายปี
  - ตามกลุ่มธุรกิจ/บริการ

---

## 🎯 Phase 1: Project Setup (วันที่ 1-2)

### 1.1 สร้างโครงสร้าง Project
```bash
univer/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app
│   │   ├── config.py                  # Configuration
│   │   ├── models/                    # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── report.py
│   │   │   └── filters.py
│   │   ├── routers/                   # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── report.py
│   │   ├── services/                  # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── data_loader.py
│   │   │   ├── report_calculator.py
│   │   │   └── univer_converter.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── email_sender.py
│   │       └── otp_generator.py
│   ├── data/
│   │   ├── profit_loss.csv
│   │   ├── other_income_expense.csv
│   │   └── user_whitelist.json
│   ├── tests/
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── components/
│   │   │   ├── Auth/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── OTPVerification.tsx
│   │   │   ├── Filters/
│   │   │   │   ├── MonthSelector.tsx
│   │   │   │   ├── QuarterSelector.tsx
│   │   │   │   ├── BusinessGroupSelector.tsx
│   │   │   │   └── FilterPanel.tsx
│   │   │   ├── Report/
│   │   │   │   ├── UniverReport.tsx
│   │   │   │   └── ExportButton.tsx
│   │   │   └── Layout/
│   │   │       ├── Header.tsx
│   │   │       └── Sidebar.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── authService.ts
│   │   │   └── reportService.ts
│   │   ├── types/
│   │   │   ├── auth.ts
│   │   │   ├── report.ts
│   │   │   └── univer.ts
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   └── useReport.ts
│   │   └── utils/
│   │       └── univerHelper.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env
├── docs/
│   ├── API.md
│   ├── DATA_STRUCTURE.md
│   └── DEPLOYMENT.md
├── PROJECT_PLAN.md
└── README.md
```

### 1.2 ติดตั้ง Dependencies

**Backend (requirements.txt)**:
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pandas==2.2.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
passlib==1.7.4
python-multipart==0.0.6
aiosmtplib==3.0.1
openpyxl==3.1.2
```

**Frontend (package.json)**:
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@univerjs/core": "^0.1.0",
    "@univerjs/design": "^0.1.0",
    "@univerjs/docs": "^0.1.0",
    "@univerjs/docs-ui": "^0.1.0",
    "@univerjs/engine-formula": "^0.1.0",
    "@univerjs/engine-render": "^0.1.0",
    "@univerjs/sheets": "^0.1.0",
    "@univerjs/sheets-formula": "^0.1.0",
    "@univerjs/sheets-ui": "^0.1.0",
    "@univerjs/ui": "^0.1.0",
    "axios": "^1.6.5",
    "antd": "^5.13.0"
  }
}
```

---

## 🎯 Phase 2: Backend Development (วันที่ 3-7)

### 2.1 Authentication System (วันที่ 3)
- [ ] Email domain validation
- [ ] OTP generation (6 digits, expire 5 minutes)
- [ ] OTP email sending
- [ ] Session management (JWT token)
- [ ] API endpoints:
  - `POST /auth/send-otp` - ส่ง OTP ไป email
  - `POST /auth/verify-otp` - ตรวจสอบ OTP และออก JWT token
  - `POST /auth/logout` - ลบ session

### 2.2 Data Loading & Processing (วันที่ 4-5)
- [ ] CSV file reader (pandas)
- [ ] Data validation
- [ ] Mapping columns สำหรับการคำนวณ
- [ ] Cache mechanism สำหรับ data ที่โหลดแล้ว

### 2.3 Report Calculator (วันที่ 6-7)
สร้าง service สำหรับคำนวณรายงาน โดยแบ่งเป็น:

#### 2.3.1 Revenue Calculation
```python
def calculate_revenue(df, filters):
    """
    คำนวณรายได้แยกตามกลุ่มธุรกิจ
    - กลุ่มธุรกิจโครงสร้างพื้นฐาน
    - กลุ่มธุรกิจโทรศัพท์ประจำที่และอินเตอร์เนตบรอดแบนด์
    - ... (7 กลุ่มทั้งหมด)
    """
```

#### 2.3.2 Cost Calculation
```python
def calculate_cost_of_service(df, filters):
    """
    คำนวณต้นทุนบริการ (TYPE = '02 ต้นทุนบริการ')
    แยกตามหมวดบัญชี:
    - C01 ค่าใช้จ่ายตอบแทนแรงงาน
    - C02 ค่าสวัสดิการ
    - ... (14 รายการทั้งหมด)
    """

def calculate_selling_expense(df, filters):
    """
    คำนวณค่าใช้จ่ายขายและการตลาด (TYPE = '03 ค่าใช้จ่ายขายและการตลาด')
    """

def calculate_admin_expense(df, filters):
    """
    คำนวณค่าใช้จ่ายบริหาร (TYPE = '04 ค่าใช้จ่ายสนับสนุน')
    """
```

#### 2.3.3 Profit Calculation
```python
def calculate_gross_profit(revenue, cost_of_service):
    """กำไรขั้นต้น = รายได้ - ต้นทุนบริการ"""

def calculate_ebit(gross_profit, selling_exp, admin_exp):
    """EBIT = กำไรขั้นต้น - ค่าใช้จ่ายขาย - ค่าใช้จ่ายบริหาร"""

def calculate_ebitda(ebit, depreciation, amortization):
    """EBITDA = EBIT + Depreciation + Amortization"""

def calculate_ebt(ebit, other_income, other_expense, financial_cost):
    """EBT = EBIT + รายได้อื่น - ค่าใช้จ่ายอื่น - ต้นทุนทางการเงิน"""
```

#### 2.3.4 Common Size Calculation
```python
def calculate_common_size(amount, base_revenue):
    """
    คำนวณเปอร์เซ็นต์เทียบกับรายได้
    Common Size % = (amount / revenue) * 100
    """
```

#### 2.3.5 Crosstab Creation
```python
def create_crosstab(df, row_structure, col_filters):
    """
    สร้าง crosstab ตามโครงสร้างที่กำหนด
    - rows: ตามโครงสร้างรายงาน P&L
    - columns: ตามเงื่อนไขที่เลือก (เดือน/ไตรมาส/กลุ่มธุรกิจ)
    """
```

### 2.4 Univer Snapshot Converter (วันที่ 7)
```python
def convert_to_univer_snapshot(df_report, formatting_rules):
    """
    แปลง DataFrame เป็น Univer snapshot format
    - กำหนดสี, ตัวหนา, ขีดเส้นใต้
    - Merge cells สำหรับ header
    - กำหนด number format (จำนวนเงิน, เปอร์เซ็นต์)
    - สร้าง formula สำหรับการคำนวณ

    Returns:
    {
        "id": "workbook-01",
        "name": "รายงานผลดำเนินงาน",
        "sheets": {
            "sheet-01": {
                "name": "P&L Report",
                "cellData": {...},
                "rowData": {...},
                "columnData": {...}
            }
        },
        "styles": {...}
    }
    """
```

### 2.5 API Endpoints (วันที่ 7)

#### Report Generation API
```python
@router.post("/api/report/generate")
async def generate_report(
    filters: ReportFilters,
    current_user: User = Depends(get_current_user)
):
    """
    Input (ReportFilters):
    {
        "months": [1, 2, 3],          // เดือนที่เลือก
        "year": 2025,
        "view_type": "monthly",        // monthly, quarterly, yearly
        "display_type": "actual_ytd",  // actual, ytd, both
        "business_groups": [],         // ถ้าเป็น [] = all
        "service_groups": [],
        "services": [],
        "show_common_size": true
    }

    Output:
    {
        "snapshot": {...},             // Univer snapshot
        "metadata": {
            "generated_at": "2025-01-22T...",
            "filters_applied": {...},
            "total_rows": 50,
            "total_columns": 12
        }
    }
    """
```

#### Filter Options API
```python
@router.get("/api/filters/options")
async def get_filter_options():
    """
    ดึงรายการตัวเลือกสำหรับ filter

    Output:
    {
        "years": [2023, 2024, 2025],
        "business_groups": [
            {"id": "1", "name": "โครงสร้างพื้นฐาน"},
            {"id": "2", "name": "โทรศัพท์ประจำที่ฯ"},
            ...
        ],
        "service_groups": [...],
        "services": [...]
    }
    """
```

---

## 🎯 Phase 3: Frontend Development (วันที่ 8-12)

### 3.1 Authentication UI (วันที่ 8)
- [ ] LoginForm component (กรอก email)
  - Validate email domain
  - แสดง error message
- [ ] OTPVerification component
  - Input OTP (6 digits)
  - Countdown timer (5 minutes)
  - Resend OTP button
- [ ] Protected route wrapper

### 3.2 Filter Panel (วันที่ 9)
- [ ] MonthSelector (multi-select checkbox)
- [ ] QuarterSelector (Q1, Q2, Q3, Q4 buttons)
- [ ] YearSelector (dropdown)
- [ ] ViewTypeSelector (radio: รายเดือน/ไตรมาส/ปี)
- [ ] DisplayTypeSelector (radio: เดือน/สะสม/ทั้งคู่)
- [ ] BusinessGroupSelector (tree select)
- [ ] CommonSizeToggle (switch: แสดง/ซ่อน %)
- [ ] "สร้างรายงาน" button

### 3.3 Univer Integration (วันที่ 10-11)

#### UniverReport Component
```typescript
interface UniverReportProps {
  snapshot: IWorkbookData;
  onExport?: () => void;
}

const UniverReport: React.FC<UniverReportProps> = ({ snapshot, onExport }) => {
  const univerRef = useRef<HTMLDivElement>(null);
  const [univer, setUniver] = useState<Univer | null>(null);

  useEffect(() => {
    // Initialize Univer
    const univerInstance = createUniver({
      locale: LocaleType.TH_TH,
      locales: { ... },
      presets: [
        UniverSheetsCorePreset({
          container: univerRef.current!,
        }),
      ],
    });

    // Load snapshot
    univerInstance.univerAPI.createWorkbook(snapshot);

    setUniver(univerInstance);

    return () => {
      univerInstance.dispose();
    };
  }, [snapshot]);

  return (
    <div className="univer-container">
      <div ref={univerRef} style={{ height: '100vh' }} />
      <ExportButton onClick={onExport} />
    </div>
  );
};
```

### 3.4 Export Functionality (วันที่ 11)
```typescript
const exportToExcel = async (univerAPI: FUniver) => {
  // ใช้ Univer API เพื่อ export เป็น .xlsx
  const workbook = univerAPI.getActiveWorkbook();
  const blob = await workbook.save();

  // Download file
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `รายงานผลดำเนินงาน_${new Date().toISOString()}.xlsx`;
  a.click();
};
```

### 3.5 Layout & UI Polish (วันที่ 12)
- [ ] Header (logo, user info, logout button)
- [ ] Sidebar (collapsible filter panel)
- [ ] Loading states
- [ ] Error handling & toast notifications
- [ ] Responsive design

---

## 🎯 Phase 4: Advanced Features (วันที่ 13-15)

### 4.1 Row/Column Grouping (Collapse/Expand) (วันที่ 13)
ใน Univer ใช้ฟีเจอร์ Row/Column Grouping:
```typescript
// สร้าง group สำหรับรายได้ (rows 2-9)
univerAPI.executeCommand({
  id: 'sheet.command.set-row-group',
  params: {
    startRow: 2,
    endRow: 9,
    level: 1,
  },
});

// สร้าง group สำหรับต้นทุนบริการ (rows 11-24)
univerAPI.executeCommand({
  id: 'sheet.command.set-row-group',
  params: {
    startRow: 11,
    endRow: 24,
    level: 1,
  },
});
```

### 4.2 Conditional Formatting (วันที่ 13)
- แถวหัวข้อหลัก (รายได้, ต้นทุน): สีเทาเข้ม, ตัวหนา
- แถวรายย่อย: สีขาว
- แถวผลรวม (กำไรขั้นต้น, EBIT, EBT): สีน้ำเงินอ่อน, ตัวหนา, ขีดเส้นใต้
- ค่าติดลบ: ตัวอักษรสีแดง
- Common Size %: สีเทาอ่อน

### 4.3 Number Formatting (วันที่ 14)
```python
def get_cell_format(cell_type, value):
    formats = {
        "currency": {
            "pattern": "#,##0.00",
            "prefix": "",
            "suffix": ""
        },
        "percentage": {
            "pattern": "0.00%",
        },
        "integer": {
            "pattern": "#,##0",
        }
    }
    return formats.get(cell_type)
```

### 4.4 MCP Server Integration (วันที่ 14-15)

#### ติดตั้ง MCP SDK
```bash
pip install mcp
```

#### สร้าง MCP Server
```python
# backend/mcp_server/server.py
from mcp import MCPServer, Tool

server = MCPServer("univer-report-server")

@server.tool()
async def get_report_data(filters: dict) -> dict:
    """
    MCP Tool สำหรับดึงข้อมูลรายงาน
    ให้ AI Agent เรียกใช้งานได้
    """
    # Logic เดียวกับ API endpoint
    result = await generate_report(filters)
    return result

@server.tool()
async def get_filter_options() -> dict:
    """
    MCP Tool สำหรับดึงตัวเลือก filter
    """
    options = await load_filter_options()
    return options

if __name__ == "__main__":
    server.run()
```

#### การใช้งาน MCP
User สามารถใช้ AI Agent (เช่น Claude Desktop) พูดคุยกับระบบ:
```
User: "ช่วยดึงรายงานผลดำเนินงานเดือนมกราคม 2025 ของกลุ่มธุรกิจ Fixed Line"
AI Agent -> เรียก MCP Tool get_report_data() -> ได้ข้อมูลกลับมา
```

---

## 🎯 Phase 5: Testing & Optimization (วันที่ 16-18)

### 5.1 Unit Testing (วันที่ 16)
**Backend Tests**:
```python
# tests/test_report_calculator.py
def test_calculate_revenue():
    df = load_test_data()
    result = calculate_revenue(df, filters={...})
    assert result['total'] == expected_value

def test_calculate_ebit():
    # Test EBIT calculation
    ...

def test_calculate_common_size():
    # Test percentage calculation
    ...
```

**Frontend Tests**:
```typescript
// src/components/Filters/__tests__/MonthSelector.test.tsx
describe('MonthSelector', () => {
  it('should select multiple months', () => {
    // Test logic
  });
});
```

### 5.2 Integration Testing (วันที่ 17)
- [ ] Test API endpoints
- [ ] Test authentication flow
- [ ] Test report generation with various filters
- [ ] Test export functionality

### 5.3 Performance Optimization (วันที่ 17-18)
- [ ] Add caching (Redis) สำหรับ report ที่เคยสร้างแล้ว
- [ ] Optimize pandas operations (use vectorization)
- [ ] Add pagination/lazy loading ถ้า report มีข้อมูลเยอะมาก
- [ ] Optimize Univer rendering (virtual scrolling)

### 5.4 User Acceptance Testing (วันที่ 18)
- [ ] ทดสอบกับ real users
- [ ] รวบรวม feedback
- [ ] ปรับแต่งตาม feedback

---

## 🎯 Phase 6: Deployment (วันที่ 19-20)

### 6.1 Backend Deployment
**Option 1: Docker**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./data ./data

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Option 2: Cloud Run / AWS Lambda**

### 6.2 Frontend Deployment
**Build for production**:
```bash
npm run build
```

**Deploy to**:
- Vercel
- Netlify
- AWS S3 + CloudFront

### 6.3 Environment Configuration
```bash
# .env.production
DATABASE_URL=...
SMTP_SERVER=...
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
JWT_SECRET=...
ALLOWED_EMAIL_DOMAINS=company.com,company.co.th
```

---

## 📝 ข้อควรระวังและ Best Practices

### Data Processing
1. **ใช้ pandas อย่างมีประสิทธิภาพ**:
   - ใช้ `.groupby()` แทน loop
   - ใช้ `.query()` สำหรับ filter
   - ใช้ `.pivot_table()` สำหรับ crosstab

2. **Handle missing data**:
   - กรณีเดือนไหนไม่มีข้อมูล แสดง 0 หรือ "-"
   - กรณี division by zero ใน Common Size

3. **Validate data**:
   - Check data types
   - Check required columns exist
   - Check date ranges

### Univer Integration
1. **Performance**:
   - ไม่ควรสร้าง snapshot ที่มีเซลล์เกิน 10,000 เซลล์
   - ใช้ lazy loading ถ้าข้อมูลเยอะ

2. **Styling**:
   - สร้าง style library ไว้ใช้ซ้ำ
   - ไม่ควรกำหนด style แบบ inline ทุก cell

3. **Formula**:
   - ใช้ formula ใน Univer สำหรับการคำนวณที่ user อาจจะแก้ไข
   - ส่งค่าสำเร็จจาก backend สำหรับค่าที่ไม่ควรแก้ไข

### Security
1. **Authentication**:
   - OTP expire หลัง 5 นาที
   - จำกัด rate limit (ส่ง OTP ได้ไม่เกิน 3 ครั้ง/ชั่วโมง)
   - ใช้ HTTPS เท่านั้น

2. **Data Access**:
   - ตรวจสอบ email domain ก่อนส่ง OTP
   - ตรวจสอบ JWT token ทุก request
   - ไม่ expose sensitive data ใน API response

---

## 📊 Timeline Summary

| Phase | Duration | Tasks |
|-------|----------|-------|
| Phase 1: Setup | 2 days | Project structure, dependencies |
| Phase 2: Backend | 5 days | Auth, data processing, API |
| Phase 3: Frontend | 5 days | UI components, Univer integration |
| Phase 4: Advanced | 3 days | Grouping, formatting, MCP |
| Phase 5: Testing | 3 days | Unit/integration tests, optimization |
| Phase 6: Deployment | 2 days | Docker, cloud deployment |
| **Total** | **20 days** | |

---

## 🎯 Success Criteria

- [ ] User สามารถ login ด้วย email + OTP ได้
- [ ] User สามารถเลือก filter ได้ (เดือน, ไตรมาส, กลุ่มธุรกิจ)
- [ ] รายงานแสดงผลบน Univer เหมือน Excel
- [ ] รายงานมีการคำนวณ EBIT, EBITDA, Common Size ถูกต้อง
- [ ] User สามารถ export เป็น Excel ได้
- [ ] User สามารถหุบ/ขยายรายการได้
- [ ] ระบบรองรับ MCP Server
- [ ] Response time < 3 วินาที สำหรับการสร้างรายงาน

---

## 📚 ทรัพยากรเพิ่มเติม

- [Univer Documentation](https://univer.ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [React Documentation](https://react.dev/)
- [MCP SDK](https://github.com/anthropics/model-context-protocol)
