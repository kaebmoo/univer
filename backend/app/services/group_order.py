"""
Business Group and Service Group Ordering
Define proper sorting order for groups based on business requirements
"""

# Business group ordering with their codes
BUSINESS_GROUP_ORDER = {
    '1 Hard Infrastructure': 1,
    '2 International': 2,
    '3 Mobile': 3,
    '4 Fixed Line & Broadband': 4,
    '5 Digital': 5,
    '6 ICT Solution': 6,
    '7 กลุ่มบริการอื่นไม่ใช่โทรคมนาคม': 7,
    '8 รายได้อื่น': 8,
}

# Service group ordering with their parent business group
SERVICE_GROUP_ORDER = {
    # 1. Hard Infrastructure
    '1.1 กลุ่มบริการท่อร้อยสาย': 11,
    '1.2 กลุ่มบริการ Dark Fiber': 12,
    '1.2 กลุ่มบริการ DARK FIBER': 12,  # Alternative name
    '1.3 กลุ่มบริการเสาโทรคมนาคม (Tower)': 13,
    '1.3 กลุ่มบริการเสาโทรคมนาคม (TOWER)': 13,  # Alternative name
    '1.4 กลุ่มบริการพัฒนาสินทรัพย์': 14,

    # 2. International
    '2.1 กลุ่มบริการ IIG (International Internet Gateway)': 21,
    '2.3 กลุ่มบริการ Connectivity': 23,
    '2.4 กลุ่มบริการเคเบิลใต้น้ำ': 24,
    '2.5 กลุ่มบริการ IDD': 25,

    # 3. Mobile
    '3.1 บริการโทรคมนาคมสื่อสารไร้สาย - กลุ่มค้าส่ง (Wholesale)': 31,
    '3.2 บริการโทรคมนาคมสื่อสารไร้สาย - กลุ่มค้าปลีก (Retail)': 32,
    '3.3 บริการ Trunk Radio': 33,
    '3.4 บริการเครื่องและอุปกรณ์ 2G, 3G, 4G & Shared Antenna': 34,
    '3.5 บริการ IoT Connectivity': 35,
    '3.6 บริการ 5G Solutions': 36,
    '3.7 บริการ CDMA ภูมิภาคและส่วนกลาง': 37,

    # 4. Fixed Line & Broadband
    '4.2 กลุ่มบริการ Internet Retail': 42,
    '4.3 กลุ่มบริการวงจรเช่า (Datacom)': 43,
    '4.4 บริการโทรศัพท์ประจำที่ (Fixed Line)': 44,
    '4.5 กลุ่มบริการ Satellite NT': 45,
    '4.5 กลุ่มบริการ Satellite ไทยคม': 45,  # Same order as NT
    '4.6 กลุ่มบริการ USO และอื่นๆ': 46,

    # 5. Digital
    '5.1 กลุ่มบริการ Cloud & BigData': 51,
    '5.2 กลุ่มบริการ Data Center & IX': 52,
    '5.3 กลุ่มบริการ Cybersecurity & CCTV': 53,
    '5.4 กลุ่มบริการ Application & Digital Services': 54,
    '5.5 กลุ่มบริการ DATA InterChange': 55,

    # 6. ICT Solution
    '6.1 กลุ่มบริการ Solution and Manage Service': 61,
    '6.2 กลุ่มบริการ Contact Center': 62,
    '6.3 กลุ่มบริการ ICT Solution & Platform': 63,

    # 7. Non-Telecom
    '7.1 กลุ่มบริการอื่น': 71,

    # 8. Other Income
    '8.1 ผลตอบแทนทางการเงิน': 81,
    '8.2 รายได้อื่น': 82,
}


def get_business_group_sort_key(business_group: str) -> int:
    """
    Get sort key for business group

    Args:
        business_group: Business group name

    Returns:
        Sort key (lower number = higher priority)
    """
    return BUSINESS_GROUP_ORDER.get(business_group, 999)


def get_service_group_sort_key(service_group: str) -> int:
    """
    Get sort key for service group

    Args:
        service_group: Service group name

    Returns:
        Sort key (lower number = higher priority)
    """
    return SERVICE_GROUP_ORDER.get(service_group, 999)


def sort_business_groups(groups: list) -> list:
    """
    Sort business groups in correct order

    Args:
        groups: List of business group names

    Returns:
        Sorted list
    """
    return sorted(groups, key=get_business_group_sort_key)


def sort_service_groups(groups: list) -> list:
    """
    Sort service groups in correct order

    Args:
        groups: List of service group names

    Returns:
        Sorted list
    """
    return sorted(groups, key=get_service_group_sort_key)
