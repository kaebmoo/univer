# Fix: Product-Level Line Items in Excel Report

## Problem
รายการบรรทัดต่างๆ ไม่ถูกคำนวณและแสดงผลในระดับ product (รายบริการ) ใน Excel
มีการแสดงผลเฉพาะในระดับ:
- กลุ่มธุรกิจ (BU totals)
- กลุ่มบริการ (SERVICE_GROUP)

แต่ไม่มีการคำนวณและแสดงผลในระดับ **รายบริการ (PRODUCT)**

รายการที่ไม่แสดงในระดับ product:
1. รายได้
2. ต้นทุนบริการและต้นทุนขาย
3. กำไร(ขาดทุน)ขั้นต้นจากการดำเนินงาน (1) - (2)
4. ค่าใช้จ่ายขายและการตลาด
5. กำไร(ขาดทุน)หลังหักค่าใช้จ่ายขายและการตลาด (3) - (4)
6. ค่าใช้จ่ายบริหารและสนับสนุน
7. ต้นทุนทางการเงิน-ด้านการดำเนินงาน
8. กำไร(ขาดทุน)ก่อนต้นทุนจัดหาเงิน รายได้อื่นและค่าใช้จ่ายอื่น (5) - (6) - (7)
9. ผลตอบแทนทางการเงินและรายได้อื่น
   - ผลตอบแทนทางการเงิน
   - รายได้อื่น
10. ค่าใช้จ่ายอื่น
11. ต้นทุนทางการเงิน-ด้านการจัดหาเงิน
12. กำไร(ขาดทุน)ก่อนหักภาษีเงินได้ (EBT) (8) + (9) - (10) - (11)
13. ภาษีเงินได้นิติบุคคล
14. กำไร(ขาดทุน) สุทธิ (12) - (13)

และรายการสรุปอื่นๆ:
- รายได้รวม
- ค่าใช้จ่ายรวม (ไม่รวมต้นทุนทางการเงิน)
- ค่าใช้จ่ายรวม (รวมต้นทุนทางการเงิน)
- EBITDA
- รายได้บริการ
- ต้นทุนบริการรวม
- สัดส่วนต่อรายได้
- ต้นทุนบริการ - ค่าเสื่อมราคาฯ
- ต้นทุนบริการ - ไม่รวมค่าใช้จ่ายบุคลากรและค่าเสื่อมราคาฯ

## Root Cause
ในไฟล์ `generate_report_with_products.py` บรรทัด 258-263:
```python
elif col_type == "PRODUCT":
    if group and not is_calculated_row(label):
        value = aggregator.get_value_by_product(group, sub_group, bu, sg, pk)
    else:
        # For calculated rows, product-level is not supported (use 0)
        value = 0  # ⬅️ ปัญหาตรงนี้!
```

สำหรับ **calculated rows** (บรรทัดที่คำนวณ) มันจะใส่ค่า **0** เสมอ แทนที่จะคำนวณจริง

## Solution

### 1. เพิ่มเมธอดใหม่ใน DataAggregator (`src/data_loader/data_aggregator.py`)

เพิ่มเมธอดใหม่ 3 ตัว:

#### 1.1 `calculate_product_value()`
คำนวณค่าในระดับ product สำหรับทุก calculated rows รวมถึง:
- รายได้รวม (sum_revenue)
- ค่าใช้จ่ายรวม (sum_expense_no_finance, sum_expense_with_finance)
- EBITDA
- รายได้บริการ (service_revenue)
- ต้นทุนบริการรวม (total_service_cost)
- สัดส่วนต่อรายได้ (ratios)
- ต้นทุนบริการ - ค่าเสื่อมราคาฯ
- ต้นทุนบริการ - ไม่รวมค่าใช้จ่ายบุคลากรและค่าเสื่อมราคาฯ

#### 1.2 `_sum_depreciation_by_product()`
รวมค่าเสื่อมราคาทั้งหมดในระดับ product

#### 1.3 `_sum_personnel_by_product()`
รวมค่าใช้จ่ายบุคลากรทั้งหมดในระดับ product

### 2. อัปเดต `generate_report_with_products.py`

แก้ไขการคำนวณค่าในระดับ product:

```python
elif col_type == "PRODUCT":
    # For product level, use the new calculate_product_value method
    value = aggregator.calculate_product_value(label, bu, sg, pk, all_row_data, current_main_group_label)
    # Store product-level values for calculated rows
    product_key_str = f"{bu}_{sg}_{pk}"
    if product_key_str not in all_row_data.get(label, {}):
        if label not in all_row_data:
            all_row_data[label] = {}
        all_row_data[label][product_key_str] = value
```

### 3. เพิ่ม context tracking
เพิ่มการ track `current_main_group_label` เพื่อให้ `get_group_sub_group()` ทำงานได้ถูกต้อง:

```python
# Track the current main group context
current_main_group_label = None

for level, label, is_calc, formula, is_bold in ROW_ORDER:
    # Update the main group context if this is a level 0 row
    if level == 0:
        current_main_group_label = label
    ...
```

## Files Modified

1. **src/data_loader/data_aggregator.py**
   - เพิ่มเมธอด `calculate_product_value()`
   - เพิ่มเมธอด `_sum_depreciation_by_product()`
   - เพิ่มเมธอด `_sum_personnel_by_product()`
   - อัปเดต signature ของ `calculate_summary_row()` (เพิ่ม optional parameters)

2. **generate_report_with_products.py**
   - แก้ไขการคำนวณค่าในระดับ product
   - เพิ่ม context tracking สำหรับ main group label
   - เก็บ product-level values ใน `all_row_data` สำหรับการคำนวณแบบ cascading

3. **generate_correct_report.py** ⭐
   - แก้ไขการคำนวณค่าในระดับ product (เหมือน #2)
   - ใช้ `calculate_product_value()` แทนการใส่ค่า 0
   - เก็บ product-level values ใน `all_row_data`

## Expected Results

หลังจากการแก้ไข Excel report จะแสดง:
- ✅ รายได้ในระดับ product
- ✅ ต้นทุนและค่าใช้จ่ายทั้งหมดในระดับ product
- ✅ กำไร/ขาดทุนทุกระดับในระดับ product
- ✅ รายได้รวม, ค่าใช้จ่ายรวม, EBITDA ในระดับ product
- ✅ ต้นทุนบริการและสัดส่วนต่อรายได้ในระดับ product
- ✅ ค่าต่างๆ ที่คำนวณจากต้นทุนบริการ (ไม่รวมค่าเสื่อมราคาฯ, ไม่รวมบุคลากร) ในระดับ product

## Testing

To test the fix:
```bash
cd /home/user/univer/report_generator
python3 generate_correct_report.py
```

หรือ

```bash
python3 generate_report_with_products.py
```

ตรวจสอบ Excel output ว่ามีการแสดงผลค่าในระดับ product ครบถ้วนหรือไม่

**Note**: ตอนแรกแก้ไขเฉพาะ `generate_report_with_products.py` แต่ต่อมาแก้ไข `generate_correct_report.py` เพิ่มเติมในคอมมิต `492aeb5` เพราะผู้ใช้รันไฟล์นี้จริงๆ

## Date
2025-11-25
