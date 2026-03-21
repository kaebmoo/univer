# NT P&L Reconciliation Web App — Implementation Plan (v2)

## Context

รวม Python reconciliation scripts 4 ตัว (ตัดตัวที่ 5 ออกเนื่องจากซ้ำซ้อน) เป็น single-page web app:

| # | Python Script | หน้าที่ | สถานะ |
|---|---|---|---|
| 1 | `reconcile_nt_pl.py` | BU Level: CSV vs Excel, cross-sheet, alliance | ported |
| 2 | `reconcile_sg_svc_v2.py` | SG/Product: EBITDA, EBIT, cross-column | ported |
| 3 | `pl_reconciliation_enhanced.py` | Enhanced: completeness, cross-sheet, internal math, tie-out | ported |
| 4 | `pl_reconciliation_combined.py` | Combined file validation | ported |
| ~~5~~ | ~~`pl_reconciliation.py`~~ | ~~Basic 3-point check~~ | **ตัดออก** — ถูกครอบคลุมโดย Enhanced ทั้งหมด |

**เหตุผลที่ตัด `pl_reconciliation.py`:**
- Check 1 (Cost vs GL net profit) = Enhanced check 2c
- Check 2 (CSV vs Report net profit) = Enhanced check 1.2b
- Check 3 (Report vs Text tie-out) = Enhanced check 3
- Enhanced ตรวจเพิ่ม: Revenue, Expense, Internal Math, cross-sheet 3 คู่, ทั้ง 6 sheets

---

## Project Location

`/Users/seal/Documents/GitHub/univer/report_generator/reconciliation/pl-reconciliation-app/`

---

## Architecture: Upload Once, Run All

### ไฟล์ที่ upload (ครั้งเดียว)

| # | ไฟล์ | บังคับ? | ใช้โดย |
|---|------|:---:|--------|
| 1 | COSTTYPE MTH CSV | ใช่ | BU, SG, Enhanced |
| 2 | COSTTYPE YTD CSV | ใช่ | BU, SG, Enhanced |
| 3 | GLGROUP MTH CSV | ใช่ | BU, SG, Enhanced, Combined |
| 4 | GLGROUP YTD CSV | ใช่ | BU, SG, Enhanced, Combined |
| 5 | Report MTH Excel | ใช่ | BU, SG, Enhanced |
| 6 | Report YTD Excel | ใช่ | BU, SG, Enhanced |
| 7 | Combined Output Excel | ไม่ | Combined |
| 8 | Financial Statement TXT | ไม่ | Enhanced (tie-out) |

### Flow: กดปุ่มเดียว → รัน 4 reconcilers

```
Upload 6+2 files → Click "เริ่มตรวจสอบทั้งหมด"
    → Web Worker:
        1. Parse CSV (auto-detect encoding: UTF-8 → windows-874)
        2. Parse Excel (xlsx.js)
        3. Run BU Level reconciler        → results[]
        4. Run SG/Service reconciler      → results[]
        5. Run Enhanced reconciler        → results[]
        6. Run Combined reconciler (ถ้ามี) → results[]
    → รวม results ทั้งหมด → แสดง UI + Export Excel
```

---

## Project Structure

```
src/
  main.tsx
  index.css
  App.tsx                           # Single-page: upload → run → results

  utils/
    cn.ts                           # Tailwind merge
    encoding.ts                     # windows-874 auto-detect
    parsers.ts                      # parseThaiNumber(), parseNumber()
    tolerance.ts                    # TOLERANCE constants + createResult()

  lib/
    types.ts                        # CheckResult, FileSlots, Worker messages
    csv-reader.ts                   # CSV parse + aggregation (lodash-es)
    excel-reader.ts                 # ExcelSheetReader (BU level)
    excel-reader-sg.ts              # SG/Product layout detection
    text-reader.ts                  # .txt file parse
    constants.ts                    # ROW_MAPs, CHECKS, EBITDA constants
    ebitda-calc.ts                  # calcEbitFromCsv(), calcEbitdaFromCsv()

    reconcilers/
      bu-level.ts                   # reconcile_nt_pl.py
      enhanced.ts                   # pl_reconciliation_enhanced.py (ครอบคลุม basic)
      sg-svc.ts                     # reconcile_sg_svc_v2.py
      combined.ts                   # pl_reconciliation_combined.py

  workers/
    reconciliation.worker.ts        # Web Worker: parse + run all reconcilers

  stores/
    reconciliation-store.ts         # Zustand: files, results, loading, error

  components/
    FileUploadPanel.tsx             # 3 groups: CSV / Excel / Optional
    ResultsTable.tsx                # Category filter, status filter, search
    SummaryCards.tsx                 # Pass/Fail/Total/Rate
    ExportButton.tsx                # Excel export
    ProgressBar.tsx                 # Worker progress
```

---

## Key Technical Decisions

### 1. Web Worker
- ทุก reconciler เป็น pure function → รันใน worker ได้ทั้งหมด
- Main thread เหลือแค่ UI + progress bar
- Worker ส่ง progress message ที่แต่ละขั้น

### 2. State Management (Zustand)
- Store เดียว: `files`, `results`, `loading`, `progress`, `error`
- ไม่ต้องแยก state per mode เพราะรันทั้งหมดพร้อมกัน

### 3. Data Manipulation (lodash-es แทน pandas)
- `groupBy`, `sumBy` จาก lodash-es
- NaN safety: `parseCsvValue()` → `parseFloat(val) || 0` ทุกจุด
- Empty string handling เหมือน pandas

### 4. Encoding (windows-874)
- `TextDecoder('utf-8')` → check `\uFFFD` → fallback `TextDecoder('windows-874')`
- ใช้กับทั้ง CSV และ TXT

### 5. Excel cell values (xlsx.js)
- `sheet_to_json({header:1, defval:null})` ให้ raw `.v` values
- `parseThaiNumber()` เป็น safety net สำหรับ text-formatted cells

### 6. Single-file build
- System fonts only, lucide-react tree-shake, no images
- Bundle: ~550KB HTML + ~400KB worker JS

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| UI freezing | Web Worker + Progress bar |
| pandas → TS accuracy | lodash-es + `parseFloat \|\| 0` + golden file test |
| CSV encoding ภาษาไทย | `TextDecoder('windows-874')` |
| xlsx.js cell types | `sheet_to_json` raw values + `parseThaiNumber()` safety net |
| Excel merged cells | Test with actual files; fallback cell-by-cell read |
| 0-based vs 1-based indexing | Centralized in excel-reader |
| SG matching accuracy | 3-tier `matchSg()` ported verbatim |
| EBITDA SUB_GROUP filtering | Filter conditions ported verbatim |

---

## Files to Reference (Python Sources)

| File | Lines | Status |
|------|-------|--------|
| `reconcile_nt_pl.py` | 598 | Ported → `bu-level.ts` |
| `reconcile_sg_svc_v2.py` | 1,265 | Ported → `sg-svc.ts` + `ebitda-calc.ts` |
| `pl_reconciliation_enhanced.py` | 619 | Ported → `enhanced.ts` |
| `pl_reconciliation_combined.py` | 330 | Ported → `combined.ts` |
| ~~`pl_reconciliation.py`~~ | ~~212~~ | ~~ตัดออก~~ |

---

## Verification

1. `npm run dev` → verify UI loads, upload files, progress bar works
2. Upload actual data from `data/` + `report/` directories
3. Compare results count and values with Python output (golden file)
4. Export Excel → verify format
5. `npm run build` → verify bundle size < 1MB total
