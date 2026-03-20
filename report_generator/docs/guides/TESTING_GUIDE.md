# 🧪 Testing Guide - Phase 2B

**Created:** 2025-11-27  
**Purpose:** Test new modular architecture

---

## 📋 Test Scripts Created

### 1. test_1_imports.py
**Purpose:** Test if all modules can be imported

**What it tests:**
- ✅ Core imports (ReportBuilder, ReportConfig)
- ✅ Config creation
- ✅ Builder initialization
- ✅ All writers initialized
- ✅ Formatter initialized

**Run:**
```bash
python3 test_1_imports.py
```

**Expected:** All imports successful, no errors

---

### 2. test_2_generate.py
**Purpose:** Test if report can be generated

**What it tests:**
- ✅ Data loading (CSV)
- ✅ Data processing
- ✅ Report generation
- ✅ Output file created
- ✅ File size reasonable

**Run:**
```bash
python3 test_2_generate.py
```

**Expected:** Excel file created in `output/test_new_module.xlsx`

**Prerequisites:**
- Data file must exist: `data/TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv`

---

### 3. test_3_compare.py
**Purpose:** Compare old vs new implementation

**What it tests:**
- ✅ Generate with main_generator.py (old)
- ✅ Generate with new modules
- ✅ Compare file sizes
- ✅ Compare worksheet dimensions
- ✅ Compare sample cells

**Run:**
```bash
python3 test_3_compare.py
```

**Expected:** 
- Both files generated
- Similar file sizes
- Same dimensions
- Sample cells match

**Output:**
- `output/old_method.xlsx`
- `output/new_method.xlsx`

---

### 4. run_all_tests.py
**Purpose:** Run all tests in sequence

**Run:**
```bash
python3 run_all_tests.py
```

**Expected:** All 3 tests pass

---

## 🚀 Quick Start

### Option A: Run All Tests

```bash
cd /Users/seal/Documents/GitHub/univer/report_generator
python3 run_all_tests.py
```

### Option B: Run Individual Tests

```bash
# Test 1: Imports
python3 test_1_imports.py

# Test 2: Generation
python3 test_2_generate.py

# Test 3: Comparison
python3 test_3_compare.py
```

---

## ✅ Success Criteria

### Test 1: Import Test
```
✅ Core imports successful
✅ Config created: COSTTYPE
✅ ReportBuilder created
✅ Column builder: BUSGProductBuilder
✅ Formatter: CellFormatter
✅ ALL IMPORT TESTS PASSED!
```

### Test 2: Generate Test
```
✅ Imports successful
✅ Data file found
✅ Loaded XXX rows
✅ Data processed
✅ Config created
✅ Builder created
✅ Report generated!
✅ File exists
✅ File size: XX.X KB
✅ REPORT GENERATION TEST PASSED!
```

### Test 3: Compare Test
```
✅ OLD method done: XX.X KB
✅ NEW method done: XX.X KB
✅ File sizes similar
✅ Dimensions match
✅ Sample cells match
✅ COMPARISON TEST COMPLETE!
```

---

## 🔍 Manual Verification

After tests pass, manually verify:

### 1. Open Both Files in Excel

```bash
# Open old method
open output/old_method.xlsx

# Open new method
open output/new_method.xlsx
```

### 2. Visual Comparison Checklist

**Headers:**
- [ ] Company name (B2)
- [ ] Report title (B3)
- [ ] Period description (B4)
- [ ] Info box (G1-J5)

**Column Headers:**
- [ ] รายละเอียด column (B6-B9)
- [ ] รวมทั้งสิ้น column (C6-C9)
- [ ] BU headers (row 6)
- [ ] รวม BU columns (merged 6-9)
- [ ] SG headers (row 7)
- [ ] รวม SG columns (merged 7-9) ← CRITICAL
- [ ] Product keys (row 8)
- [ ] Product names (row 9)

**Data Rows:**
- [ ] All row labels present
- [ ] Values in Grand Total column
- [ ] Values in BU Total columns
- [ ] Values in SG Total columns ← CRITICAL
- [ ] Values in Product columns
- [ ] Ratio rows (สัดส่วนต่อรายได้) show percentages

**Formatting:**
- [ ] Section headers (orange background)
- [ ] BU colors applied
- [ ] Borders present
- [ ] Number formats correct (1,234.00)
- [ ] Percentages formatted (12.34%)
- [ ] Freeze panes at correct position

**Remarks:**
- [ ] "หมายเหตุ:" title present
- [ ] Remark lines present
- [ ] Formatting correct

---

## ⚠️ Common Issues

### Issue 1: Data file not found
```
❌ Data file not found: data/TRN_PL_COSTTYPE_NT_MTH_TABLE_20251031.csv
```

**Solution:**
- Ensure data file exists
- Check path is correct
- File must be in `data/` directory

### Issue 2: Import error
```
ModuleNotFoundError: No module named 'src.report_generator'
```

**Solution:**
- Run from project root directory
- Check `sys.path.insert(0, ...)` in script
- Verify directory structure

### Issue 3: Different output
```
⚠️ File sizes differ significantly
```

**Solution:**
- This may be OK (different compression)
- Check dimensions match
- Check sample cells match
- Visual comparison in Excel

---

## 📊 Expected Output

### Console Output (Success)

```
============================================================
Master Test Suite - Report Generator
============================================================

🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷
Running: Test 1: Import Test
🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷

... (test output) ...

✅ Test 1: Import Test - PASSED

🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷
Running: Test 2: Report Generation Test
🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷

... (test output) ...

✅ Test 2: Report Generation Test - PASSED

🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷
Running: Test 3: Comparison Test
🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷

... (test output) ...

✅ Test 3: Comparison Test - PASSED

============================================================
TEST SUMMARY
============================================================
✅ PASS - Test 1: Import Test
✅ PASS - Test 2: Report Generation Test
✅ PASS - Test 3: Comparison Test

============================================================
Result: 3/3 tests passed
============================================================

🎉 ALL TESTS PASSED! 🎉

The new modular architecture is working correctly!
```

---

## 🎯 Next Steps After Testing

### If All Tests Pass:

1. **Phase 2C** (Optional):
   - Create BUOnlyBuilder
   - Create BUSGBuilder
   - Test new report types

2. **Phase 3** (Integration):
   - Update CLI (src/cli/cli.py)
   - Update Web API (src/web/routes/report.py)
   - Update test_all_reports.py

3. **Documentation**:
   - Update README.md
   - Update USAGE.md
   - Add examples

### If Tests Fail:

1. Read error messages carefully
2. Check which test failed
3. Review the specific module
4. Fix issues
5. Re-run tests

---

## 📞 Support

**Questions?**
- Check error messages
- Review module docstrings
- Check `PHASE2B_COMPLETE.md`

**Found a bug?**
- Note which test failed
- Note error message
- Check relevant module

---

**Created:** 2025-11-27  
**Status:** Ready for Testing  
**Run:** `python3 run_all_tests.py`
