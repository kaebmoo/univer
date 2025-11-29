"""
Data Aggregator - Aggregate CSV data by GROUP/SUB_GROUP
"""
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.data_mapping import (
    get_group_sub_group,
    is_calculated_row,
    get_calculation_type,
    DEPRECIATION_CATEGORIES,
    PERSONNEL_CATEGORIES
)

logger = logging.getLogger(__name__)


class DataAggregator:
    """Aggregate data from CSV based on GROUP/SUB_GROUP structure"""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize aggregator with dataframe

        Args:
            df: Processed dataframe from CSV
        """
        self.df = df
        self._build_lookup()

    def _build_lookup(self):
        """Build fast lookup dictionary for data access"""
        self.lookup = {}
        self.lookup_with_products = {}  # Product-level lookup

        if self.df.empty:
            return

        # Group by GROUP, SUB_GROUP, BU, SERVICE_GROUP
        grouped = self.df.groupby(['GROUP', 'SUB_GROUP', 'BU', 'SERVICE_GROUP'], dropna=False)['VALUE'].sum()

        # Build nested dictionary
        for (group, sub_group, bu, service_group), value in grouped.items():
            if group not in self.lookup:
                self.lookup[group] = {}

            # Handle None/NaN sub_group
            sub_key = sub_group if pd.notna(sub_group) else "_TOTAL_"

            if sub_key not in self.lookup[group]:
                self.lookup[group][sub_key] = {}

            if bu not in self.lookup[group][sub_key]:
                self.lookup[group][sub_key][bu] = {}

            service_key = service_group if pd.notna(service_group) else "_TOTAL_"
            self.lookup[group][sub_key][bu][service_key] = value

        # Build product-level lookup
        grouped_products = self.df.groupby(['GROUP', 'SUB_GROUP', 'BU', 'SERVICE_GROUP', 'PRODUCT_KEY'], dropna=False)['VALUE'].sum()

        for (group, sub_group, bu, service_group, product_key), value in grouped_products.items():
            if group not in self.lookup_with_products:
                self.lookup_with_products[group] = {}

            sub_key = sub_group if pd.notna(sub_group) else "_TOTAL_"

            if sub_key not in self.lookup_with_products[group]:
                self.lookup_with_products[group][sub_key] = {}

            if bu not in self.lookup_with_products[group][sub_key]:
                self.lookup_with_products[group][sub_key][bu] = {}

            service_key = service_group if pd.notna(service_group) else "_TOTAL_"

            if service_key not in self.lookup_with_products[group][sub_key][bu]:
                self.lookup_with_products[group][sub_key][bu][service_key] = {}

            product_key_str = str(product_key) if pd.notna(product_key) else "_TOTAL_"
            self.lookup_with_products[group][sub_key][bu][service_key][product_key_str] = value

        logger.info(f"Built lookup with {len(self.lookup)} groups, {len(self.lookup_with_products)} groups with products")

    def get_value(
        self,
        group: Optional[str],
        sub_group: Optional[str],
        bu: Optional[str] = None,
        service_group: Optional[str] = None
    ) -> float:
        """
        Get value for specific GROUP/SUB_GROUP/BU/SERVICE_GROUP

        Args:
            group: GROUP value
            sub_group: SUB_GROUP value (None for total)
            bu: BU value (None for total)
            service_group: SERVICE_GROUP value (None for total)

        Returns:
            Value or 0 if not found
        """
        if group is None:
            return 0

        if group not in self.lookup:
            return 0

        sub_key = sub_group if sub_group else "_TOTAL_"
        if sub_key not in self.lookup[group]:
            # If specific sub_group not found, try to sum all sub_groups
            if sub_group is None:
                return self._sum_all_subgroups(group, bu, service_group)
            return 0

        if bu is None:
            # Sum across all BUs
            return self._sum_all_bus(group, sub_key, service_group)

        if bu not in self.lookup[group][sub_key]:
            return 0

        if service_group is None:
            # Sum across all service groups
            return sum(self.lookup[group][sub_key][bu].values())

        service_key = service_group if service_group else "_TOTAL_"
        return self.lookup[group][sub_key][bu].get(service_key, 0)

    def _sum_all_subgroups(
        self,
        group: str,
        bu: Optional[str] = None,
        service_group: Optional[str] = None
    ) -> float:
        """Sum all sub-groups for a GROUP"""
        total = 0
        if group in self.lookup:
            for sub_key in self.lookup[group]:
                if bu is None:
                    total += self._sum_all_bus(group, sub_key, service_group)
                else:
                    if bu in self.lookup[group][sub_key]:
                        if service_group is None:
                            total += sum(self.lookup[group][sub_key][bu].values())
                        else:
                            service_key = service_group if service_group else "_TOTAL_"
                            total += self.lookup[group][sub_key][bu].get(service_key, 0)
        return total

    def _sum_all_bus(
        self,
        group: str,
        sub_key: str,
        service_group: Optional[str] = None
    ) -> float:
        """Sum all BUs for a GROUP/SUB_GROUP"""
        total = 0
        if group in self.lookup and sub_key in self.lookup[group]:
            for bu in self.lookup[group][sub_key]:
                if service_group is None:
                    total += sum(self.lookup[group][sub_key][bu].values())
                else:
                    service_key = service_group if service_group else "_TOTAL_"
                    total += self.lookup[group][sub_key][bu].get(service_key, 0)
        return total

    def get_value_by_product(
        self,
        group: Optional[str],
        sub_group: Optional[str],
        bu: Optional[str] = None,
        service_group: Optional[str] = None,
        product_key: Optional[str] = None
    ) -> float:
        """
        Get value for specific GROUP/SUB_GROUP/BU/SERVICE_GROUP/PRODUCT_KEY

        Args:
            group: GROUP value
            sub_group: SUB_GROUP value (None for total)
            bu: BU value (None for total)
            service_group: SERVICE_GROUP value (None for total)
            product_key: PRODUCT_KEY value (None for total)

        Returns:
            Value or 0 if not found
        """
        if group is None:
            return 0

        if group not in self.lookup_with_products:
            return 0

        if bu is None:
            return 0  # Product-level requires BU

        if service_group is None:
            return 0  # Product-level requires SERVICE_GROUP

        sub_key = sub_group if sub_group else "_TOTAL_"

        # If sub_key not found, sum across all sub_groups
        if sub_key not in self.lookup_with_products[group]:
            if sub_group is None:
                # Sum all sub-groups for this GROUP
                total = 0
                for sub_k in self.lookup_with_products[group]:
                    if bu in self.lookup_with_products[group][sub_k]:
                        service_key = service_group if service_group else "_TOTAL_"
                        if service_key in self.lookup_with_products[group][sub_k][bu]:
                            if product_key is None:
                                # Sum all products
                                total += sum(self.lookup_with_products[group][sub_k][bu][service_key].values())
                            else:
                                product_key_str = str(product_key)
                                total += self.lookup_with_products[group][sub_k][bu][service_key].get(product_key_str, 0)
                return total
            return 0

        if bu not in self.lookup_with_products[group][sub_key]:
            return 0

        service_key = service_group if service_group else "_TOTAL_"
        if service_key not in self.lookup_with_products[group][sub_key][bu]:
            return 0

        if product_key is None:
            # Sum all products
            return sum(self.lookup_with_products[group][sub_key][bu][service_key].values())

        product_key_str = str(product_key)
        return self.lookup_with_products[group][sub_key][bu][service_key].get(product_key_str, 0)

    def get_row_data(
        self,
        row_label: str,
        main_group_label: str,
        bu_list: List[str],
        service_group_dict: Dict[str, List[str]]
    ) -> Dict[str, float]:
        """
        Get all column values for a row

        Args:
            row_label: Row label
            main_group_label: The label of the current main group (context).
            bu_list: List of BUs
            service_group_dict: Dict mapping BU to list of service groups

        Returns:
            Dict mapping column identifiers to values
        """
        result = {}

        # Check if this is a calculated row
        if is_calculated_row(row_label):
            # Will be handled by calculator
            return result

        # Get GROUP and SUB_GROUP for this row, using context
        group, sub_group = get_group_sub_group(row_label, main_group_label)

        if group is None:
            return result

        # For each BU and its service groups
        for bu in bu_list:
            # BU total
            bu_total_key = f"BU_TOTAL_{bu}"
            result[bu_total_key] = self.get_value(group, sub_group, bu, None)

            # Service groups under this BU
            service_groups = service_group_dict.get(bu, [])
            for sg in service_groups:
                sg_key = f"{bu}_{sg}"
                result[sg_key] = self.get_value(group, sub_group, bu, sg)

        # Grand total
        result["GRAND_TOTAL"] = self.get_value(group, sub_group, None, None)

        return result

    def calculate_summary_row(
        self,
        row_label: str,
        bu_list: List[str],
        service_group_dict: Dict[str, List[str]],
        all_row_data: Dict[str, Dict[str, float]],
        include_products: bool = False,
        product_dict: Optional[Dict[str, Dict[str, List[Tuple]]]] = None
    ) -> Dict[str, float]:
        """
        Calculate summary rows (EBITDA, totals, ratios)

        Args:
            row_label: Row label
            bu_list: List of BUs
            service_group_dict: Dict mapping BU to service groups
            all_row_data: All previously calculated row data
            include_products: Whether to include product-level calculations
            product_dict: Dict mapping BU -> SERVICE_GROUP -> [(PRODUCT_KEY, PRODUCT_NAME)]

        Returns:
            Dict mapping column identifiers to calculated values
        """
        calc_type = get_calculation_type(row_label)
        if not calc_type:
            return {}

        result = {}

        # Main profit/loss calculations
        if calc_type == "gross_profit":
            # 3 = 1 - 2
            revenue_data = all_row_data.get("1.รายได้", {})
            cost_data = all_row_data.get("2.ต้นทุนบริการและต้นทุนขาย :", {})
            for key in revenue_data:
                result[key] = revenue_data.get(key, 0) - cost_data.get(key, 0)
            return result

        elif calc_type == "profit_after_selling":
            # 5 = 3 - 4
            gross_profit = all_row_data.get("3.กำไร(ขาดทุน)ขั้นต้นจากการดำเนินงาน (1) - (2)", {})
            selling_expense = all_row_data.get("4.ค่าใช้จ่ายขายและการตลาด :", {})
            for key in gross_profit:
                result[key] = gross_profit.get(key, 0) - selling_expense.get(key, 0)
            return result

        elif calc_type == "profit_before_finance":
            # 8 = 5 - 6 - 7
            profit5 = all_row_data.get("5.กำไร(ขาดทุน)หลังหักค่าใช้จ่ายขายและการตลาด (3) - (4)", {})
            admin_expense = all_row_data.get("6.ค่าใช้จ่ายบริหารและสนับสนุน :", {})
            finance_operating = all_row_data.get("7.ต้นทุนทางการเงิน-ด้านการดำเนินงาน", {})
            for key in profit5:
                result[key] = profit5.get(key, 0) - admin_expense.get(key, 0) - finance_operating.get(key, 0)
            return result

        elif calc_type == "ebt":
            # 12 = 8 + 9 - 10 - 11
            profit8 = all_row_data.get("8.กำไร(ขาดทุน)ก่อนต้นทุนจัดหาเงิน รายได้อื่นและค่าใช้จ่ายอื่น (5) - (6) - (7)", {})
            financial_income = all_row_data.get("9.ผลตอบแทนทางการเงินและรายได้อื่น", {})
            other_expense = all_row_data.get("10.ค่าใช้จ่ายอื่น", {})
            finance_funding = all_row_data.get("11.ต้นทุนทางการเงิน-ด้านการจัดหาเงิน", {})
            for key in profit8:
                result[key] = profit8.get(key, 0) + financial_income.get(key, 0) - other_expense.get(key, 0) - finance_funding.get(key, 0)
            return result

        elif calc_type == "net_profit":
            # 14 = 12 - 13
            # Net profit is only calculated at GRAND_TOTAL level
            # For BU_TOTAL and SG columns, return None
            ebt = all_row_data.get("12.กำไร(ขาดทุน)ก่อนหักภาษีเงินได้ (EBT) (8) + (9) - (10) - (11)", {})
            tax = all_row_data.get("13.ภาษีเงินได้นิติบุคคล", {})
            for key in ebt:
                # Only calculate for GRAND_TOTAL
                if key == "GRAND_TOTAL":
                    result[key] = ebt.get(key, 0) - tax.get(key, 0)
                else:
                    result[key] = None  # Will be displayed with gray background
            return result

        elif calc_type == "sum_revenue":
            # Sum all revenue (GROUP = 01 + 09)
            groups = ["01.รายได้", "09.ผลตอบแทนทางการเงินและรายได้อื่น"]
            return self._sum_multiple_groups(groups, bu_list, service_group_dict)

        elif calc_type == "sum_expense_no_finance":
            # Sum of cost of service, selling, admin, other expenses (02, 04, 06, 10)
            groups = [
                "02.ต้นทุนบริการและต้นทุนขาย :",
                "04.ค่าใช้จ่ายขายและการตลาด :",
                "06.ค่าใช้จ่ายบริหารและสนับสนุน :",
                "10.ค่าใช้จ่ายอื่น"
            ]
            return self._sum_multiple_groups(groups, bu_list, service_group_dict)

        elif calc_type == "sum_expense_with_finance":
            # Sum including finance costs (02, 04, 06, 07, 10, 11)
            groups = [
                "02.ต้นทุนบริการและต้นทุนขาย :",
                "04.ค่าใช้จ่ายขายและการตลาด :",
                "06.ค่าใช้จ่ายบริหารและสนับสนุน :",
                "07.ต้นทุนทางการเงิน-ด้านการดำเนินงาน",
                "10.ค่าใช้จ่ายอื่น",
                "11.ต้นทุนทางการเงิน-ด้านการจัดหาเงิน"
            ]
            return self._sum_multiple_groups(groups, bu_list, service_group_dict)

        elif calc_type == "ebitda":
            # EBITDA = Revenue Total - Expense Total (excl. finance & depreciation)
            # = (01 + 09) - (02 + 04 + 06 + 10) + Depreciation
            revenue_data = all_row_data.get("รายได้รวม", {})
            expense_data = all_row_data.get("ค่าใช้จ่ายรวม (ไม่รวมต้นทุนทางการเงิน)", {})

            # Get depreciation from all expense groups (02, 04, 06)
            depreciation_data = self._sum_depreciation(bu_list, service_group_dict)

            # EBITDA = Revenue - Expense + Depreciation
            for key in revenue_data:
                result[key] = revenue_data.get(key, 0) - expense_data.get(key, 0) + depreciation_data.get(key, 0)

            return result

        elif calc_type == "service_revenue":
            # Revenue excluding other income (exclude GROUP 09)
            # This is basically GROUP 01 only
            return self._sum_by_group("01.รายได้", bu_list, service_group_dict)

        elif calc_type == "total_service_cost":
            # Total service cost (GROUP 02)
            return self._sum_by_group("02.ต้นทุนบริการและต้นทุนขาย :", bu_list, service_group_dict)

        elif calc_type == "total_service_cost_ratio":
            # Ratio = total_service_cost / service_revenue
            service_revenue = all_row_data.get("รายได้บริการ", {})
            total_cost = all_row_data.get("     1. ต้นทุนบริการรวม", {})
            return self._calculate_ratio(total_cost, service_revenue)

        elif calc_type == "service_cost_no_depreciation":
            # This is NOT "service cost minus depreciation"
            # It's "depreciation portion of service cost" (just the depreciation value itself)
            # = SUB_GROUP "12.ค่าเสื่อมราคา..." from GROUP 02 only
            depreciation_category = "12.ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์"
            group = "02.ต้นทุนบริการและต้นทุนขาย :"

            result = {}
            for bu in bu_list:
                bu_total_key = f"BU_TOTAL_{bu}"
                result[bu_total_key] = self.get_value(group, depreciation_category, bu, None)

                service_groups = service_group_dict.get(bu, [])
                for sg in service_groups:
                    sg_key = f"{bu}_{sg}"
                    result[sg_key] = self.get_value(group, depreciation_category, bu, sg)

            result["GRAND_TOTAL"] = self.get_value(group, depreciation_category, None, None)
            return result

        elif calc_type == "service_cost_no_depreciation_ratio":
            service_revenue = all_row_data.get("รายได้บริการ", {})
            cost_no_dep = all_row_data.get("     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ", {})
            return self._calculate_ratio(cost_no_dep, service_revenue)

        elif calc_type == "service_cost_no_personnel_depreciation":
            # Service cost excluding personnel and depreciation (SUB_GROUP 12 only, not 13)
            # = Total service cost - personnel costs - depreciation (12 only)
            total_cost = all_row_data.get("     1. ต้นทุนบริการรวม", {})
            personnel = self._sum_personnel(bu_list, service_group_dict, group_filter="02.ต้นทุนบริการและต้นทุนขาย :")

            # Get only SUB_GROUP 12 (not 13)
            depreciation_category = "12.ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์"
            group = "02.ต้นทุนบริการและต้นทุนขาย :"

            depreciation = {}
            for bu in bu_list:
                bu_total_key = f"BU_TOTAL_{bu}"
                depreciation[bu_total_key] = self.get_value(group, depreciation_category, bu, None)

                service_groups = service_group_dict.get(bu, [])
                for sg in service_groups:
                    sg_key = f"{bu}_{sg}"
                    depreciation[sg_key] = self.get_value(group, depreciation_category, bu, sg)

            depreciation["GRAND_TOTAL"] = self.get_value(group, depreciation_category, None, None)

            result = {}
            for key in total_cost:
                result[key] = total_cost.get(key, 0) - personnel.get(key, 0) - depreciation.get(key, 0)
            return result

        elif calc_type == "service_cost_no_personnel_depreciation_ratio":
            service_revenue = all_row_data.get("รายได้บริการ", {})
            cost_no_pers_dep = all_row_data.get("     3. ต้นทุนบริการ - ไม่รวมค่าใช้จ่ายบุคลากรและค่าเสื่อมราคาฯ", {})
            return self._calculate_ratio(cost_no_pers_dep, service_revenue)

        return result
    # ==================== GLGROUP METHODS ====================
    
    def get_row_data_glgroup(
        self,
        label: str,
        bu_list: List[str],
        service_group_dict: Dict[str, List[str]]
    ) -> Dict[str, float]:
        """
        Get row data for GLGROUP dimension
        Uses GROUP/SUB_GROUP from data directly
        Supports optional SERVICE_GROUP filter for detail rows
        """
        from config.data_mapping_glgroup import get_group_sub_group_glgroup
        
        mapping = get_group_sub_group_glgroup(label)
        
        if not mapping or len(mapping) < 2:
            return {}
        
        group = mapping[0]
        sub_group = mapping[1]
        service_group_filter = mapping[2] if len(mapping) > 2 else None
        
        if not group:
            return {}
        
        # Filter by GROUP and SUB_GROUP
        filtered = self.df[
            (self.df['GROUP'] == group) & 
            (self.df['SUB_GROUP'] == sub_group)
        ]
        
        # Additional SERVICE_GROUP filter for detail rows
        if service_group_filter:
            filtered = filtered[filtered['SERVICE_GROUP'] == service_group_filter]
        
        if len(filtered) == 0:
            logger.info(f"No data for GLGROUP: {group} / {sub_group}" + 
                       (f" / {service_group_filter}" if service_group_filter else ""))
            return {}
        
        result = {}
        result['GRAND_TOTAL'] = filtered['VALUE'].sum()
        
        for bu in bu_list:
            bu_data = filtered[filtered['BU'] == bu]
            bu_total = bu_data['VALUE'].sum()
            result[f'BU_TOTAL_{bu}'] = bu_total
            
            if bu in service_group_dict:
                for sg in service_group_dict[bu]:
                    sg_data = bu_data[bu_data['SERVICE_GROUP'] == sg]
                    sg_total = sg_data['VALUE'].sum()
                    result[f'SG_TOTAL_{bu}_{sg}'] = sg_total
                    
                    products = sg_data.groupby('PRODUCT_KEY')['VALUE'].sum()
                    for product_key, value in products.items():
                        result[f'PRODUCT_{bu}_{sg}_{product_key}'] = value
        
        return result

    def calculate_summary_row_glgroup(
        self,
        label: str,
        bu_list: List[str],
        service_group_dict: Dict[str, List[str]],
        all_row_data: Dict[str, Dict]
    ) -> Dict[str, float]:
        """Calculate summary rows for GLGROUP"""
        from config.row_order_glgroup import ROW_ORDER_GLGROUP
        
        formula = None
        for level, row_label, is_calc, calc_formula, is_bold in ROW_ORDER_GLGROUP:
            if row_label == label and is_calc:
                formula = calc_formula
                break
        
        if not formula:
            print(f"⚠️ WARNING: No formula found for calculated row: {label}")
            logger.warning(f"No formula found for calculated row: {label}")
            return {}
        
        print(f"📊 Calculating GLGROUP row '{label}' with formula: {formula}")
        logger.info(f"Calculating GLGROUP row '{label}' with formula: {formula}")
        
        print(f"  Checking formula: '{formula}'")
        print(f"  formula == 'sum_group_1': {formula == 'sum_group_1'}")
        print(f"  Type: {type(formula)}")
        
        if formula == "sum_group_1":
            print(f"  → Using sum_group_1 formula")
            revenue_labels = [
                "- รายได้กลุ่มธุรกิจโครงสร้างพื้นฐาน",
                "- รายได้กลุ่มธุรกิจโทรศัพท์ประจำที่และบรอดแบนด์",
                "- รายได้กลุ่มธุรกิจโทรศัพท์เคลื่อนที่",
                "- รายได้กลุ่มธุรกิจวงจรระหว่างประเทศ",
                "- รายได้กลุ่มธุรกิจดิจิทัล",
                "- รายได้กลุ่มธุรกิจ ICT Solution Business",
                "- รายได้จากการให้บริการอื่นที่ไม่ใช่โทรคมนาคม",
                "- รายได้จากการขาย",
                "- ผลตอบแทนทางการเงินและรายได้อื่น"  # Parent row, NOT detail rows
            ]
            # Query from database directly (this calculated row appears before detail rows)
            return self._sum_labels_from_db_glgroup(revenue_labels, bu_list, service_group_dict)
        
        elif formula == "sum_group_2":
            expense_labels = [
                "- ค่าใช้จ่ายตอบแทนแรงงาน", "- ค่าสวัสดิการ",
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
                "- ค่าเช่าและค่าใช้สินทรัพย์", "- ต้นทุนขาย",
                "- ค่าใช้จ่ายบริการอื่น",
                "- ค่าใช้จ่ายดำเนินงานอื่น", "- ค่าใช้จ่ายอื่น",
                "- ต้นทุนทางการเงิน-ด้านการดำเนินงาน",
                "- ต้นทุนทางการเงิน-ด้านการจัดหาเงิน"
            ]
            # Query from database directly (this calculated row appears before detail rows)
            return self._sum_labels_from_db_glgroup(expense_labels, bu_list, service_group_dict)
        
        elif formula == "sum_service_revenue":
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
            return self._sum_rows_glgroup(all_row_data, service_labels)
        
        elif formula == "total_revenue":
            return all_row_data.get("1 รวมรายได้", {}).copy()
        
        elif formula == "total_expense_no_finance":
            total = all_row_data.get("2 รวมค่าใช้จ่าย", {}).copy()
            op = all_row_data.get("- ต้นทุนทางการเงิน-ด้านการดำเนินงาน", {})
            fund = all_row_data.get("- ต้นทุนทางการเงิน-ด้านการจัดหาเงิน", {})
            result = {}
            for key in total:
                result[key] = total.get(key, 0) - op.get(key, 0) - fund.get(key, 0)
            return result
        
        elif formula == "total_expense_with_finance":
            return all_row_data.get("2 รวมค่าใช้จ่าย", {}).copy()
        
        elif formula == "ebitda":
            ebt = all_row_data.get("3.กำไร(ขาดทุน)ก่อนหักภาษีเงินได้ (EBT) (1)-(2)", {})
            dep = all_row_data.get("- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์", {})
            amort = all_row_data.get("- ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า", {})
            fin_op = all_row_data.get("- ต้นทุนทางการเงิน-ด้านการดำเนินงาน", {})
            fin_fund = all_row_data.get("- ต้นทุนทางการเงิน-ด้านการจัดหาเงิน", {})
            result = {}
            all_keys = set(ebt.keys()) | set(dep.keys()) | set(amort.keys()) | set(fin_op.keys()) | set(fin_fund.keys())
            for key in all_keys:
                result[key] = (ebt.get(key, 0) + dep.get(key, 0) + amort.get(key, 0) + 
                             fin_op.get(key, 0) + fin_fund.get(key, 0))
            return result
        
        return {}

    def _sum_rows_glgroup(self, all_row_data: Dict[str, Dict], labels: List[str]) -> Dict[str, float]:
        """Sum multiple rows for GLGROUP"""
        print(f"    _sum_rows_glgroup called with {len(labels)} labels")
        print(f"    all_row_data has {len(all_row_data)} keys: {list(all_row_data.keys())[:5]}...")
        result = {}
        for label in labels:
            if label in all_row_data:
                print(f"      ✓ Found '{label}' in all_row_data")
                for key, value in all_row_data[label].items():
                    result[key] = result.get(key, 0) + value
            else:
                print(f"      ✗ Missing '{label}' in all_row_data")
        print(f"    _sum_rows_glgroup result: {len(result)} keys")
        return result

    def _sum_labels_from_db_glgroup(
        self,
        labels: List[str],
        bu_list: List[str],
        service_group_dict: Dict[str, List[str]]
    ) -> Dict[str, float]:
        """
        Sum multiple labels by querying database directly (for calculated rows that appear before detail rows)

        Args:
            labels: List of row labels to sum
            bu_list: List of BUs
            service_group_dict: Dict mapping BU to service groups

        Returns:
            Dict with aggregated values at GRAND_TOTAL, BU_TOTAL, SG_TOTAL, and PRODUCT levels
        """
        from config.data_mapping_glgroup import get_group_sub_group_glgroup

        result = {}
        print(f"  _sum_labels_from_db_glgroup: Processing {len(labels)} labels")

        for label in labels:
            # Get GROUP/SUB_GROUP for this label (can be 2-tuple or 3-tuple)
            mapping = get_group_sub_group_glgroup(label)
            
            if not mapping or mapping[0] is None:
                print(f"    ✗ No mapping for label: '{label}'")
                continue
            
            group = mapping[0]
            sub_group = mapping[1] if len(mapping) > 1 else None
            
            # Skip FORMULA rows
            if group == "FORMULA":
                print(f"    ✗ Skipping FORMULA row: '{label}'")
                continue

            # Query from database
            row_data = self.get_row_data_glgroup(label, bu_list, service_group_dict)
            print(f"    ✓ Label '{label}': got {len(row_data)} keys")

            # Sum into result
            for key, value in row_data.items():
                result[key] = result.get(key, 0) + value

        print(f"  _sum_labels_from_db_glgroup: Result has {len(result)} keys")
        if result:
            sample_keys = list(result.keys())[:5]
            print(f"    Sample keys: {sample_keys}")
        
        return result

    def _sum_by_group(
        self,
        group: str,
        bu_list: List[str],
        service_group_dict: Dict[str, List[str]]
    ) -> Dict[str, float]:
        """Sum all values for a GROUP across all BUs and service groups"""
        result = {}

        for bu in bu_list:
            bu_total_key = f"BU_TOTAL_{bu}"
            result[bu_total_key] = self.get_value(group, None, bu, None)

            service_groups = service_group_dict.get(bu, [])
            for sg in service_groups:
                sg_key = f"{bu}_{sg}"
                result[sg_key] = self.get_value(group, None, bu, sg)

        result["GRAND_TOTAL"] = self.get_value(group, None, None, None)

        return result

    def _sum_multiple_groups(
        self,
        groups: List[str],
        bu_list: List[str],
        service_group_dict: Dict[str, List[str]]
    ) -> Dict[str, float]:
        """Sum across multiple GROUPs"""
        result = {}

        for group in groups:
            group_data = self._sum_by_group(group, bu_list, service_group_dict)
            for key, value in group_data.items():
                result[key] = result.get(key, 0) + value

        return result

    def _sum_depreciation(
        self,
        bu_list: List[str],
        service_group_dict: Dict[str, List[str]],
        group_filter: Optional[str] = None
    ) -> Dict[str, float]:
        """Sum depreciation categories from all expense groups or specific group"""
        result = {}

        # Groups to search for depreciation
        if group_filter:
            expense_groups = [group_filter]
        else:
            expense_groups = [
                "02.ต้นทุนบริการและต้นทุนขาย :",
                "04.ค่าใช้จ่ายขายและการตลาด :",
                "06.ค่าใช้จ่ายบริหารและสนับสนุน :"
            ]

        for dep_category in DEPRECIATION_CATEGORIES:
            for group in expense_groups:
                for bu in bu_list:
                    bu_total_key = f"BU_TOTAL_{bu}"
                    result[bu_total_key] = result.get(bu_total_key, 0) + self.get_value(group, dep_category, bu, None)

                    service_groups = service_group_dict.get(bu, [])
                    for sg in service_groups:
                        sg_key = f"{bu}_{sg}"
                        result[sg_key] = result.get(sg_key, 0) + self.get_value(group, dep_category, bu, sg)

                result["GRAND_TOTAL"] = result.get("GRAND_TOTAL", 0) + self.get_value(group, dep_category, None, None)

        return result

    def _sum_personnel(
        self,
        bu_list: List[str],
        service_group_dict: Dict[str, List[str]],
        group_filter: Optional[str] = None
    ) -> Dict[str, float]:
        """Sum personnel cost categories from all expense groups or specific group"""
        result = {}

        # Groups to search for personnel costs
        if group_filter:
            expense_groups = [group_filter]
        else:
            expense_groups = [
                "02.ต้นทุนบริการและต้นทุนขาย :",
                "04.ค่าใช้จ่ายขายและการตลาด :",
                "06.ค่าใช้จ่ายบริหารและสนับสนุน :"
            ]

        for pers_category in PERSONNEL_CATEGORIES:
            for group in expense_groups:
                for bu in bu_list:
                    bu_total_key = f"BU_TOTAL_{bu}"
                    result[bu_total_key] = result.get(bu_total_key, 0) + self.get_value(group, pers_category, bu, None)

                    service_groups = service_group_dict.get(bu, [])
                    for sg in service_groups:
                        sg_key = f"{bu}_{sg}"
                        result[sg_key] = result.get(sg_key, 0) + self.get_value(group, pers_category, bu, sg)

                result["GRAND_TOTAL"] = result.get("GRAND_TOTAL", 0) + self.get_value(group, pers_category, None, None)

        return result

    def _calculate_ratio(
        self,
        numerator_dict: Dict[str, float],
        denominator_dict: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate ratio, handling division by zero"""
        result = {}

        # Handle None inputs
        if numerator_dict is None:
            numerator_dict = {}
        if denominator_dict is None:
            denominator_dict = {}

        for key in numerator_dict:
            numerator = numerator_dict.get(key, 0)
            denominator = denominator_dict.get(key, 0)

            if abs(denominator) < 1e-9:  # Division by zero
                result[key] = None  # Will be displayed as blank or #DIV/0!
            else:
                result[key] = numerator / denominator

        return result

    def calculate_product_value(
        self,
        row_label: str,
        bu: str,
        service_group: str,
        product_key: str,
        all_row_data: Dict[str, Dict[str, float]],
        main_group_label: Optional[str] = None
    ) -> float:
        """
        Calculate value for a specific product in a calculated row

        Args:
            row_label: Row label
            bu: Business unit
            service_group: Service group
            product_key: Product key
            all_row_data: All previously calculated row data
            main_group_label: The label of the current main group (context)

        Returns:
            Calculated value for this product
        """
        # Check if this is a calculated row
        if not is_calculated_row(row_label):
            # Not a calculated row, get directly from data
            group, sub_group = get_group_sub_group(row_label, main_group_label)
            if group:
                return self.get_value_by_product(group, sub_group, bu, service_group, product_key)
            return 0

        calc_type = get_calculation_type(row_label)
        if not calc_type:
            return 0

        # Main profit/loss calculations
        if calc_type == "gross_profit":
            # 3 = 1 - 2
            product_key_str = f"{bu}_{service_group}_{product_key}"
            revenue = (all_row_data.get("1.รายได้") or {}).get(product_key_str, 0)
            cost = (all_row_data.get("2.ต้นทุนบริการและต้นทุนขาย :") or {}).get(product_key_str, 0)
            return revenue - cost

        elif calc_type == "profit_after_selling":
            # 5 = 3 - 4
            product_key_str = f"{bu}_{service_group}_{product_key}"
            gross_profit = (all_row_data.get("3.กำไร(ขาดทุน)ขั้นต้นจากการดำเนินงาน (1) - (2)") or {}).get(product_key_str, 0)
            selling_expense = (all_row_data.get("4.ค่าใช้จ่ายขายและการตลาด :") or {}).get(product_key_str, 0)
            return gross_profit - selling_expense

        elif calc_type == "profit_before_finance":
            # 8 = 5 - 6 - 7
            product_key_str = f"{bu}_{service_group}_{product_key}"
            profit5 = (all_row_data.get("5.กำไร(ขาดทุน)หลังหักค่าใช้จ่ายขายและการตลาด (3) - (4)") or {}).get(product_key_str, 0)
            admin_expense = (all_row_data.get("6.ค่าใช้จ่ายบริหารและสนับสนุน :") or {}).get(product_key_str, 0)
            finance_operating = (all_row_data.get("7.ต้นทุนทางการเงิน-ด้านการดำเนินงาน") or {}).get(product_key_str, 0)
            return profit5 - admin_expense - finance_operating

        elif calc_type == "ebt":
            # 12 = 8 + 9 - 10 - 11
            product_key_str = f"{bu}_{service_group}_{product_key}"
            profit8 = (all_row_data.get("8.กำไร(ขาดทุน)ก่อนต้นทุนจัดหาเงิน รายได้อื่นและค่าใช้จ่ายอื่น (5) - (6) - (7)") or {}).get(product_key_str, 0)
            financial_income = (all_row_data.get("9.ผลตอบแทนทางการเงินและรายได้อื่น") or {}).get(product_key_str, 0)
            other_expense = (all_row_data.get("10.ค่าใช้จ่ายอื่น") or {}).get(product_key_str, 0)
            finance_funding = (all_row_data.get("11.ต้นทุนทางการเงิน-ด้านการจัดหาเงิน") or {}).get(product_key_str, 0)
            return profit8 + financial_income - other_expense - finance_funding

        elif calc_type == "net_profit":
            # 14 = 12 - 13
            # Net profit is only calculated at GRAND_TOTAL level, not at product/BU/SG level
            # Return None to indicate this should not be displayed
            return None

        elif calc_type == "sum_revenue":
            # Sum all revenue (GROUP = 01 + 09)
            groups = ["01.รายได้", "09.ผลตอบแทนทางการเงินและรายได้อื่น"]
            total = 0
            for group in groups:
                total += self.get_value_by_product(group, None, bu, service_group, product_key)
            return total

        elif calc_type == "sum_expense_no_finance":
            # Sum of cost of service, selling, admin, other expenses (02, 04, 06, 10)
            groups = [
                "02.ต้นทุนบริการและต้นทุนขาย :",
                "04.ค่าใช้จ่ายขายและการตลาด :",
                "06.ค่าใช้จ่ายบริหารและสนับสนุน :",
                "10.ค่าใช้จ่ายอื่น"
            ]
            total = 0
            for group in groups:
                total += self.get_value_by_product(group, None, bu, service_group, product_key)
            return total

        elif calc_type == "sum_expense_with_finance":
            # Sum including finance costs (02, 04, 06, 07, 10, 11)
            groups = [
                "02.ต้นทุนบริการและต้นทุนขาย :",
                "04.ค่าใช้จ่ายขายและการตลาด :",
                "06.ค่าใช้จ่ายบริหารและสนับสนุน :",
                "07.ต้นทุนทางการเงิน-ด้านการดำเนินงาน",
                "10.ค่าใช้จ่ายอื่น",
                "11.ต้นทุนทางการเงิน-ด้านการจัดหาเงิน"
            ]
            total = 0
            for group in groups:
                total += self.get_value_by_product(group, None, bu, service_group, product_key)
            return total

        elif calc_type == "ebitda":
            # EBITDA = Revenue Total - Expense Total (excl. finance & depreciation)
            # Get revenue and expense from all_row_data
            product_key_str = f"{bu}_{service_group}_{product_key}"
            revenue_data = all_row_data.get("รายได้รวม", {})
            expense_data = all_row_data.get("ค่าใช้จ่ายรวม (ไม่รวมต้นทุนทางการเงิน)", {})

            # Get depreciation from expense groups (02, 04, 06)
            depreciation = self._sum_depreciation_by_product(bu, service_group, product_key)

            # EBITDA = Revenue - Expense + Depreciation
            revenue = revenue_data.get(product_key_str, 0)
            expense = expense_data.get(product_key_str, 0)
            return revenue - expense + depreciation

        elif calc_type == "service_revenue":
            # Revenue excluding other income (exclude GROUP 09)
            return self.get_value_by_product("01.รายได้", None, bu, service_group, product_key)

        elif calc_type == "total_service_cost":
            # Total service cost (GROUP 02)
            return self.get_value_by_product("02.ต้นทุนบริการและต้นทุนขาย :", None, bu, service_group, product_key)

        elif calc_type == "total_service_cost_ratio":
            # Ratio = total_service_cost / service_revenue
            product_key_str = f"{bu}_{service_group}_{product_key}"
            service_revenue = (all_row_data.get("รายได้บริการ") or {}).get(product_key_str, 0)
            total_cost = (all_row_data.get("     1. ต้นทุนบริการรวม") or {}).get(product_key_str, 0)

            if abs(service_revenue) < 1e-9:
                return None  # Division by zero
            return total_cost / service_revenue

        elif calc_type == "service_cost_no_depreciation":
            # Depreciation portion of service cost from GROUP 02
            depreciation_category = "12.ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์"
            group = "02.ต้นทุนบริการและต้นทุนขาย :"
            return self.get_value_by_product(group, depreciation_category, bu, service_group, product_key)

        elif calc_type == "service_cost_no_depreciation_ratio":
            product_key_str = f"{bu}_{service_group}_{product_key}"
            service_revenue = (all_row_data.get("รายได้บริการ") or {}).get(product_key_str, 0)
            cost_no_dep = (all_row_data.get("     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ") or {}).get(product_key_str, 0)

            if abs(service_revenue) < 1e-9:
                return None
            return cost_no_dep / service_revenue

        elif calc_type == "service_cost_no_personnel_depreciation":
            # Service cost excluding personnel and depreciation
            product_key_str = f"{bu}_{service_group}_{product_key}"
            total_cost = (all_row_data.get("     1. ต้นทุนบริการรวม") or {}).get(product_key_str, 0)
            personnel = self._sum_personnel_by_product(bu, service_group, product_key, "02.ต้นทุนบริการและต้นทุนขาย :")

            # Get only SUB_GROUP 12 (not 13)
            depreciation_category = "12.ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์"
            group = "02.ต้นทุนบริการและต้นทุนขาย :"
            depreciation = self.get_value_by_product(group, depreciation_category, bu, service_group, product_key)

            return total_cost - personnel - depreciation

        elif calc_type == "service_cost_no_personnel_depreciation_ratio":
            product_key_str = f"{bu}_{service_group}_{product_key}"
            service_revenue = (all_row_data.get("รายได้บริการ") or {}).get(product_key_str, 0)
            cost_no_pers_dep = (all_row_data.get("     3. ต้นทุนบริการ - ไม่รวมค่าใช้จ่ายบุคลากรและค่าเสื่อมราคาฯ") or {}).get(product_key_str, 0)

            if abs(service_revenue) < 1e-9:
                return None
            return cost_no_pers_dep / service_revenue

        return 0

    def _sum_depreciation_by_product(
        self,
        bu: str,
        service_group: str,
        product_key: str,
        group_filter: Optional[str] = None
    ) -> float:
        """Sum depreciation categories for a specific product"""
        total = 0

        # Groups to search for depreciation
        if group_filter:
            expense_groups = [group_filter]
        else:
            expense_groups = [
                "02.ต้นทุนบริการและต้นทุนขาย :",
                "04.ค่าใช้จ่ายขายและการตลาด :",
                "06.ค่าใช้จ่ายบริหารและสนับสนุน :"
            ]

        for dep_category in DEPRECIATION_CATEGORIES:
            for group in expense_groups:
                total += self.get_value_by_product(group, dep_category, bu, service_group, product_key)

        return total

    def _sum_personnel_by_product(
        self,
        bu: str,
        service_group: str,
        product_key: str,
        group_filter: Optional[str] = None
    ) -> float:
        """Sum personnel cost categories for a specific product"""
        total = 0

        # Groups to search for personnel costs
        if group_filter:
            expense_groups = [group_filter]
        else:
            expense_groups = [
                "02.ต้นทุนบริการและต้นทุนขาย :",
                "04.ค่าใช้จ่ายขายและการตลาด :",
                "06.ค่าใช้จ่ายบริหารและสนับสนุน :"
            ]

        for pers_category in PERSONNEL_CATEGORIES:
            for group in expense_groups:
                total += self.get_value_by_product(group, pers_category, bu, service_group, product_key)

        return total

    # ==================== GLGROUP METHODS ====================
    
    def get_row_data_glgroup(
        self,
        label: str,
        bu_list: List[str],
        service_group_dict: Dict[str, List[str]]
    ) -> Dict[str, float]:
        """
        Get row data for GLGROUP dimension
        Uses GROUP/SUB_GROUP from data directly
        """
        from config.data_mapping_glgroup import get_group_sub_group_glgroup
        
        mapping = get_group_sub_group_glgroup(label)
        
        if not mapping or len(mapping) < 2:
            return {}
        
        group = mapping[0]
        sub_group = mapping[1]
        service_group_filter = mapping[2] if len(mapping) > 2 else None
        
        if not group:
            return {}
        
        # Filter by GROUP and SUB_GROUP
        filtered = self.df[
            (self.df['GROUP'] == group) & 
            (self.df['SUB_GROUP'] == sub_group)
        ]
        
        # Additional SERVICE_GROUP filter for detail rows
        if service_group_filter:
            filtered = filtered[filtered['SERVICE_GROUP'] == service_group_filter]
        
        if len(filtered) == 0:
            logger.info(f"No data for GLGROUP: {group} / {sub_group}" +
                       (f" / {service_group_filter}" if service_group_filter else ""))
            return {}
        
        result = {}
        result['GRAND_TOTAL'] = filtered['VALUE'].sum()
        
        for bu in bu_list:
            bu_data = filtered[filtered['BU'] == bu]
            bu_total = bu_data['VALUE'].sum()
            result[f'BU_TOTAL_{bu}'] = bu_total
            
            if bu in service_group_dict:
                for sg in service_group_dict[bu]:
                    sg_data = bu_data[bu_data['SERVICE_GROUP'] == sg]
                    sg_total = sg_data['VALUE'].sum()
                    result[f'SG_TOTAL_{bu}_{sg}'] = sg_total
                    
                    products = sg_data.groupby('PRODUCT_KEY')['VALUE'].sum()
                    for product_key, value in products.items():
                        result[f'PRODUCT_{bu}_{sg}_{product_key}'] = value
        
        return result

    def _sum_rows_glgroup(self, all_row_data: Dict[str, Dict], labels: List[str]) -> Dict[str, float]:
        """Sum multiple rows for GLGROUP"""
        result = {}
        for label in labels:
            if label in all_row_data:
                for key, value in all_row_data[label].items():
                    result[key] = result.get(key, 0) + value
        return result

    def _calculate_ratio_by_type(
        self,
        calc_type: str,
        all_row_data: Dict[str, Dict[str, float]],
        bu_list: List[str],
        service_group_dict: Dict[str, List[str]]
    ) -> Dict[str, float]:
        """Calculate specific ratio type based on context"""
        if calc_type == "total_service_cost_ratio":
            service_revenue = all_row_data.get("รายได้บริการ") or {}
            total_cost = all_row_data.get("     1. ต้นทุนบริการรวม") or {}
            return self._calculate_ratio(total_cost, service_revenue)

        elif calc_type == "service_cost_no_depreciation_ratio":
            service_revenue = all_row_data.get("รายได้บริการ") or {}
            cost_no_dep = all_row_data.get("     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ") or {}
            return self._calculate_ratio(cost_no_dep, service_revenue)

        elif calc_type == "service_cost_no_personnel_depreciation_ratio":
            service_revenue = all_row_data.get("รายได้บริการ") or {}
            cost_no_pers_dep = all_row_data.get("     3. ต้นทุนบริการ - ไม่รวมค่าใช้จ่ายบุคลากรและค่าเสื่อมราคาฯ") or {}
            return self._calculate_ratio(cost_no_pers_dep, service_revenue)

        return {}
