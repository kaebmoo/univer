"""
Row order configuration for P&L Report - GLGROUP (หมวดบัญชี)
Defines the exact order and structure of rows for GL Group dimension

Key differences from COSTTYPE:
- Grouped by GL Group and Sub Group
- Different summary calculations
- Simpler structure (no sub-sections like cost/selling/admin)
"""

# Row structure with hierarchy
# Format: (level, label, is_calculated, calculation_formula, is_bold)

ROW_ORDER_GLGROUP = [
    # 1. รวมรายได้
    (0, "1 รวมรายได้", True, "sum_group_1", True),
    (1, "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน", False, None, False),
    (1, "- รายได้กลุ่มธุรกิจโทรศัพท์ประจำที่และบรอดแบนด์", False, None, False),
    (1, "- รายได้กลุ่มธุรกิจโทรศัพท์เคลื่อนที่", False, None, False),
    (1, "- รายได้กลุ่มธุรกิจวงจรระหว่างประเทศ", False, None, False),
    (1, "- รายได้กลุ่มธุรกิจดิจิทัล", False, None, False),
    (1, "- รายได้กลุ่มธุรกิจ ICT Solution Business", False, None, False),
    (1, "- รายได้จากการให้บริการอื่นที่ไม่ใช่โทรคมนาคม", False, None, False),
    (1, "- รายได้จากการขาย", False, None, False),
    
    # รวมรายได้จากการให้บริการ
    (0, "รวมรายได้จากการให้บริการ", True, "sum_service_revenue", True),
    
    # ผลตอบแทนทางการเงินและรายได้อื่น
    (1, "- ผลตอบแทนทางการเงินและรายได้อื่น", False, None, False),
    (2, "     - ผลตอบแทนทางการเงิน", False, None, False),
    (2, "     - รายได้อื่น", False, None, False),
    
    # 2. รวมค่าใช้จ่าย
    (0, "2 รวมค่าใช้จ่าย", True, "sum_group_2", True),
    (1, "- ค่าใช้จ่ายตอบแทนแรงงาน", False, None, False),
    (1, "- ค่าสวัสดิการ", False, None, False),
    (1, "- ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร", False, None, False),
    (1, "- ค่าซ่อมแซมและบำรุงรักษาและวัสดุใช้ไป", False, None, False),
    (1, "- ค่าสาธารณูปโภค", False, None, False),
    (1, "- ค่าใช้จ่ายการตลาดและส่งเสริมการขาย", False, None, False),
    (1, "- ค่าใช้จ่ายเผยแพร่ประชาสัมพันธ์", False, None, False),
    (1, "- ค่าใช้จ่ายเกี่ยวกับการกำกับดูแลของ กสทช.", False, None, False),
    (1, "- ค่าส่วนแบ่งบริการโทรคมนาคม", False, None, False),
    (1, "- ค่าใช้จ่ายบริการโทรคมนาคม", False, None, False),
    (1, "- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์", False, None, False),
    (1, "- ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า", False, None, False),
    (1, "- ค่าเช่าและค่าใช้สินทรัพย์", False, None, False),
    (1, "- ต้นทุนขาย", False, None, False),
    (1, "- ค่าใช้จ่ายบริการอื่น", False, None, False),
    (1, "- ค่าใช้จ่ายดำเนินงานอื่น", False, None, False),
    (1, "- ค่าใช้จ่ายอื่น", False, None, False),
    (1, "- ต้นทุนทางการเงิน-ด้านการดำเนินงาน", False, None, False),
    (1, "- ต้นทุนทางการเงิน-ด้านการจัดหาเงิน", False, None, False),
    
    # 3. EBT
    (0, "3.กำไร(ขาดทุน)ก่อนหักภาษีเงินได้ (EBT) (1)-(2)", False, None, True),
    
    # 4. Tax
    (0, "4.ภาษีเงินได้นิติบุคคล", False, None, True),
    
    # 5. Net profit
    (0, "5.กำไร(ขาดทุน) สุทธิ (3)-(4)", False, None, True),
    
    # Empty row
    (0, "", False, None, False),
    
    # Summary rows
    (0, "รายได้รวม", True, "total_revenue", True),
    (0, "ค่าใช้จ่ายรวม (ไม่รวมต้นทุนทางการเงิน)", True, "total_expense_no_finance", True),
    (0, "ค่าใช้จ่ายรวม (รวมต้นทุนทางการเงิน)", True, "total_expense_with_finance", True),
    (0, "EBITDA", True, "ebitda", True),
]


def get_row_index_map_glgroup():
    """Get mapping of row labels to their indices for GLGROUP"""
    row_map = {}
    for idx, (level, label, is_calc, formula, is_bold) in enumerate(ROW_ORDER_GLGROUP):
        if label:
            row_map[label] = idx
    return row_map


# GL Group categories for depreciation (same as COSTTYPE)
DEPRECIATION_CATEGORIES_GLGROUP = [
    "- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์",
    "- ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า",
]

# GL Group categories for personnel (same as COSTTYPE)
PERSONNEL_CATEGORIES_GLGROUP = [
    "- ค่าใช้จ่ายตอบแทนแรงงาน",
    "- ค่าสวัสดิการ",
    "- ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร",
]

# Finance cost categories
FINANCE_CATEGORIES_GLGROUP = [
    "- ต้นทุนทางการเงิน-ด้านการดำเนินงาน",
    "- ต้นทุนทางการเงิน-ด้านการจัดหาเงิน",
]
