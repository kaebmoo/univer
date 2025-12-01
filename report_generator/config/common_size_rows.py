"""
Common Size Row Configuration
กำหนดว่าบรรทัดไหนควรมี Common Size

Common Size จะคำนวณเฉพาะบรรทัดที่อยู่ในลิสต์นี้เท่านั้น
"""

# COSTTYPE: บรรทัดที่ควรมี Common Size
COMMON_SIZE_ROWS_COSTTYPE = {
    "รายได้รวม",
    "รายได้บริการ",
    "     1. ต้นทุนบริการรวม",
    "     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ",
    "     3. ต้นทุนบริการ - ไม่รวมค่าใช้จ่ายบุคลากรและค่าเสื่อมราคาฯ",
    "คำนวณสัดส่วนต้นทุนบริการต่อรายได้",
    "ค่าใช้จ่ายรวม (ไม่รวมต้นทุนทางการเงิน)",
    "ค่าใช้จ่ายรวม (รวมต้นทุนทางการเงิน)",
    "EBITDA",
}

# GLGROUP: บรรทัดที่ควรมี Common Size
COMMON_SIZE_ROWS_GLGROUP = {
    "1 รวมรายได้",
    "รายได้บริการ (1)-(9)",
    "     1. ต้นทุนบริการรวม",
    "     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ",
    "     3. ต้นทุนบริการ - ไม่รวมค่าใช้จ่ายบุคลากรและค่าเสื่อมราคาฯ",
    "คำนวณสัดส่วนต้นทุนบริการต่อรายได้",
    "2 รวมค่าใช้จ่าย",
    "2 รวมค่าใช้จ่าย (ไม่รวมต้นทุนทางการเงิน) (2)-(18)-(19)",
    "EBITDA",
}


def should_have_common_size(label: str, report_type: str) -> bool:
    """
    ตรวจสอบว่าบรรทัดนี้ควรมี Common Size หรือไม่
    
    Args:
        label: Row label
        report_type: "COSTTYPE" or "GLGROUP"
    
    Returns:
        True if should have common size
    """
    if report_type == "COSTTYPE":
        return label in COMMON_SIZE_ROWS_COSTTYPE
    elif report_type == "GLGROUP":
        return label in COMMON_SIZE_ROWS_GLGROUP
    else:
        return False
