#!/usr/bin/env python3
"""
Apply fix for Row 13 (Tax) - only show in GRAND_TOTAL column
"""

print("""
=================================================================
MANUAL FIX REQUIRED: Row 13 - Tax Row
=================================================================

File: src/report_generator/writers/data_writer.py

Location: In function _write_data_cells(), after line:
    # Skip label column
    data_columns = [c for c in columns if c.col_type != 'label']

ADD THIS CODE:

    # CRITICAL FIX: Row 13 - only show in GRAND_TOTAL column
    is_tax_row = (label == "13.ภาษีเงินได้นิติบุคคล")

Then, in the loop:
    for idx, col in enumerate(data_columns):
        col_index = start_col + idx + 1  # +1 for label column
        
        # ADD THIS CHECK:
        # Skip non-grand-total columns for tax row
        if is_tax_row and col.col_type != 'grand_total':
            # Write empty cell with gray background
            cell = ws.cell(row=row_index + 1, column=col_index + 1)
            self.formatter.format_data_cell(
                cell,
                value=None,
                is_bold=row_def.is_bold,
                bg_color='A6A6A6',
                is_ratio=False
            )
            continue
        
        # Get value for this cell (existing code continues...)
        value = self._get_cell_value(...)

=================================================================
SUMMARY OF CHANGES:
=================================================================

1. ✅ row_builder.py - สีเทา A6A6A6 สำหรับบรรทัด 13 และ 14
2. ⏳ data_writer.py - บรรทัด 13 แสดงเฉพาะ GRAND_TOTAL (ต้องแก้ด้วยตนเอง)

หลังแก้แล้ว รันทดสอบ:
    python3 test_phase2c.py

ตรวจสอบ:
    - บรรทัด 13 มีค่าเฉพาะ column "รวมทั้งสิ้น"
    - บรรทัด 13 columns อื่นว่างเปล่า (สีเทา)
    - บรรทัด 14 สีเทา A6A6A6

=================================================================
""")
