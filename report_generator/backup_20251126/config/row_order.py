"""
Row order configuration for P&L Report
Defines the exact order and structure of rows in the report
"""

# Row structure with hierarchy
# Format: (level, label, is_calculated, calculation_formula, is_bold)

ROW_ORDER = [
    # Level 0 = Main sections, Level 1 = Sub-items, Level 2 = Sub-sub-items

    # 1. รายได้
    (0, "1.รายได้", False, None, True),
    (1, "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน", False, None, False),
    (1, "- รายได้กลุ่มธุรกิจโทรศัพท์ประจำที่และอินเตอร์เนตบรอดแบนด์", False, None, False),
    (1, "- รายได้กลุ่มธุรกิจโทรศัพท์เคลื่อนที่", False, None, False),
    (1, "- รายได้กลุ่มธุรกิจวงจรระหว่างประเทศ", False, None, False),
    (1, "- รายได้กลุ่มธุรกิจดิจิทัล", False, None, False),
    (1, "- รายได้กลุ่มธุรกิจ ICT Solution Business", False, None, False),
    (1, "- รายได้จากการให้บริการอื่นที่ไม่ใช่โทรคมนาคม", False, None, False),
    (1, "- รายได้จากการขาย", False, None, False),

    # 2. ต้นทุนบริการและต้นทุนขาย
    (0, "2.ต้นทุนบริการและต้นทุนขาย :", False, None, True),
    (1, "- ค่าใช้จ่ายตอบแทนแรงงาน", False, None, False),
    (1, "- ค่าสวัสดิการ", False, None, False),
    (1, "- ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร", False, None, False),
    (1, "- ค่าซ่อมแซมและบำรุงรักษาและวัสดุใช้ไป", False, None, False),
    (1, "- ค่าสาธารณูปโภค", False, None, False),
    (1, "- ค่าใช้จ่ายเกี่ยวกับการกำกับดูแลของ กสทช.", False, None, False),
    (1, "- ค่าส่วนแบ่งบริการโทรคมนาคม", False, None, False),
    (1, "- ค่าใช้จ่ายบริการโทรคมนาคม", False, None, False),
    (1, "- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์", False, None, False),
    (1, "- ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า", False, None, False),
    (1, "- ค่าเช่าและค่าใช้สินทรัพย์", False, None, False),
    (1, "- ต้นทุนขาย", False, None, False),
    (1, "- ค่าใช้จ่ายบริการอื่น", False, None, False),
    (1, "- ค่าใช้จ่ายดำเนินงานอื่น", False, None, False),

    # 3. กำไร(ขาดทุน)ขั้นต้นจากการดำเนินงาน
    (0, "3.กำไร(ขาดทุน)ขั้นต้นจากการดำเนินงาน (1) - (2)", True, "1 - 2", True),

    # 4. ค่าใช้จ่ายขายและการตลาด
    (0, "4.ค่าใช้จ่ายขายและการตลาด :", False, None, True),
    (1, "- ค่าใช้จ่ายตอบแทนแรงงาน", False, None, False),
    (1, "- ค่าสวัสดิการ", False, None, False),
    (1, "- ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร", False, None, False),
    (1, "- ค่าซ่อมแซมและบำรุงรักษาและวัสดุใช้ไป", False, None, False),
    (1, "- ค่าสาธารณูปโภค", False, None, False),
    (1, "- ค่าใช้จ่ายการตลาดและส่งเสริมการขาย", False, None, False),
    (1, "- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์", False, None, False),
    (1, "- ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า", False, None, False),
    (1, "- ค่าเช่าและค่าใช้สินทรัพย์", False, None, False),
    (1, "- ค่าใช้จ่ายดำเนินงานอื่น", False, None, False),

    # 5. กำไร(ขาดทุน)หลังหักค่าใช้จ่ายขายและการตลาด
    (0, "5.กำไร(ขาดทุน)หลังหักค่าใช้จ่ายขายและการตลาด (3) - (4)", True, "3 - 4", True),

    # 6. ค่าใช้จ่ายบริหารและสนับสนุน
    (0, "6.ค่าใช้จ่ายบริหารและสนับสนุน :", False, None, True),
    (1, "- ค่าใช้จ่ายตอบแทนแรงงาน", False, None, False),
    (1, "- ค่าสวัสดิการ", False, None, False),
    (1, "- ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร", False, None, False),
    (1, "- ค่าซ่อมแซมและบำรุงรักษาและวัสดุใช้ไป", False, None, False),
    (1, "- ค่าสาธารณูปโภค", False, None, False),
    (1, "- ค่าใช้จ่ายเผยแพร่ประชาสัมพันธ์", False, None, False),
    (1, "- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์", False, None, False),
    (1, "- ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า", False, None, False),
    (1, "- ค่าเช่าและค่าใช้สินทรัพย์", False, None, False),
    (1, "- ค่าใช้จ่ายบริการอื่น", False, None, False),
    (1, "- ค่าใช้จ่ายดำเนินงานอื่น", False, None, False),

    # 7. ต้นทุนทางการเงิน-ด้านการดำเนินงาน
    (0, "7.ต้นทุนทางการเงิน-ด้านการดำเนินงาน", False, None, True),

    # 8. กำไร(ขาดทุน)ก่อนต้นทุนจัดหาเงิน รายได้อื่นและค่าใช้จ่ายอื่น
    (0, "8.กำไร(ขาดทุน)ก่อนต้นทุนจัดหาเงิน รายได้อื่นและค่าใช้จ่ายอื่น (5) - (6) - (7)", True, "5 - 6 - 7", True),

    # 9. ผลตอบแทนทางการเงินและรายได้อื่น
    (0, "9.ผลตอบแทนทางการเงินและรายได้อื่น", False, None, True),
    (1, "     - ผลตอบแทนทางการเงิน", False, None, False),
    (1, "     - รายได้อื่น", False, None, False),

    # 10. ค่าใช้จ่ายอื่น
    (0, "10.ค่าใช้จ่ายอื่น", False, None, True),

    # 11. ต้นทุนทางการเงิน-ด้านการจัดหาเงิน
    (0, "11.ต้นทุนทางการเงิน-ด้านการจัดหาเงิน", False, None, True),

    # 12. กำไร(ขาดทุน)ก่อนหักภาษีเงินได้ (EBT)
    (0, "12.กำไร(ขาดทุน)ก่อนหักภาษีเงินได้ (EBT) (8) + (9) - (10) - (11)", True, "8 + 9 - 10 - 11", True),

    # 13. ภาษีเงินได้นิติบุคคล
    (0, "13.ภาษีเงินได้นิติบุคคล", False, None, True),

    # 14. กำไร(ขาดทุน) สุทธิ
    (0, "14.กำไร(ขาดทุน) สุทธิ (12) - (13)", True, "12 - 13", True),

    # Additional summary rows
    (0, "", False, None, False),  # Empty row
    (0, "รายได้รวม", True, "sum_revenue", True),
    (0, "ค่าใช้จ่ายรวม (ไม่รวมต้นทุนทางการเงิน)", True, "sum_expense_no_finance", True),
    (0, "ค่าใช้จ่ายรวม (รวมต้นทุนทางการเงิน)", True, "sum_expense_with_finance", True),
    (0, "EBITDA", True, "ebitda", True),

    # Cost to revenue ratio section
    (0, "", False, None, False),  # Empty row
    (0, "คำนวณสัดส่วนต้นทุนบริการต่อรายได้", False, None, True),
    (0, "รายได้บริการ", True, "service_revenue", True),
    (0, "ต้นทุนบริการ :", False, None, True),
    (1, "     1. ต้นทุนบริการรวม", True, "total_service_cost", False),
    (1, "         สัดส่วนต่อรายได้", True, "total_service_cost_ratio", False),
    (1, "     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ", True, "service_cost_no_depreciation", False),
    (1, "         สัดส่วนต่อรายได้", True, "service_cost_no_depreciation_ratio", False),
    (1, "     3. ต้นทุนบริการ - ไม่รวมค่าใช้จ่ายบุคลากรและค่าเสื่อมราคาฯ", True, "service_cost_no_personnel_depreciation", False),
    (1, "         สัดส่วนต่อรายได้", True, "service_cost_no_personnel_depreciation_ratio", False),
]


# Mapping of labels to row indices for calculation purposes
def get_row_index_map():
    """Get mapping of row labels to their indices"""
    row_map = {}
    for idx, (level, label, is_calc, formula, is_bold) in enumerate(ROW_ORDER):
        if label:
            row_map[label] = idx
    return row_map


# Categories that are part of depreciation
DEPRECIATION_CATEGORIES = [
    "- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์",
    "- ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า",
]

# Categories that are personnel costs
PERSONNEL_CATEGORIES = [
    "- ค่าใช้จ่ายตอบแทนแรงงาน",
    "- ค่าสวัสดิการ",
    "- ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร",
]
