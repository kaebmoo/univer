"""
Data Mapping Configuration
Maps row labels to CSV GROUP/SUB_GROUP structure
"""

# New context-aware mapping structure.
# This nested dictionary allows looking up sub-group IDs within the context of their parent main group.
CONTEXTUAL_MAPPING = {
    "1.รายได้": {
        "GROUP_ID": "01.รายได้",
        "SUB_GROUPS": {
            "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน": "01.รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน",
            "- รายได้กลุ่มธุรกิจโทรศัพท์ประจำที่และอินเตอร์เนตบรอดแบนด์": "02.รายได้กลุ่มธุรกิจโทรศัพท์ประจำที่และอินเตอร์เนตบรอดแบนด์",
            "- รายได้กลุ่มธุรกิจโทรศัพท์เคลื่อนที่": "03.รายได้กลุ่มธุรกิจโทรศัพท์เคลื่อนที่",
            "- รายได้กลุ่มธุรกิจวงจรระหว่างประเทศ": "04.รายได้กลุ่มธุรกิจวงจรระหว่างประเทศ",
            "- รายได้กลุ่มธุรกิจดิจิทัล": "05.รายได้กลุ่มธุรกิจดิจิทัล",
            "- รายได้กลุ่มธุรกิจ ICT Solution Business": "06.รายได้กลุ่มธุรกิจ ICT SOLUTION BUSINESS",
            "- รายได้จากการให้บริการอื่นที่ไม่ใช่โทรคมนาคม": "08.รายได้จากการให้บริการอื่นที่ไม่ใช่โทรคมนาคม",
            "- รายได้จากการขาย": "09.รายได้จากการขาย",
        }
    },
    "2.ต้นทุนบริการและต้นทุนขาย :": {
        "GROUP_ID": "02.ต้นทุนบริการและต้นทุนขาย :",
        "SUB_GROUPS": {
            "- ค่าใช้จ่ายตอบแทนแรงงาน": "01.ค่าใช้จ่ายตอบแทนแรงงาน",
            "- ค่าสวัสดิการ": "03.ค่าสวัสดิการ",
            "- ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร": "04.ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร",
            "- ค่าซ่อมแซมและบำรุงรักษาและวัสดุใช้ไป": "05.ค่าซ่อมแซมและบำรุงรักษาและวัสดุใช้ไป",
            "- ค่าสาธารณูปโภค": "06.ค่าสาธารณูปโภค",
            "- ค่าใช้จ่ายเกี่ยวกับการกำกับดูแลของ กสทช.": "09.ค่าใช้จ่ายเกี่ยวกับการกำกับดูแลของ กสทช.",
            "- ค่าส่วนแบ่งบริการโทรคมนาคม": "10.ค่าส่วนแบ่งบริการโทรคมนาคม",
            "- ค่าใช้จ่ายบริการโทรคมนาคม": "11.ค่าใช้จ่ายบริการโทรคมนาคม",
            "- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์": "12.ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์",
            "- ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า": "13.ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า",
            "- ค่าเช่าและค่าใช้สินทรัพย์": "14.ค่าเช่าและค่าใช้สินทรัพย์",
            "- ต้นทุนขาย": "15.ต้นทุนขาย",
            "- ค่าใช้จ่ายบริการอื่น": "16.ค่าใช้จ่ายบริการอื่น",
            "- ค่าใช้จ่ายดำเนินงานอื่น": "17.ค่าใช้จ่ายดำเนินงานอื่น",
        }
    },
    "3.กำไร(ขาดทุน)ขั้นต้นจากการดำเนินงาน (1) - (2)": {
        "GROUP_ID": "03.กำไร(ขาดทุน)ขั้นต้นจากการดำเนินงาน (1) - (2)",
        "SUB_GROUPS": {"3.กำไร(ขาดทุน)ขั้นต้นจากการดำเนินงาน (1) - (2)": "03.กำไร(ขาดทุน)ขั้นต้นจากการดำเนินงาน (1) - (2)"}
    },
    "4.ค่าใช้จ่ายขายและการตลาด :": {
        "GROUP_ID": "04.ค่าใช้จ่ายขายและการตลาด :",
        "SUB_GROUPS": {
            "- ค่าใช้จ่ายตอบแทนแรงงาน": "01.ค่าใช้จ่ายตอบแทนแรงงาน",
            "- ค่าสวัสดิการ": "03.ค่าสวัสดิการ",
            "- ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร": "04.ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร",
            "- ค่าซ่อมแซมและบำรุงรักษาและวัสดุใช้ไป": "05.ค่าซ่อมแซมและบำรุงรักษาและวัสดุใช้ไป",
            "- ค่าสาธารณูปโภค": "06.ค่าสาธารณูปโภค",
            "- ค่าใช้จ่ายการตลาดและส่งเสริมการขาย": "07.ค่าใช้จ่ายการตลาดและส่งเสริมการขาย",
            "- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์": "12.ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์",
            "- ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า": "13.ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า",
            "- ค่าเช่าและค่าใช้สินทรัพย์": "14.ค่าเช่าและค่าใช้สินทรัพย์",
            "- ค่าใช้จ่ายดำเนินงานอื่น": "17.ค่าใช้จ่ายดำเนินงานอื่น",
        }
    },
    "5.กำไร(ขาดทุน)หลังหักค่าใช้จ่ายขายและการตลาด (3) - (4)": {
        "GROUP_ID": "05.กำไร(ขาดทุน)หลังหักค่าใช้จ่ายขายและการตลาด (3) - (4)",
        "SUB_GROUPS": {"5.กำไร(ขาดทุน)หลังหักค่าใช้จ่ายขายและการตลาด (3) - (4)": "05.กำไร(ขาดทุน)หลังหักค่าใช้จ่ายขายและการตลาด (3) - (4)"}
    },
    "6.ค่าใช้จ่ายบริหารและสนับสนุน :": {
        "GROUP_ID": "06.ค่าใช้จ่ายบริหารและสนับสนุน :",
        "SUB_GROUPS": {
            "- ค่าใช้จ่ายตอบแทนแรงงาน": "01.ค่าใช้จ่ายตอบแทนแรงงาน",
            "- ค่าสวัสดิการ": "03.ค่าสวัสดิการ",
            "- ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร": "04.ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร",
            "- ค่าซ่อมแซมและบำรุงรักษาและวัสดุใช้ไป": "05.ค่าซ่อมแซมและบำรุงรักษาและวัสดุใช้ไป",
            "- ค่าสาธารณูปโภค": "06.ค่าสาธารณูปโภค",
            "- ค่าใช้จ่ายเผยแพร่ประชาสัมพันธ์": "08.ค่าใช้จ่ายเผยแพร่ประชาสัมพันธ์",
            "- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์": "12.ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์",
            "- ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า": "13.ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า",
            "- ค่าเช่าและค่าใช้สินทรัพย์": "14.ค่าเช่าและค่าใช้สินทรัพย์",
            "- ค่าใช้จ่ายบริการอื่น": "16.ค่าใช้จ่ายบริการอื่น",
            "- ค่าใช้จ่ายดำเนินงานอื่น": "17.ค่าใช้จ่ายดำเนินงานอื่น",
        }
    },
    "7.ต้นทุนทางการเงิน-ด้านการดำเนินงาน": {
        "GROUP_ID": "07.ต้นทุนทางการเงิน-ด้านการดำเนินงาน",
        "SUB_GROUPS": {} # Direct mapping, no sub-groups
    },
    "8.กำไร(ขาดทุน)ก่อนต้นทุนจัดหาเงิน รายได้อื่นและค่าใช้จ่ายอื่น (5) - (6) - (7)": {
        "GROUP_ID": "08.กำไร(ขาดทุน)ก่อนต้นทุนจัดหาเงิน รายได้อื่นและค่าใช้จ่ายอื่น (5) - (6) - (7)",
        "SUB_GROUPS": {}
    },
    "9.ผลตอบแทนทางการเงินและรายได้อื่น": {
        "GROUP_ID": "09.ผลตอบแทนทางการเงินและรายได้อื่น",
        "SUB_GROUPS": {
            "     - ผลตอบแทนทางการเงิน": "09.ผลตอบแทนทางการเงิน",
            "     - รายได้อื่น": "09.รายได้อื่น",
        }
    },
    "10.ค่าใช้จ่ายอื่น": {
        "GROUP_ID": "10.ค่าใช้จ่ายอื่น", "SUB_GROUPS": {}
    },
    "11.ต้นทุนทางการเงิน-ด้านการจัดหาเงิน": {
        "GROUP_ID": "11.ต้นทุนทางการเงิน-ด้านการจัดหาเงิน", "SUB_GROUPS": {}
    },
    "12.กำไร(ขาดทุน)ก่อนหักภาษีเงินได้ (EBT) (8) + (9) - (10) - (11)": {
        "GROUP_ID": "12.กำไร(ขาดทุน)ก่อนหักภาษีเงินได้ (EBT) (8) + (9) - (10) - (11)", "SUB_GROUPS": {}
    },
    "13.ภาษีเงินได้นิติบุคคล": {
        "GROUP_ID": "13.ภาษีเงินได้นิติบุคคล", "SUB_GROUPS": {}
    },
    "14.กำไร(ขาดทุน) สุทธิ (12) - (13)": {
        "GROUP_ID": "14.กำไร(ขาดทุน) สุทธิ (12) - (13)", "SUB_GROUPS": {}
    },
}

# Rows that need to be calculated (not in CSV)
CALCULATED_ROWS = {
    # Main profit/loss calculations
    "3.กำไร(ขาดทุน)ขั้นต้นจากการดำเนินงาน (1) - (2)": "gross_profit",  # 1 - 2
    "5.กำไร(ขาดทุน)หลังหักค่าใช้จ่ายขายและการตลาด (3) - (4)": "profit_after_selling",  # 3 - 4
    "8.กำไร(ขาดทุน)ก่อนต้นทุนจัดหาเงิน รายได้อื่นและค่าใช้จ่ายอื่น (5) - (6) - (7)": "profit_before_finance",  # 5 - 6 - 7
    "12.กำไร(ขาดทุน)ก่อนหักภาษีเงินได้ (EBT) (8) + (9) - (10) - (11)": "ebt",  # 8 + 9 - 10 - 11
    "14.กำไร(ขาดทุน) สุทธิ (12) - (13)": "net_profit",  # 12 - 13

    # Summary rows
    "รายได้รวม": "sum_revenue",  # Sum of all revenue (GROUP = 01)
    "ค่าใช้จ่ายรวม (ไม่รวมต้นทุนทางการเงิน)": "sum_expense_no_finance",  # Sum of 02, 04, 06
    "ค่าใช้จ่ายรวม (รวมต้นทุนทางการเงิน)": "sum_expense_with_finance",  # Sum of 02, 04, 06, 07, 11
    "EBITDA": "ebitda",  # EBIT + depreciation + amortization

    # Service cost analysis
    "รายได้บริการ": "service_revenue",  # Revenue excluding other income
    "     1. ต้นทุนบริการรวม": "total_service_cost",  # GROUP = 02 total
    "     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ": "service_cost_no_depreciation",
    "     3. ต้นทุนบริการ - ไม่รวมค่าใช้จ่ายบุคลากรและค่าเสื่อมราคาฯ": "service_cost_no_personnel_depreciation",

    # Ratios
    "         สัดส่วนต่อรายได้": "ratio_to_revenue",  # Context-dependent ratio
}

# Special handling for ratio rows that have context-dependent calculation
RATIO_ROW_LABEL = "         สัดส่วนต่อรายได้"

# Categories for depreciation (used in EBITDA calculation)
DEPRECIATION_CATEGORIES = [
    "12.ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์",
    "13.ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า",
]

# Categories for personnel costs
PERSONNEL_CATEGORIES = [
    "01.ค่าใช้จ่ายตอบแทนแรงงาน",
    "03.ค่าสวัสดิการ",
    "04.ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร",
]


def get_group_sub_group(row_label: str, main_group_label: str = None) -> tuple:
    """
    Get GROUP and SUB_GROUP for a row label using context from the main group.

    Args:
        row_label: The label of the current row being processed.
        main_group_label: The label of the parent (level 0) group.

    Returns:
        Tuple of (GROUP_ID, SUB_GROUP_ID) or (None, None) if not found.
    """
    if row_label in CALCULATED_ROWS:
        return (None, None)

    # Case 1: The row is a main group itself (or has no parent context).
    if not main_group_label or row_label == main_group_label:
        mapping = CONTEXTUAL_MAPPING.get(row_label)
        if mapping:
            # Main groups map to a GROUP_ID but have no SUB_GROUP in this context.
            return (mapping["GROUP_ID"], None)
        return (None, None)

    # Case 2: The row is a sub-item. Look for it within its main group's context.
    main_group_mapping = CONTEXTUAL_MAPPING.get(main_group_label)
    if main_group_mapping:
        group_id = main_group_mapping["GROUP_ID"]
        sub_group_id = main_group_mapping["SUB_GROUPS"].get(row_label)
        if sub_group_id:
            return (group_id, sub_group_id)

    # Fallback for rows that might not be in the nested structure but have a direct mapping
    # (e.g., rows 7, 10, 11, etc. which have no sub-items).
    direct_mapping = CONTEXTUAL_MAPPING.get(row_label)
    if direct_mapping:
        return (direct_mapping["GROUP_ID"], direct_mapping["SUB_GROUPS"].get(row_label))


    return (None, None) # Fallback if no mapping is found


def is_calculated_row(row_label: str) -> bool:
    """Check if row needs to be calculated (not in CSV)"""
    return row_label in CALCULATED_ROWS


def get_calculation_type(row_label: str) -> str:
    """Get calculation type for calculated rows"""
    return CALCULATED_ROWS.get(row_label, None)
