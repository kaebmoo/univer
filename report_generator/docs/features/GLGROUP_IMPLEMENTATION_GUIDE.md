# GLGROUP Implementation - COMPLETE GUIDE

## 📋 Overview
GLGROUP (หมวดบัญชี) reports มีโครงสร้างต่างจาก COSTTYPE:
- ใช้ GROUP/SUB_GROUP แทน MAIN_GROUP/SUB_GROUP
- บรรทัดที่ 3,4,5 ไม่คำนวณ (มีในข้อมูล)
- GROUP 04 (ภาษี) อาจไม่มีในบางงวด

---

## ✅ สิ่งที่ทำเสร็จแล้ว (100%):

### 1. Configuration Files
- ✅ `config/row_order_glgroup.py` - Row structure (3,4,5 = False)
- ✅ `config/data_mapping_glgroup.py` - GROUP/SUB_GROUP mapping

### 2. Core Modules
- ✅ `src/report_generator/rows/row_builder.py` - Auto-select ROW_ORDER

### 3. Testing Scripts
- ✅ `check_glgroup_data.py` - Data structure checker
- ✅ `check_ytd_tax.py` - Tax data checker
- ✅ `test_glgroup_loading.py` - Loading test

---

## ⏳ สิ่งที่ต้องทำต่อ:

### CRITICAL - Data Handling:

#### 1. สร้าง `get_row_data_glgroup()` ใน DataAggregator
Location: `src/data_loader.py`

```python
def get_row_data_glgroup(
    self,
    label: str,
    bu_list: List[str],
    service_group_dict: Dict[str, List[str]]
) -> Dict[str, float]:
    """
    Get row data for GLGROUP dimension
    Uses GROUP/SUB_GROUP instead of MAIN_GROUP/SUB_GROUP
    """
    from config.data_mapping_glgroup import get_group_sub_group_glgroup
    
    # Get mapping
    group, sub_group = get_group_sub_group_glgroup(label)
    
    if not group:
        return {}  # No mapping
    
    # Filter data
    filtered = self.df[
        (self.df['GROUP'] == group) & 
        (self.df['SUB_GROUP'] == sub_group)
    ]
    
    if len(filtered) == 0:
        # No data (e.g., Tax in MTH) → return empty dict
        return {}
    
    # Build result dict
    result = {}
    
    # Grand total
    result['grand_total'] = filtered['VALUE'].sum()
    
    # By BU
    for bu in bu_list:
        bu_data = filtered[filtered['BU'] == bu]
        result[f'bu_total_{bu}'] = bu_data['VALUE'].sum()
        
        # By SG
        if bu in service_group_dict:
            for sg in service_group_dict[bu]:
                sg_data = bu_data[bu_data['SERVICE_GROUP'] == sg]
                result[f'sg_total_{bu}_{sg}'] = sg_data['VALUE'].sum()
                
                # By Product
                for _, row in sg_data.iterrows():
                    product_key = row['PRODUCT_KEY']
                    result[f'product_{bu}_{sg}_{product_key}'] = row['VALUE']
    
    return result
```

#### 2. สร้าง `calculate_summary_row_glgroup()` ใน DataAggregator

```python
def calculate_summary_row_glgroup(
    self,
    label: str,
    bu_list: List[str],
    service_group_dict: Dict[str, List[str]],
    all_row_data: Dict[str, Dict]
) -> Dict[str, float]:
    """
    Calculate summary rows for GLGROUP
    Handles special formulas like:
    - "1 รวมรายได้" = sum of all revenue items
    - "2 รวมค่าใช้จ่าย" = sum of all expense items
    - "รายได้รวม" = total revenue
    - "EBITDA" = special calculation
    """
    from config.row_order_glgroup import ROW_ORDER_GLGROUP
    
    # Find formula
    formula = None
    for level, row_label, is_calc, calc_formula, is_bold in ROW_ORDER_GLGROUP:
        if row_label == label and is_calc:
            formula = calc_formula
            break
    
    if not formula:
        return {}
    
    # Execute formula
    if formula == "sum_group_1":
        # Sum all revenue items under "1 รวมรายได้"
        return self._sum_group_items(all_row_data, "1 รวมรายได้")
    
    elif formula == "sum_group_2":
        # Sum all expense items under "2 รวมค่าใช้จ่าย"
        return self._sum_group_items(all_row_data, "2 รวมค่าใช้จ่าย")
    
    elif formula == "sum_service_revenue":
        # Sum of revenue items + finance income
        return self._sum_service_revenue(all_row_data)
    
    elif formula == "total_revenue":
        # All revenue (from GROUP 01)
        return all_row_data.get("1 รวมรายได้", {})
    
    elif formula == "ebitda":
        # EBITDA calculation
        return self._calculate_ebitda_glgroup(all_row_data)
    
    # ... other formulas
    
    return {}
```

#### 3. แก้ `data_writer.py` - Call correct methods

Location: `src/report_generator/writers/data_writer.py`

ใน method `write()`:

```python
# Get row data
if self.config.report_type.value == "GLGROUP":
    # Use GLGROUP methods
    if is_ratio_row:
        row_data = aggregator._calculate_ratio_by_type(...)
    elif is_calculated_row(label):
        row_data = aggregator.calculate_summary_row_glgroup(
            label, bu_list, service_group_dict, all_row_data
        )
    else:
        row_data = aggregator.get_row_data_glgroup(
            label, bu_list, service_group_dict
        )
else:
    # Use COSTTYPE methods (existing)
    if is_ratio_row:
        row_data = aggregator._calculate_ratio_by_type(...)
    elif is_calculated_row(label):
        row_data = aggregator.calculate_summary_row(...)
    else:
        row_data = aggregator.get_row_data(...)
```

#### 4. แก้ Tax & Net Profit Gray Background

ใน method `_write_data_cells()`:

```python
# Tax and Net Profit - special handling
is_tax_row = ("ภาษีเงินได้นิติบุคคล" in label)
is_net_profit_row = ("กำไร(ขาดทุน) สุทธิ" in label and "(" in label)

for idx, col in enumerate(data_columns):
    col_index = start_col + idx + 1
    
    # Tax row: only in GRAND_TOTAL, gray for others
    if is_tax_row and col.col_type != 'grand_total':
        cell = ws.cell(row=row_index + 1, column=col_index + 1)
        self.formatter.format_data_cell(
            cell,
            value=None,
            is_bold=row_def.is_bold,
            bg_color='A6A6A6',
            is_ratio=False
        )
        continue
    
    # Net Profit row: calculate but gray BG for non-grand-total
    if is_net_profit_row and col.col_type != 'grand_total':
        value = self._get_cell_value(...)  # Get value normally
        cell = ws.cell(row=row_index + 1, column=col_index + 1)
        self.formatter.format_data_cell(
            cell,
            value=value,
            is_bold=row_def.is_bold,
            bg_color='A6A6A6',  # Gray!
            is_ratio=is_ratio_row
        )
        continue
    
    # Normal handling...
```

---

## 🧪 Testing Plan:

### 1. Test Data Loading
```bash
python3 test_glgroup_loading.py
```
Expected: ✅ Load data, mapping works

### 2. Test MTH Report
```bash
python3 test_glgroup.py
```
Expected:
- ✅ Generate 3 reports (BU_ONLY, BU_SG, BU_SG_PRODUCT)
- ✅ Row 4 (Tax) = empty cells (no data)
- ✅ Row 4 columns gray except GRAND_TOTAL
- ✅ Row 5 (Net Profit) = calculated, gray non-grand-total

### 3. Test YTD Report
```bash
python3 test_ytd_reports.py
```
Expected:
- ✅ Row 4 (Tax) = has value in GRAND_TOTAL only
- ✅ Gray backgrounds correct

---

## 📊 Data Structure Reference:

### Columns:
```
TIME_KEY, GROUP, SUB_GROUP, BU, SERVICE_GROUP, 
PRODUCT_NAME, PRODUCT_KEY, ALLIE, VALUE
```

### GROUPs:
- **01.รายได้** - Revenue items
- **02.ค่าใช้จ่าย** - Expense items
- **03.กำไร(ขาดทุน)ก่อนหักภาษีเงินได้ (EBT) (1)-(2)** - EBT
- **04.ภาษีเงินได้นิติบุคคล** - Tax (may not exist in MTH)
- **05.กำไร(ขาดทุน) สุทธิ (3)-(4)** - Net Profit

### SUB_GROUPs Examples:
- `01.รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน`
- `02.ค่าใช้จ่ายตอบแทนแรงงาน`
- `03.กำไร(ขาดทุน)ก่อนหักภาษีเงินได้ (EBT) (1)-(2)`
- `04.ภาษีเงินได้นิติบุคคล`
- `05.กำไร(ขาดทุน) สุทธิ (3)-(4)`

---

## 💡 Special Cases:

### 1. Missing Tax Data (MTH)
- GROUP 04 doesn't exist
- Solution: Return empty dict → empty cells
- Gray background for non-grand-total columns

### 2. Tax Data Exists (YTD)
- GROUP 04 has 1 row
- Only populate GRAND_TOTAL column
- All other columns: gray empty cells

### 3. Calculated Rows
- Row 3 (EBT): From data, not calculated
- Row 4 (Tax): From data, not calculated
- Row 5 (Net Profit): From data, not calculated
- Row "1 รวมรายได้": Sum of revenue items
- Row "2 รวมค่าใช้จ่าย": Sum of expense items
- Row "EBITDA": Special formula

---

## 📁 Files Summary:

### Created:
- config/row_order_glgroup.py
- config/data_mapping_glgroup.py
- check_glgroup_data.py
- check_ytd_tax.py
- test_glgroup_loading.py

### Modified:
- src/report_generator/rows/row_builder.py

### Need to Modify:
- src/data_loader.py (DataAggregator)
- src/report_generator/writers/data_writer.py

---

## 🎯 Success Criteria:

✅ GLGROUP reports generate without errors
✅ Row structure matches specification
✅ Tax row (4) handles missing data gracefully
✅ Gray backgrounds correct for rows 4 & 5
✅ Data accuracy matches source files
✅ All 3 detail levels work (BU_ONLY, BU_SG, FULL)

---

**Next: Implement DataAggregator GLGROUP methods!**
