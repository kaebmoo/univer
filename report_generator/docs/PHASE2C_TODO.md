# Phase 2C - TODO List

## สิ่งที่ทำเสร็จแล้ว:
✅ BUOnlyBuilder - สร้างแล้ว
✅ BUSGBuilder - สร้างแล้ว  
✅ report_builder.py - อัพเดทแล้ว
✅ __init__.py - อัพเดทแล้ว
✅ test_phase2c.py - สร้างแล้ว

## สิ่งที่ต้องทำต่อ:

### 1. column_header_writer.py
ต้องเพิ่ม handling สำหรับ col_type == 'sg' (BU+SG builder)

ในฟังก์ชัน write():
```python
elif col.col_type == 'sg':
    # Write SG column (BU+SG builder, merged rows 2-4)
    self._write_sg_column(ws, col, col_index, start_row)
```

ใน _group_columns_by_bu():
```python
elif col.col_type == 'sg':
    # Handle SG columns for BU+SG builder
    # Similar to sg_total but simpler
```

สร้างฟังก์ชัน _write_sg_column():
```python
def _write_sg_column(self, ws, col: ColumnDef, col_index: int, start_row: int):
    """Write SG column for BU+SG builder (merged rows 2-4)"""
    cell = ws.cell(row=start_row + 2, column=col_index + 1)
    cell.value = col.name
    cell.font = self.formatter.create_font(bold=True)
    cell.fill = self.formatter.create_fill(col.color)
    cell.alignment = self.formatter.create_alignment(
        horizontal='center',
        vertical='center',
        wrap_text=True
    )
    cell.border = self.formatter.create_border()
    
    # Merge rows 2-4
    ws.merge_cells(
        start_row=start_row + 2,
        start_column=col_index + 1,
        end_row=start_row + 4,
        end_column=col_index + 1
    )
```

### 2. data_writer.py  
ต้องเพิ่ม handling สำหรับ col_type == 'sg'

ในฟังก์ชัน _get_cell_value():
```python
elif col_type == 'sg':
    # For BU+SG builder - SG column (same as sg_total)
    return row_data.get(f'{col.bu}_{col.service_group}', 0)
```

## วิธีทดสอบ:

```bash
python3 test_phase2c.py
```

คาดว่าจะ error ที่:
1. column_header_writer ไม่รู้จัก 'sg' type
2. data_writer ไม่รู้จัก 'sg' type

แก้ไขตาม TODO ด้านบน แล้วทดสอบใหม่
