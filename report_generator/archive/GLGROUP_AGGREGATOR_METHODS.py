"""
GLGROUP Methods for DataAggregator
Add these methods to src/data_loader/data_aggregator.py
"""

# ADD TO DataAggregator class:

def get_row_data_glgroup(
    self,
    label: str,
    bu_list: List[str],
    service_group_dict: Dict[str, List[str]]
) -> Dict[str, float]:
    """
    Get row data for GLGROUP dimension
    Uses GROUP/SUB_GROUP from data directly
    
    Args:
        label: Row label from ROW_ORDER_GLGROUP
        bu_list: List of business units
        service_group_dict: Dict of {BU: [service_groups]}
    
    Returns:
        Dict with aggregated values by column type
    """
    from config.data_mapping_glgroup import get_group_sub_group_glgroup
    
    # Get mapping
    group, sub_group = get_group_sub_group_glgroup(label)
    
    if not group:
        return {}  # No mapping
    
    # Filter data by GROUP and SUB_GROUP
    filtered = self.df[
        (self.df['GROUP'] == group) & 
        (self.df['SUB_GROUP'] == sub_group)
    ]
    
    if len(filtered) == 0:
        # No data (e.g., Tax in MTH) → return empty dict
        logger.info(f"No data for GLGROUP: {group} / {sub_group}")
        return {}
    
    # Build result dict
    result = {}
    
    # Grand total
    result['grand_total'] = filtered['VALUE'].sum()
    
    # By BU
    for bu in bu_list:
        bu_data = filtered[filtered['BU'] == bu]
        bu_total = bu_data['VALUE'].sum()
        result[f'bu_total_{bu}'] = bu_total
        
        # By SG
        if bu in service_group_dict:
            for sg in service_group_dict[bu]:
                sg_data = bu_data[bu_data['SERVICE_GROUP'] == sg]
                sg_total = sg_data['VALUE'].sum()
                result[f'sg_total_{bu}_{sg}'] = sg_total
                
                # By Product
                products = sg_data.groupby('PRODUCT_KEY')['VALUE'].sum()
                for product_key, value in products.items():
                    result[f'product_{bu}_{sg}_{product_key}'] = value
    
    return result


def calculate_summary_row_glgroup(
    self,
    label: str,
    bu_list: List[str],
    service_group_dict: Dict[str, List[str]],
    all_row_data: Dict[str, Dict]
) -> Dict[str, float]:
    """
    Calculate summary rows for GLGROUP
    
    Handles special formulas:
    - "sum_group_1": Sum all items under "1 รวมรายได้"
    - "sum_group_2": Sum all items under "2 รวมค่าใช้จ่าย"
    - "sum_service_revenue": Revenue from services
    - "total_revenue": Total revenue
    - "ebitda": EBITDA calculation
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
        # Sum all revenue items
        revenue_labels = [
            "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน",
            "- รายได้กลุ่มธุรกิจโทรศัพท์ประจำที่และบรอดแบนด์",
            "- รายได้กลุ่มธุรกิจโทรศัพท์เคลื่อนที่",
            "- รายได้กลุ่มธุรกิจวงจรระหว่างประเทศ",
            "- รายได้กลุ่มธุรกิจดิจิทัล",
            "- รายได้กลุ่มธุรกิจ ICT Solution Business",
            "- รายได้จากการให้บริการอื่นที่ไม่ใช่โทรคมนาคม",
            "- รายได้จากการขาย",
            "     - ผลตอบแทนทางการเงิน",
            "     - รายได้อื่น"
        ]
        return self._sum_rows(all_row_data, revenue_labels)
    
    elif formula == "sum_group_2":
        # Sum all expense items
        expense_labels = [
            "- ค่าใช้จ่ายตอบแทนแรงงาน",
            "- ค่าสวัสดิการ",
            "- ค่าใช้จ่ายพัฒนาและฝึกอบรมบุคลากร",
            "- ค่าซ่อมแซมและบำรุงรักษาและวัสดุใช้ไป",
            "- ค่าสาธารณูปโภค",
            "- ค่าใช้จ่ายการตลาดและส่งเสริมการขาย",
            "- ค่าใช้จ่ายเผยแพร่ประชาสัมพันธ์",
            "- ค่าใช้จ่ายเกี่ยวกับการกำกับดูแลของ กสทช.",
            "- ค่าส่วนแบ่งบริการโทรคมนาคม",
            "- ค่าใช้จ่ายบริการโทรคมนาคม",
            "- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์",
            "- ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า",
            "- ค่าเช่าและค่าใช้สินทรัพย์",
            "- ต้นทุนขาย",
            "- ค่าใช้จ่ายบริการอื่น",
            "- ค่าใช้จ่ายดำเนินงานอื่น",
            "- ค่าใช้จ่ายอื่น",
            "- ต้นทุนทางการเงิน-ด้านการดำเนินงาน",
            "- ต้นทุนทางการเงิน-ด้านการจัดหาเงิน"
        ]
        return self._sum_rows(all_row_data, expense_labels)
    
    elif formula == "sum_service_revenue":
        # Service revenue only (without finance income)
        service_labels = [
            "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน",
            "- รายได้กลุ่มธุรกิจโทรศัพท์ประจำที่และบรอดแบนด์",
            "- รายได้กลุ่มธุรกิจโทรศัพท์เคลื่อนที่",
            "- รายได้กลุ่มธุรกิจวงจรระหว่างประเทศ",
            "- รายได้กลุ่มธุรกิจดิจิทัล",
            "- รายได้กลุ่มธุรกิจ ICT Solution Business",
            "- รายได้จากการให้บริการอื่นที่ไม่ใช่โทรคมนาคม",
            "- รายได้จากการขาย"
        ]
        return self._sum_rows(all_row_data, service_labels)
    
    elif formula == "total_revenue":
        # Total revenue = "1 รวมรายได้"
        return all_row_data.get("1 รวมรายได้", {}).copy()
    
    elif formula == "total_expense_no_finance":
        # Expense without finance costs
        total_expense = all_row_data.get("2 รวมค่าใช้จ่าย", {}).copy()
        finance_op = all_row_data.get("- ต้นทุนทางการเงิน-ด้านการดำเนินงาน", {})
        finance_funding = all_row_data.get("- ต้นทุนทางการเงิน-ด้านการจัดหาเงิน", {})
        
        result = {}
        for key in total_expense:
            result[key] = total_expense.get(key, 0) - finance_op.get(key, 0) - finance_funding.get(key, 0)
        return result
    
    elif formula == "total_expense_with_finance":
        # Total expense = "2 รวมค่าใช้จ่าย"
        return all_row_data.get("2 รวมค่าใช้จ่าย", {}).copy()
    
    elif formula == "ebitda":
        # EBITDA = EBT + depreciation + amortization
        ebt = all_row_data.get("3.กำไร(ขาดทุน)ก่อนหักภาษีเงินได้ (EBT) (1)-(2)", {})
        depreciation = all_row_data.get("- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์", {})
        amortization = all_row_data.get("- ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า", {})
        
        result = {}
        all_keys = set(ebt.keys()) | set(depreciation.keys()) | set(amortization.keys())
        for key in all_keys:
            result[key] = ebt.get(key, 0) + depreciation.get(key, 0) + amortization.get(key, 0)
        return result
    
    return {}


def _sum_rows(self, all_row_data: Dict[str, Dict], labels: List[str]) -> Dict[str, float]:
    """Sum multiple rows together"""
    result = {}
    
    for label in labels:
        if label in all_row_data:
            row_data = all_row_data[label]
            for key, value in row_data.items():
                result[key] = result.get(key, 0) + value
    
    return result
