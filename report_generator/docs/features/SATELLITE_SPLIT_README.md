# SATELLITE Service Group Split Feature

## 📋 ภาพรวม

Feature นี้แยก `4.5 กลุ่มบริการ SATELLITE` ออกเป็น 2 กลุ่มย่อย และเพิ่มคอลัมน์สรุปยอดรวม:

- **4.5.1 กลุ่มบริการ Satellite-NT** (12 products)
- **4.5.2 กลุ่มบริการ Satellite-ไทยคม** (4 products)
- **รวม 4.5 SATELLITE** (virtual column - sum ของทั้ง 2 กลุ่ม)

## ✅ รองรับรายงานทั้งหมด 6 รูปแบบ

| # | Report Type | Detail Level | ผลลัพธ์ |
|---|-------------|--------------|---------|
| 1 | COSTTYPE | BU_ONLY | ✅ Sum อัตโนมัติที่ BU level |
| 2 | COSTTYPE | BU_SG | ✅ แสดง "รวม 4.5 SAT", 4.5.1, 4.5.2 |
| 3 | COSTTYPE | BU_SG_PRODUCT | ✅ แสดง "รวม 4.5 SAT", 4.5.1+products, 4.5.2+products |
| 4 | GLGROUP | BU_ONLY | ✅ Sum อัตโนมัติที่ BU level |
| 5 | GLGROUP | BU_SG | ✅ แสดง "รวม 4.5 SAT", 4.5.1, 4.5.2 |
| 6 | GLGROUP | BU_SG_PRODUCT | ✅ แสดง "รวม 4.5 SAT", 4.5.1+products, 4.5.2+products |

---

## 📁 ไฟล์ที่แก้ไข

### 1. **Config File** (ใหม่)
```
config/satellite_config.py
```
- กำหนด PRODUCT_KEY ที่จัดอยู่ในแต่ละกลุ่ม
- Feature toggle: `ENABLE_SATELLITE_SPLIT`
- ชื่อคอลัมน์สรุป: `SATELLITE_SUMMARY_NAME`

### 2. **Data Processor**
```
src/data_loader/data_processor.py
```
- เพิ่ม `_split_satellite_service_group()` method
- แยก SERVICE_GROUP ตาม PRODUCT_KEY
- ทำงานอัตโนมัติใน `process_data()`

### 3. **Data Aggregator**
```
src/data_loader/data_aggregator.py
```
- เพิ่ม `get_satellite_summary()` - sum ที่ BU+SG level
- เพิ่ม `get_satellite_summary_product()` - sum ที่ product level

### 4. **BU_SG Builder**
```
src/report_generator/columns/bu_sg_builder.py
```
- แก้ `_build_bu_columns()` - เพิ่ม logic แทรกคอลัมน์ "รวม 4.5 SATELLITE"
- เพิ่ม `_create_satellite_summary_column()` - สร้าง virtual column

### 5. **BU_SG_Product Builder**
```
src/report_generator/columns/bu_sg_product_builder.py
```
- แก้ `_build_bu_columns()` - เพิ่ม logic แทรกคอลัมน์ "รวม 4.5 SATELLITE"
- เพิ่ม `_create_satellite_summary_column()` - สร้าง virtual column

### 6. **Data Writer**
```
src/report_generator/writers/data_writer.py
```
- แก้ `_get_cell_value()` - รองรับ `satellite_summary` column type
- เพิ่ม `_get_satellite_summary_value()` - คำนวณค่า sum

---

## 🔧 วิธีใช้งาน

### การ Enable/Disable Feature

แก้ไขไฟล์ `config/satellite_config.py`:

```python
# Enable feature
ENABLE_SATELLITE_SPLIT = True

# Disable feature (ใช้ SERVICE_GROUP แบบเดิม)
ENABLE_SATELLITE_SPLIT = False
```

### การเปลี่ยนแปลงการจัดกลุ่ม

แก้ไขใน `config/satellite_config.py`:

```python
SATELLITE_GROUPS = {
    'NT': {
        'name': '4.5.1 กลุ่มบริการ Satellite-NT',
        'product_keys': [
            '102010401',  # เพิ่ม/ลบ PRODUCT_KEY ตามต้องการ
            # ...
        ]
    },
    'THAICOM': {
        'name': '4.5.2 กลุ่มบริการ Satellite-ไทยคม',
        'product_keys': [
            '102010409',
            # ...
        ]
    }
}
```

---

## 📊 โครงสร้างคอลัมน์ที่ได้

### BU_SG_PRODUCT Level (ตัวอย่าง)

```
รายละเอียด | รวมทั้งสิ้น | รวม BU | 4.4 SG | รวม 4.5 SATELLITE ⭐ | 4.5.1 SAT-NT | Product1 | Product2 | ... | 4.5.2 SAT-ไทยคม | Product1 | ... | 4.6 SG
```

---

## 🎯 การทำงาน

### Step 1: Data Processing
```python
# src/data_loader/data_processor.py
df = self._split_satellite_service_group(df)
# แยก SERVICE_GROUP ตาม PRODUCT_KEY
```

### Step 2: Aggregation
```python
# src/data_loader/data_aggregator.py
total = aggregator.get_satellite_summary(group, sub_group, bu)
# คำนวณ sum ของ 4.5.1 + 4.5.2
```

### Step 3: Column Building
```python
# Column builders
bu_columns.append(self._create_satellite_summary_column(bu))
# เพิ่มคอลัมน์ "รวม 4.5 SATELLITE"
```

### Step 4: Data Writing
```python
# data_writer.py
value = self._get_satellite_summary_value(col, label, aggregator, all_row_data, main_group)
# เขียนค่าลงเซลล์
```

---

## 📦 การจัดกลุ่ม PRODUCT_KEY

### กลุ่ม 4.5.1 Satellite-NT (12 products)
```
102010401 - บริการ NT TV Transmission
102010402 - บริการ NT GlobeSat
102010403 - บริการ INMARSAT
102010404 - บริการ NT iP Star
102010406 - บริการ NT Satellite Platform
102010407 - บริการ Ground Segment as a Service (GSaaS)
102010413 - บริการ DTH Platform
102010414 - Foreign Satellite Transponder
102010415 - บริการ NT nexConnect
103010016 - บริการ NT e-Entertainment
204060002 - บริการสื่อสัญญาณถ่ายทอดภาพและเสียง (TV Encoder Decoder)
204070003 - บริการ iP Star
```

### กลุ่ม 4.5.2 Satellite-ไทยคม (4 products)
```
102010409 - Thaicom 4 Satellite Wholesale Transponder
102010410 - Thaicom 4 Satellite Ratail Transponder
102010411 - Thaicom 6 Satellite Wholesale Transponder
102010412 - Thaicom 6 Satellite Ratail Transponder
```

---

## 🔄 วิธี Revert กลับ

### Option 1: Disable Feature
```python
# config/satellite_config.py
ENABLE_SATELLITE_SPLIT = False
```

### Option 2: แก้ไข Code
ใน `src/data_loader/data_processor.py`:
```python
def process_data(self, df, report_type="costtype"):
    # ...

    # Comment บรรทัดนี้
    # df = self._split_satellite_service_group(df)

    return df
```

---

## ⚠️ ข้อควรระวัง

1. **PRODUCT_KEY ต้องถูกต้อง**
   - ถ้า CSV มี PRODUCT_KEY ที่ไม่อยู่ใน config → จะแสดง warning
   - ตรวจสอบ log: `⚠ Unmatched: X rows`

2. **Column Order**
   - คอลัมน์ "รวม 4.5 SATELLITE" จะแทรกหลัง SERVICE_GROUP ที่ขึ้นต้นด้วย `4.4`
   - ถ้าไม่มี `4.4` → จะแทรกก่อน `4.6`

3. **Calculated Rows**
   - ทุก calculated row จะคำนวณ sum อัตโนมัติ
   - ไม่ต้อง config เพิ่มเติม

---

## 🧪 การทดสอบ

### Test 1: ตรวจสอบการแยกข้อมูล
```bash
python generate_report.py --report-type COSTTYPE --period MTH --detail-level BU_SG_PRODUCT
```

ตรวจสอบ log:
```
Found X SATELLITE rows - splitting...
SATELLITE split complete:
  ✓ Updated: X rows
  → 4.5.1 บริการ Satellite-NT: X rows
  → 4.5.2 บริการ Satellite-ไทยคม: X rows
```

### Test 2: ตรวจสอบ Excel Output
1. เปิดไฟล์ Excel ที่ generate
2. หาคอลัมน์ "รวม 4.5 SATELLITE"
3. ตรวจสอบว่าค่า = 4.5.1 + 4.5.2

### Test 3: ทดสอบทุกรูปแบบ
```bash
# BU_ONLY (COSTTYPE)
python generate_report.py --detail-level BU_ONLY

# BU_SG (COSTTYPE)
python generate_report.py --detail-level BU_SG

# BU_SG_PRODUCT (COSTTYPE)
python generate_report.py --detail-level BU_SG_PRODUCT

# GLGROUP
python generate_report.py --report-type GLGROUP --detail-level BU_SG_PRODUCT
```

---

## 📝 Changelog

### Version 1.0.0 (2025-12-15)
- ✅ เพิ่ม feature แยก SATELLITE service group
- ✅ รองรับทั้ง 6 รูปแบบรายงาน
- ✅ เพิ่ม virtual column "รวม 4.5 SATELLITE"
- ✅ จัดกลุ่มตาม PRODUCT_KEY (16 products)

---

## 🆘 Troubleshooting

### ปัญหา: ไม่เห็นคอลัมน์ "รวม 4.5 SATELLITE"

**สาเหตุ:**
- `ENABLE_SATELLITE_SPLIT = False`
- ไม่มีข้อมูล SATELLITE ใน CSV
- BU ไม่ใช่ "4.กลุ่มธุรกิจ FIXED LINE & BROADBAND"

**วิธีแก้:**
1. ตรวจสอบ `config/satellite_config.py`
2. ตรวจสอบ log เมื่อ run
3. ตรวจสอบ CSV ว่ามี SERVICE_GROUP = "4.5 กลุ่มบริการ SATELLITE"

### ปัญหา: Unmatched product keys

**สาเหตุ:**
- CSV มี PRODUCT_KEY ที่ไม่อยู่ใน config

**วิธีแก้:**
1. ดู warning log: `Product keys: [...]`
2. เพิ่ม PRODUCT_KEY ใน `config/satellite_config.py`

---

## 👥 ผู้พัฒนา

Feature นี้พัฒนาโดย: Claude Code
วันที่: 15 ธันวาคม 2025

---

## 📚 เอกสารเพิ่มเติม

- [config/satellite_config.py](config/satellite_config.py) - Configuration file
- [Data Processor Documentation](src/data_loader/data_processor.py)
- [Data Aggregator Documentation](src/data_loader/data_aggregator.py)
