# Fix for Row 13 and 14

## Issue:
1. บรรทัด "13.ภาษีเงินได้นิติบุคคล" ต้องมีค่าเฉพาะ column "รวมทั้งสิ้น" เท่านั้น
2. บรรทัด 13 และ 14 ต้องมีสีพื้นหลังเป็นเทา A6A6A6

## Solution:

### 1. แก้ data_writer.py

ในฟังก์ชัน `_write_data_cells`:

```python
# เพิ่มตรงนี้หลังบรรทัด label check
# Special case: Row 13 - only show in GRAND_TOTAL column
is_tax_row = (label == "13.ภาษีเงินได้นิติบุคคล")

for idx, col in enumerate(data_columns):
    col_index = start_col + idx + 1
    
    # Skip non-grand-total columns for tax row
    if is_tax_row and col.col_type != 'grand_total':
        # Write empty cell with gray background
        cell = ws.cell(row=row_index + 1, column=col_index + 1)
        self.formatter.format_data_cell(
            cell,
            value=None,
            is_bold=row_def.is_bold,
            bg_color='A6A6A6',  # Gray background
            is_ratio=False
        )
        continue
    
    # Get value...
    value = self._get_cell_value(...)
```

### 2. แก้ row_builder.py

ในฟังก์ชัน `_create_row_def`:

```python
# เพิ่ม check สำหรับบรรทัด 13 และ 14
if label in ["13.ภาษีเงินได้นิติบุคคล", "14.กำไร(ขาดทุน) สุทธิ (12) - (13)"]:
    bg_color = 'A6A6A6'  # Gray
else:
    bg_color = self._get_row_color(label, level)
```

### 3. ทดสอบ

```bash
python3 test_phase2c.py
```

ตรวจสอบ:
- [ ] บรรทัด 13 มีค่าเฉพาะ column "รวมทั้งสิ้น"
- [ ] บรรทัด 13 columns อื่นว่างเปล่า (มีสีเทา)
- [ ] บรรทัด 13 และ 14 สีเทา A6A6A6
