# NT P&L Reconciliation Web App

เว็บแอปสำหรับตรวจกระทบยอด P&L ของ NT ระหว่างไฟล์ CSV source data, Excel report, และไฟล์เสริมบางประเภท โดยประมวลผลทั้งหมดใน browser และไม่ส่งข้อมูลออกนอกเครื่อง

## ภาพรวม

โปรแกรมนี้เป็นหน้าเว็บสำหรับรวม workflow ของ reconciliation เดิมที่เคยแยกเป็นหลายสคริปต์ ให้ใช้งานผ่าน UI เดียว โดยผู้ใช้สามารถ:

- อัปโหลดไฟล์หลายชุดพร้อมกัน แล้วให้ระบบจำแนกประเภทไฟล์อัตโนมัติจากชื่อไฟล์
- รันการตรวจสอบหลายหมวดในครั้งเดียว
- ดูสรุปผล PASS/FAIL บนหน้าเว็บ
- ค้นหา กรอง และแบ่งหน้าผลลัพธ์
- Export ผลการตรวจสอบออกเป็น Excel ได้

การประมวลผลใช้ Web Worker เพื่อไม่ให้หน้าเว็บค้างระหว่างอ่านไฟล์และคำนวณผล

## ความสามารถหลัก

- BU Level reconciliation
- SG/Service reconciliation
- Enhanced reconciliation
- Combined output reconciliation เมื่อมีไฟล์ combined
- Tie-out กับ financial statement เมื่อมีไฟล์ `.txt`
- Export ผลทั้งหมดหรือผลที่กรองแล้วเป็น `.xlsx`
- ทำงานแบบ client-side ใน browser

## Tech Stack

- React 19
- TypeScript
- Vite
- Zustand
- SheetJS (`xlsx`)
- PapaParse

## โครงสร้างสำคัญ

```text
pl-reconciliation-app/
├── src/
│   ├── components/               # UI components
│   ├── lib/                      # constants, types, file classifier, readers, reconcilers
│   ├── stores/                   # Zustand store
│   ├── workers/                  # Web Worker สำหรับประมวลผล
│   ├── App.tsx                   # หน้า main
│   └── main.tsx
├── package.json
├── vite.config.ts
└── index.html
```

## ไฟล์ที่ต้องใช้

ระบบรองรับการอัปโหลดไฟล์โดยอาศัยการจำแนกจากชื่อไฟล์ ถ้าชื่อไฟล์ไม่ตรง pattern ระบบจะไม่รู้จักไฟล์นั้น

### ไฟล์จำเป็นขั้นต่ำ

ต้องมีอย่างน้อย 6 ไฟล์เพื่อรันชุดตรวจหลัก:

1. `TRN_PL_COSTTYPE_NT_MTH_TABLE_*.csv`
2. `TRN_PL_COSTTYPE_NT_YTD_TABLE_*.csv`
3. `TRN_PL_GLGROUP_NT_MTH_TABLE_*.csv`
4. `TRN_PL_GLGROUP_NT_YTD_TABLE_*.csv`
5. Excel report รายเดือน (`report` หรือชื่อที่มี `mth` และไม่ใช่ `combined`)
6. Excel report สะสม (`ytd`)

### ไฟล์เสริม

- Combined output Excel: ชื่อไฟล์ต้องมีคำว่า `combined`
- Financial statement text file: ไฟล์นามสกุล `.txt`

### กฎการจำแนกไฟล์

ระบบใช้ชื่อไฟล์เพื่อ map เข้า key ภายในดังนี้:

| ประเภท | key ภายใน | เงื่อนไขชื่อไฟล์โดยย่อ |
| --- | --- | --- |
| COSTTYPE MTH CSV | `costtypeMth` | มี `costtype` และ `mth` และลงท้ายด้วย `.csv` |
| COSTTYPE YTD CSV | `costtypeYtd` | มี `costtype` และ `ytd` และลงท้ายด้วย `.csv` |
| GLGROUP MTH CSV | `glgroupMth` | มี `glgroup` และ `mth` และลงท้ายด้วย `.csv` |
| GLGROUP YTD CSV | `glgroupYtd` | มี `glgroup` และ `ytd` และลงท้ายด้วย `.csv` |
| Report MTH Excel | `reportMth` | มี `report` และไม่มี `ytd`/`combined` และเป็น `.xlsx` หรือ `.xls` |
| Report YTD Excel | `reportYtd` | มี `ytd` และเป็น `.xlsx` หรือ `.xls` |
| Combined Excel | `combinedExcel` | มี `combined` และเป็น `.xlsx` หรือ `.xls` |
| Statement TXT | `stmtTxt` | ลงท้ายด้วย `.txt` |

ถ้าระบบขึ้นข้อความว่าไม่สามารถระบุไฟล์ได้ ให้ตรวจชื่อไฟล์ก่อนเป็นอย่างแรก

## เงื่อนไขการรัน

ระบบจะรัน reconciliation ตามไฟล์ที่มี:

- ถ้ามี CSV 4 ไฟล์ + Excel 2 ไฟล์: รัน `BU Level`, `SG/Service`, `Enhanced`
- ถ้ามี `combinedExcel` เพิ่ม: รัน `Combined`
- ถ้ามี `stmtTxt` เพิ่ม: Enhanced checks จะสามารถ tie-out กับงบการเงินได้

ถ้าไฟล์ไม่ครบขั้นต่ำ ระบบจะไม่เริ่มประมวลผลและจะแจ้งว่าข้อมูลไม่เพียงพอ

## วิธีติดตั้งและรัน

### 1. ติดตั้ง dependencies

```bash
cd report_generator/reconciliation/pl-reconciliation-app
npm install
```

### 2. รันโหมดพัฒนา

```bash
npm run dev
```

จากนั้นเปิด URL ที่ Vite แสดงใน terminal

### 3. สร้าง production build

```bash
npm run build
```

### 4. ทดสอบ production build ในเครื่อง

```bash
npm run preview
```

## ลักษณะของ build

โปรเจกต์นี้ใช้ `vite-plugin-singlefile` ดังนั้น production build ถูกออกแบบให้รวม asset เป็นไฟล์เดียวมากที่สุด เหมาะกับการส่งต่อหรือเปิดใช้งานแบบ static โดยไม่ต้องมี backend เฉพาะทาง

## วิธีใช้งานหน้าเว็บ

1. เปิดหน้าเว็บ
2. อัปโหลด CSV source data
3. อัปโหลด Excel reports
4. ถ้ามี ให้อัปโหลดไฟล์ `combined` และ/หรือ `.txt`
5. กดปุ่ม `เริ่มตรวจสอบทั้งหมด`
6. รอ progress bar จนเสร็จ
7. ตรวจผลลัพธ์ในตาราง
8. ใช้ filter เพื่อดูเฉพาะ PASS, FAIL, หรือหมวดที่สนใจ
9. Export ผลลัพธ์เป็น Excel เมื่อจำเป็น

## สิ่งที่ระบบตรวจ

จาก implementation ปัจจุบัน ระบบครอบคลุมการตรวจหลักดังนี้:

- CSV vs Excel totals
- CSV vs Excel by BU
- Cross-sheet consistency
- Column-total checks
- Alliance consistency
- Service group checks
- Product checks
- EBIT / EBITDA checks
- Cross-column checks
- Enhanced validation
- Combined output validation

ชื่อหมวดที่แสดงในผลลัพธ์จะขึ้นกับ reconciler ที่สร้างผลตรวจใน worker

## การอ่านผลลัพธ์

หน้าเว็บจะแสดง:

- จำนวนรายการที่ตรวจทั้งหมด
- จำนวนที่ผ่าน
- จำนวนที่ไม่ผ่าน
- อัตราผ่าน

ตารางผลลัพธ์มีข้อมูลหลักต่อรายการ เช่น:

- `Category`
- `Check`
- `Source Value`
- `Target Value`
- `Difference`
- `Status`

สถานะมี 2 แบบ:

- `PASS`
- `FAIL`

## การ Export

มี 2 รูปแบบ:

### Export ทั้งหมด

ปุ่ม `Export Excel` จะสร้างไฟล์ประมาณนี้:

- `Summary`
- `All Checks`
- `Failed Checks` ถ้ามีรายการไม่ผ่าน
- sheets แยกตาม category ได้สูงสุด 50 ชีต

ชื่อไฟล์จะอยู่ในรูปแบบ:

```text
reconciliation_All_<timestamp>.xlsx
```

### Export เฉพาะผลที่กรอง

ในตารางผลลัพธ์สามารถ export เฉพาะข้อมูลที่ค้นหา/กรองอยู่ได้ โดยไฟล์จะมี:

- `Summary`
- `Filtered Results`

## ข้อจำกัดที่ควรรู้

- การจำแนกไฟล์อาศัยชื่อไฟล์ ไม่ได้อ่าน metadata ของไฟล์เพื่อตรวจชนิดเชิงลึก
- ถ้าชื่อ Excel YTD มีเพียงคำว่า `ytd` ระบบจะจัดเป็น `reportYtd` แม้ชื่อจะไม่ได้ขึ้นต้นด้วย `Report`
- ถ้ามีไฟล์ชื่อคล้ายกันหลายไฟล์ในชุดเดียว ระบบจะจับคู่ตาม rule ตัวแรกที่ match
- การประมวลผลเกิดใน browser ดังนั้นขนาดไฟล์ใหญ่จะกิน memory ของเครื่องผู้ใช้
- ตอนนี้ไม่มีระบบ persist state ถ้า refresh หน้า ไฟล์และผลลัพธ์จะหาย
- ไม่มี backend สำหรับเก็บประวัติการรันหรือ audit trail

## แนวทางเตรียมข้อมูล

- ใช้ชุด CSV เดียวกับที่นำไปสร้าง Excel report
- ตั้งชื่อไฟล์ให้ตรง pattern ที่ระบบรู้จัก
- ตรวจ encoding ของ CSV ให้ถูกต้องตามข้อมูลต้นทาง
- ควรทดสอบด้วยไฟล์ MTH/YTD ที่เป็นงวดเดียวกัน

## Troubleshooting

### ระบบแจ้งว่าไฟล์ไม่เพียงพอ

ตรวจว่ามีครบ 6 ไฟล์หลัก:

- COSTTYPE MTH
- COSTTYPE YTD
- GLGROUP MTH
- GLGROUP YTD
- Report MTH
- Report YTD

### ระบบบอกว่าไม่รู้จักไฟล์

ตรวจชื่อไฟล์ให้มีคำสำคัญที่ระบบใช้จับคู่ เช่น `costtype`, `glgroup`, `mth`, `ytd`, `combined`

### หน้าเว็บค้างหรือช้า

- ตรวจขนาดไฟล์ input
- ลองใช้ browser รุ่นใหม่
- เปิด DevTools เพื่อตรวจ error จาก worker

### ผลไม่ตรงที่คาด

- ตรวจว่า CSV และ Excel มาจากรอบข้อมูลเดียวกัน
- ตรวจว่าอัปโหลดไฟล์ถูกประเภท
- ตรวจว่าไฟล์ `.txt` และ `combined` เป็นงวดเดียวกับไฟล์หลัก

## คำสั่งที่ใช้บ่อย

```bash
npm install
npm run dev
npm run build
npm run preview
```

## หมายเหตุ

README นี้อธิบายตาม implementation ปัจจุบันของแอปในโฟลเดอร์นี้โดยตรง ถ้ามีการเปลี่ยนกฎการจำแนกไฟล์, เพิ่ม reconciler, หรือปรับรูปแบบผลลัพธ์ ควรอัปเดตเอกสารนี้พร้อมกัน