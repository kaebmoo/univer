# Tests Directory

โฟลเดอร์นี้รวมไฟล์ test และ utility scripts ทั้งหมด

## การรัน Tests

### Quick Tests
```bash
# Test imports
python test_1_imports.py

# Test report generation
python test_2_generate.py

# Run all tests
python run_all_tests.py
```

### Using pytest
```bash
cd ..
pytest tests/
```

## ไฟล์ Test หลัก

### Unit Tests
- `test_1_imports.py` - ทดสอบการ import modules
- `test_2_generate.py` - ทดสอบการสร้างรายงาน
- `test_3_compare.py` - เปรียบเทียบ old vs new implementation

### Feature Tests
- `test_all_reports.py` - สร้างรายงานทุกแบบ (COSTTYPE/GLGROUP × MTH/YTD)
- `test_phase2c.py` - ทดสอบระดับความละเอียดทั้ง 3 แบบ
- `test_glgroup.py` - ทดสอบรายงาน GLGROUP
- `test_glgroup_loading.py` - ทดสอบการโหลดข้อมูล GLGROUP
- `test_ytd_reports.py` - ทดสอบรายงาน YTD
- `test_fix.py` - ทดสอบการแก้ไขปัญหา

### Check Scripts
- `check_glgroup_data.py` - ตรวจสอบโครงสร้างข้อมูล GLGROUP
- `check_ytd_tax.py` - ตรวจสอบข้อมูลภาษีใน YTD

### Quick Tests
- `simple_test.py` - ทดสอบแบบง่าย
- `quick_test_glgroup.py` - ทดสอบ GLGROUP แบบเร็ว
- `quick_fix_guide.py` - คู่มือแก้ไขด่วน
- `direct_test_glgroup.py` - ทดสอบ GLGROUP โดยตรง

## Requirements

ต้องติดตั้ง dependencies จาก `requirements.txt` ก่อน:
```bash
cd ..
pip install -r requirements.txt
```

## หมายเหตุ

- ไฟล์ test ทั้งหมดใช้ relative imports จาก parent directory
- ต้องมีไฟล์ CSV ใน `data/` directory เพื่อรัน tests บางตัว
- Output files จะถูกสร้างใน `output/` directory
