# Fix for Tax and Net Profit Rows - Gray BG for non-grand-total columns

## Location: src/report_generator/writers/data_writer.py

## In function _write_data_cells():

### Find this section (around line 170-180):

```python
# CRITICAL: Row 13 - only show in GRAND_TOTAL column
is_tax_row = (label == "13.ภาษีเงินได้นิติบุคคล")

for idx, col in enumerate(data_columns):
    col_index = start_col + idx + 1
    
    # Skip non-grand-total columns for tax row
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
```

### Change to:

```python
# CRITICAL: Tax and Net Profit rows - special handling
# COSTTYPE: "13.ภาษีเงินได้นิติบุคคล", "14.กำไร(ขาดทุน) สุทธิ (12) - (13)"
# GLGROUP: "4.ภาษีเงินได้นิติบุคคล", "5.กำไร(ขาดทุน) สุทธิ (3)-(4)"
is_tax_row = ("ภาษีเงินได้นิติบุคคล" in label)
is_net_profit_row = ("กำไร(ขาดทุน) สุทธิ" in label and "(" in label)

for idx, col in enumerate(data_columns):
    col_index = start_col + idx + 1
    
    # Tax row: only show in GRAND_TOTAL, gray for others
    if is_tax_row and col.col_type != 'grand_total':
        cell = ws.cell(row=row_index + 1, column=col_index + 1)
        self.formatter.format_data_cell(
            cell,
            value=None,
            is_bold=row_def.is_bold,
            bg_color='A6A6A6',  # Gray
            is_ratio=False
        )
        continue
    
    # Net Profit row: gray for non-grand-total columns
    if is_net_profit_row and col.col_type != 'grand_total':
        # Get value normally but use gray background
        value = self._get_cell_value(
            col,
            row_data,
            label,
            is_ratio_row,
            aggregator,
            all_row_data,
            current_main_group_label,
            previous_label
        )
        
        cell = ws.cell(row=row_index + 1, column=col_index + 1)
        self.formatter.format_data_cell(
            cell,
            value=value,
            is_bold=row_def.is_bold,
            bg_color='A6A6A6',  # Gray for non-grand-total
            is_ratio=is_ratio_row
        )
        continue
    
    # Normal cell handling continues...
```

## Summary:
- Tax row: Value only in GRAND_TOTAL, gray empty cells for others
- Net Profit row: Calculated values in all columns, but gray BG for non-grand-total
- Both rows: Label cell remains F8CBAD (from row_def.color)
