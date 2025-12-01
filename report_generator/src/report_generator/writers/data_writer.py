"""
Data Writer
Write data rows to Excel with calculations and formatting

This is the most complex module - handles:
- Writing row labels
- Getting row data from aggregator
- Calculating values for each column
- Context-aware ratio calculations (3 types)
- Product-level calculations
- Formatting based on row type
"""
from typing import List, Dict, Optional, Tuple
import pandas as pd
from ..columns.base_column_builder import ColumnDef
from ..rows.row_builder import RowDef
from src.data_loader import DataAggregator
from config.data_mapping import get_group_sub_group, is_calculated_row
from config.common_size_rows import should_have_common_size
import logging

logger = logging.getLogger(__name__)


class DataWriter:
    """Write all data rows"""
    
    def __init__(self, config, formatter):
        """
        Initialize data writer
        
        Args:
            config: ReportConfig instance
            formatter: CellFormatter instance
        """
        self.config = config
        self.formatter = formatter
    
    def write(
        self,
        ws,
        data: pd.DataFrame,
        aggregator: DataAggregator,
        columns: List[ColumnDef],
        rows: List[RowDef]
    ) -> int:
        """
        Write all data rows
        
        Args:
            ws: Worksheet
            data: Input dataframe
            aggregator: DataAggregator instance
            columns: List of ColumnDef
            rows: List of RowDef
        
        Returns:
            Next available row index
        """
        start_row = self.config.start_row + self.config.header_rows
        start_col = self.config.start_col
        
        current_row = start_row
        
        # Build BU list and service group dict
        from src.data_loader import DataProcessor
        data_processor = DataProcessor()
        bu_list = data_processor.get_unique_business_units(data)
        service_group_dict = {}
        for bu in bu_list:
            service_group_dict[bu] = data_processor.get_unique_service_groups(data, bu)
        
        # Store all row data for calculated rows
        all_row_data = {}
        
        # Track current main group context
        current_main_group_label = None
        previous_label = None
        
        # ========================================
        # PASS 1: Build all_row_data dictionary
        # ========================================
        logger.info("Pass 1: Building all row data for Common Size calculation...")
        for row_def in rows:
            label = row_def.label
            
            # Update main group context
            if row_def.level == 0:
                current_main_group_label = label
                logger.debug(f"Updated main_group_label to: {current_main_group_label}")
            
            # Skip empty rows
            if not label:
                continue
            
            # Debug: Log expense sub-item processing
            if row_def.level == 1 and "ค่าใช้จ่ายตอบแทนแรงงาน" in label:
                logger.info(f"Processing '{label}' under main_group='{current_main_group_label}'")
            
            # Get row data - detect report type
            is_ratio_row = (label == "สัดส่วนต่อรายได้" or "สัดส่วนต่อรายได้" in label)
            skip_calculation = (label == "คำนวณสัดส่วนต้นทุนบริการต่อรายได้")
            
            # Detect report type
            is_glgroup = (self.config.report_type.value == "GLGROUP")
            
            if skip_calculation:
                row_data = {}
            elif is_ratio_row:
                # Context-aware ratio calculation (COSTTYPE only)
                ratio_type = self._get_ratio_type(previous_label)
                row_data = aggregator._calculate_ratio_by_type(
                    ratio_type,
                    all_row_data,
                    bu_list,
                    service_group_dict
                )
            elif is_glgroup:
                # GLGROUP methods
                from config.data_mapping_glgroup import is_calculated_row_glgroup
                is_calc = is_calculated_row_glgroup(label)
                if is_calc:
                    row_data = aggregator.calculate_summary_row_glgroup(
                        label,
                        bu_list,
                        service_group_dict,
                        all_row_data
                    )
                else:
                    row_data = aggregator.get_row_data_glgroup(
                        label,
                        bu_list,
                        service_group_dict
                    )
            elif is_calculated_row(label):
                # Calculated row (COSTTYPE)
                row_data = aggregator.calculate_summary_row(
                    label,
                    bu_list,
                    service_group_dict,
                    all_row_data
                )
            else:
                # Regular data row (COSTTYPE)
                row_data = aggregator.get_row_data(
                    label,
                    current_main_group_label,
                    bu_list,
                    service_group_dict
                )
            
            # Store row data
            # For sub-items (level 1), use composite key to avoid collision
            if row_def.level == 1 and current_main_group_label:
                storage_key = f"{current_main_group_label}|{label}"
                all_row_data[storage_key] = row_data
            else:
                all_row_data[label] = row_data
            previous_label = label
        
        logger.info(f"Pass 1 complete: Built {len(all_row_data)} rows of data")
        
        # ========================================
        # PASS 2: Write all rows to Excel
        # ========================================
        logger.info("Pass 2: Writing data to Excel...")
        current_row = start_row
        current_main_group_label = None
        previous_label = None
        
        # Write each row
        for row_def in rows:
            label = row_def.label
            
            # Update main group context
            if row_def.level == 0:
                current_main_group_label = label
            
            # Handle empty rows
            if not label:
                current_row += 1
                continue
            
            # Write label cell
            self._write_label_cell(
                ws,
                label,
                row_def,
                current_row,
                start_col
            )
            
            # Get row data from pre-built all_row_data (Pass 1)
            # For sub-items (level 1), use composite key
            if row_def.level == 1 and current_main_group_label:
                lookup_key = f"{current_main_group_label}|{label}"
                row_data = all_row_data.get(lookup_key, {})
            else:
                row_data = all_row_data.get(label, {})
            
            # Detect skip calculation and ratio row
            skip_calculation = (label == "คำนวณสัดส่วนต้นทุนบริการต่อรายได้")
            is_ratio_row = ("สัดส่วนต่อรายได้" in label)
            
            # Write data cells (skip if skip_calculation)
            if not skip_calculation:
                self._write_data_cells(
                    ws,
                    columns,
                    row_data,
                    row_def,
                    label,
                    is_ratio_row,
                    current_row,
                    start_col,
                    aggregator,
                    all_row_data,
                    current_main_group_label,
                    previous_label
                )
            
            previous_label = label
            current_row += 1
        
        logger.info(f"Wrote {len([r for r in rows if r.label])} data rows")
        return current_row
    
    def _write_label_cell(
        self,
        ws,
        label: str,
        row_def: RowDef,
        row_index: int,
        start_col: int
    ):
        """Write label cell with formatting"""
        cell = ws.cell(row=row_index + 1, column=start_col + 1)
        
        self.formatter.format_label_cell(
            cell,
            label,
            is_bold=row_def.is_bold,
            bg_color=row_def.color
        )
    
    def _write_data_cells(
        self,
        ws,
        columns: List[ColumnDef],
        row_data: Dict[str, float],
        row_def: RowDef,
        label: str,
        is_ratio_row: bool,
        row_index: int,
        start_col: int,
        aggregator: DataAggregator,
        all_row_data: Dict,
        current_main_group_label: str,
        previous_label: str
    ):
        """Write all data cells for this row"""
        
        # Skip label column
        data_columns = [c for c in columns if c.col_type != 'label']

        # CRITICAL: Row 13 (COSTTYPE) - only show in GRAND_TOTAL column
        is_tax_row_costtype = (label == "13.ภาษีเงินได้นิติบุคคล")
        
        # GLGROUP special rows
        is_tax_row_glgroup = ("4.ภาษีเงินได้นิติบุคคล" in label)
        is_net_profit_row_glgroup = ("5.กำไร(ขาดทุน) สุทธิ" in label and "(" in label)
        
        for idx, col in enumerate(data_columns):
            col_index = start_col + idx + 1  # +1 for label column

            # Tax row COSTTYPE - only show in GRAND_TOTAL
            if is_tax_row_costtype and col.col_type != 'grand_total':
                cell = ws.cell(row=row_index + 1, column=col_index + 1)
                self.formatter.format_data_cell(
                    cell,
                    value=None,
                    is_bold=row_def.is_bold,
                    bg_color='A6A6A6',
                    is_percentage=False
                )
                continue
            
            # Tax row GLGROUP - only show GRAND_TOTAL and its Common Size (col.bu = None)
            if is_tax_row_glgroup:
                if col.col_type == 'grand_total':
                    # Allow grand_total to proceed normally
                    pass
                elif col.col_type == 'common_size' and col.bu is None:
                    # Allow grand total's common size to proceed normally
                    pass
                else:
                    # Gray out all other columns (including BU-specific common sizes)
                    cell = ws.cell(row=row_index + 1, column=col_index + 1)
                    self.formatter.format_data_cell(
                        cell,
                        value=None,
                        is_bold=row_def.is_bold,
                        bg_color='A6A6A6',
                        is_percentage=False
                    )
                    continue
            
            # Net Profit row GLGROUP - only show GRAND_TOTAL and its Common Size (col.bu = None)
            if is_net_profit_row_glgroup:
                if col.col_type == 'grand_total':
                    # Allow grand_total to proceed normally
                    pass
                elif col.col_type == 'common_size' and col.bu is None:
                    # Allow grand total's common size to proceed normally
                    pass
                else:
                    # Gray out all other columns (including BU-specific common sizes)
                    cell = ws.cell(row=row_index + 1, column=col_index + 1)
                    self.formatter.format_data_cell(
                        cell,
                        value=None,
                        is_bold=row_def.is_bold,
                        bg_color='A6A6A6',
                        is_percentage=False
                    )
                    continue
            
            # Get value for this cell
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
            
            # Write cell
            cell = ws.cell(row=row_index + 1, column=col_index + 1)
            
            # Determine if percentage
            is_percentage = "สัดส่วน" in label or col.col_type == 'common_size'
            
            # Special handling for None values in specific rows
            bg_color = row_def.color
            if (value is None and 
                col.col_type != 'grand_total' and 
                label == "14.กำไร(ขาดทุน) สุทธิ (12) - (13)"):
                bg_color = self.config.row_colors.get('gray_none', 'A6A6A6')
            
            self.formatter.format_data_cell(
                cell,
                value,
                is_bold=row_def.is_bold,
                bg_color=bg_color,
                is_percentage=is_percentage
            )
    
    def _get_cell_value(
        self,
        col: ColumnDef,
        row_data: Dict[str, float],
        label: str,
        is_ratio_row: bool,
        aggregator: DataAggregator,
        all_row_data: Dict,
        current_main_group_label: str,
        previous_label: str
    ) -> Optional[float]:
        """
        Get value for a specific cell

        Args:
            col: Column definition
            row_data: Row data from aggregator
            label: Row label
            is_ratio_row: Whether this is ratio row
            aggregator: DataAggregator
            all_row_data: All row data (for product calculations)
            current_main_group_label: Main group context
            previous_label: Previous row label

        Returns:
            Cell value or None
        """
        # Handle None row_data
        if row_data is None:
            return None

        col_type = col.col_type
        
        # Detect report type
        is_glgroup = (self.config.report_type.value == "GLGROUP")

        if col_type == 'grand_total':
            return row_data.get('GRAND_TOTAL', 0)

        elif col_type == 'bu_total':
            return row_data.get(f'BU_TOTAL_{col.bu}', 0)
        
        elif col_type == 'common_size':
            # Common Size column - calculate percentage of รายได้รวม
            return self._calculate_common_size(col, row_data, all_row_data, label)

        elif col_type == 'sg_total' or col_type == 'sg':
            # GLGROUP uses SG_TOTAL_{bu}_{sg}, COSTTYPE uses {bu}_{sg}
            if is_glgroup:
                return row_data.get(f'SG_TOTAL_{col.bu}_{col.service_group}', 0)
            else:
                return row_data.get(f'{col.bu}_{col.service_group}', 0)

        elif col_type == 'product':
            # Product-level value
            if is_glgroup:
                return self._get_product_value_glgroup(
                    col,
                    row_data,
                    label,
                    is_ratio_row,
                    all_row_data
                )
            else:
                return self._get_product_value(
                    col,
                    label,
                    is_ratio_row,
                    aggregator,
                    all_row_data,
                    current_main_group_label,
                    previous_label
                )

        return None
    
    def _get_product_value(
        self,
        col: ColumnDef,
        label: str,
        is_ratio_row: bool,
        aggregator: DataAggregator,
        all_row_data: Dict,
        current_main_group_label: str,
        previous_label: str
    ) -> Optional[float]:
        """
        Get product-level value
        
        For ratio rows: Calculate ratio for this specific product
        For other rows: Use aggregator.calculate_product_value()
        
        Args:
            col: Column definition
            label: Row label
            is_ratio_row: Whether this is ratio row
            aggregator: DataAggregator
            all_row_data: All row data
            current_main_group_label: Main group context
            previous_label: Previous row label
        
        Returns:
            Product value or None
        """
        product_key_str = f"{col.bu}_{col.service_group}_{col.product_key}"
        
        if is_ratio_row:
            # Calculate ratio for this specific product
            ratio_type = self._get_ratio_type(previous_label)

            if ratio_type == "total_service_cost_ratio":
                service_revenue = (all_row_data.get("รายได้บริการ") or {}).get(product_key_str, 0)
                total_cost = (all_row_data.get("     1. ต้นทุนบริการรวม") or {}).get(product_key_str, 0)
                return total_cost / service_revenue if abs(service_revenue) >= 1e-9 else None

            elif ratio_type == "service_cost_no_depreciation_ratio":
                service_revenue = (all_row_data.get("รายได้บริการ") or {}).get(product_key_str, 0)
                cost_no_dep = (all_row_data.get("     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ") or {}).get(product_key_str, 0)
                return cost_no_dep / service_revenue if abs(service_revenue) >= 1e-9 else None

            elif ratio_type == "service_cost_no_personnel_depreciation_ratio":
                service_revenue = (all_row_data.get("รายได้บริการ") or {}).get(product_key_str, 0)
                cost_no_pers_dep = (all_row_data.get("     3. ต้นทุนบริการ - ไม่รวมค่าใช้จ่ายบุคลากรและค่าเสื่อมราคาฯ") or {}).get(product_key_str, 0)
                return cost_no_pers_dep / service_revenue if abs(service_revenue) >= 1e-9 else None

            return None
        
        else:
            # Regular product value
            value = aggregator.calculate_product_value(
                label,
                col.bu,
                col.service_group,
                col.product_key,
                all_row_data,
                current_main_group_label
            )
            
            # Store product-level value for calculated rows
            if label not in all_row_data:
                all_row_data[label] = {}
            all_row_data[label][product_key_str] = value
            
            return value
    
    def _get_product_value_glgroup(
        self,
        col: ColumnDef,
        row_data: Dict[str, float],
        label: str,
        is_ratio_row: bool,
        all_row_data: Dict
    ) -> Optional[float]:
        """
        Get product-level value for GLGROUP reports
        
        For regular rows: Get value from row_data using PRODUCT_{bu}_{sg}_{product_key}
        For calculated rows: Get from row_data (already calculated by aggregator)
        
        Args:
            col: Column definition
            row_data: Row data from aggregator (for current row)
            label: Row label
            is_ratio_row: Whether this is ratio row
            all_row_data: All row data (for calculated rows)
        
        Returns:
            Product value or None
        """
        product_key_str = f"PRODUCT_{col.bu}_{col.service_group}_{col.product_key}"
        
        # ALWAYS try to get from row_data first (works for both regular and calculated rows)
        # Because calculate_summary_row_glgroup() already computed product-level values
        if row_data and product_key_str in row_data:
            value = row_data.get(product_key_str, 0)
            
            # Store for later use
            if label not in all_row_data:
                all_row_data[label] = {}
            all_row_data[label][product_key_str] = value
            
            return value
        
        # Fallback: Check if this is a calculated row that needs recalculation
        from config.data_mapping_glgroup import is_calculated_row_glgroup
        
        if is_calculated_row_glgroup(label):
            # For calculated rows that don't have value in row_data,
            # try to calculate from component rows
            return self._calculate_product_value_glgroup(
                col, label, all_row_data
            )
        else:
            # Regular data row - get from row_data (default 0 if not found)
            value = row_data.get(product_key_str, 0) if row_data else 0
            
            # Store product-level value for calculated rows
            if label not in all_row_data:
                all_row_data[label] = {}
            all_row_data[label][product_key_str] = value
            
            return value
    
    def _calculate_product_value_glgroup(
        self,
        col: ColumnDef,
        label: str,
        all_row_data: Dict
    ) -> Optional[float]:
        """
        Calculate product-level value for GLGROUP calculated rows
        
        Args:
            col: Column definition
            label: Row label (calculated row)
            all_row_data: All row data
        
        Returns:
            Calculated value or 0
        """
        from config.row_order_glgroup import ROW_ORDER_GLGROUP
        
        product_key_str = f"PRODUCT_{col.bu}_{col.service_group}_{col.product_key}"
        
        # Find formula for this row
        formula = None
        for level, row_label, is_calc, calc_formula, is_bold in ROW_ORDER_GLGROUP:
            if row_label == label and is_calc:
                formula = calc_formula
                break
        
        if not formula:
            return 0
        
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
                "- ผลตอบแทนทางการเงินและรายได้อื่น"
            ]
            return self._sum_product_values(all_row_data, revenue_labels, product_key_str)
        
        elif formula == "sum_group_2":
            # Sum all expense items
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
            return self._sum_product_values(all_row_data, expense_labels, product_key_str)
        
        elif formula == "sum_service_revenue":
            # Sum service revenue only (exclude finance income)
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
            return self._sum_product_values(all_row_data, service_labels, product_key_str)
        
        elif formula == "total_revenue":
            # Same as sum_group_1
            return (all_row_data.get("1 รวมรายได้") or {}).get(product_key_str, 0)
        
        elif formula == "total_expense_no_finance":
            # Total expense minus finance costs
            total = (all_row_data.get("2 รวมค่าใช้จ่าย") or {}).get(product_key_str, 0)
            fin_op = (all_row_data.get("- ต้นทุนทางการเงิน-ด้านการดำเนินงาน") or {}).get(product_key_str, 0)
            fin_fund = (all_row_data.get("- ต้นทุนทางการเงิน-ด้านการจัดหาเงิน") or {}).get(product_key_str, 0)
            return total - fin_op - fin_fund
        
        elif formula == "total_expense_with_finance":
            return (all_row_data.get("2 รวมค่าใช้จ่าย") or {}).get(product_key_str, 0)
        
        elif formula == "ebitda":
            # EBITDA = EBT + Depreciation + Amortization + Finance costs
            ebt = (all_row_data.get("3.กำไร(ขาดทุน)ก่อนหักภาษีเงินได้ (EBT) (1)-(2)") or {}).get(product_key_str, 0)
            dep = (all_row_data.get("- ค่าเสื่อมราคาและรายจ่ายตัดบัญชีสินทรัพย์") or {}).get(product_key_str, 0)
            amort = (all_row_data.get("- ค่าตัดจำหน่ายสิทธิการใช้ตามสัญญาเช่า") or {}).get(product_key_str, 0)
            fin_op = (all_row_data.get("- ต้นทุนทางการเงิน-ด้านการดำเนินงาน") or {}).get(product_key_str, 0)
            fin_fund = (all_row_data.get("- ต้นทุนทางการเงิน-ด้านการจัดหาเงิน") or {}).get(product_key_str, 0)
            return ebt + dep + amort + fin_op + fin_fund
        
        return 0
    
    def _sum_product_values(
        self,
        all_row_data: Dict,
        labels: List[str],
        product_key_str: str
    ) -> float:
        """
        Sum product values from multiple rows

        Args:
            all_row_data: All row data
            labels: Row labels to sum
            product_key_str: Product key string

        Returns:
            Sum of values
        """
        total = 0
        for label in labels:
            # Try direct key first
            row_data = all_row_data.get(label)
            if row_data is None:
                # Try composite keys (main_group|label)
                for storage_key in all_row_data:
                    if storage_key.endswith(f"|{label}"):
                        row_data = all_row_data[storage_key]
                        break

            if row_data:
                total += row_data.get(product_key_str, 0)
        return total
    
    def _get_ratio_type(self, previous_label: str) -> str:
        """
        Determine ratio calculation type based on previous row
        
        Args:
            previous_label: Previous row label
        
        Returns:
            Ratio type string
        """
        if previous_label == "     1. ต้นทุนบริการรวม":
            return "total_service_cost_ratio"
        elif previous_label == "     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ":
            return "service_cost_no_depreciation_ratio"
        elif previous_label == "     3. ต้นทุนบริการ - ไม่รวมค่าใช้จ่ายบุคลากรและค่าเสื่อมราคาฯ":
            return "service_cost_no_personnel_depreciation_ratio"
        return "total_service_cost_ratio"  # Default
    
    def _calculate_common_size(self, col: ColumnDef, row_data: Dict[str, float], all_row_data: Dict, label: str) -> Optional[float]:
        """
        Calculate Common Size (percentage of รายได้รวม)
        
        Args:
            col: Column definition
            row_data: Current row data
            all_row_data: All row data
            label: Row label
        
        Returns:
            Common size value (as decimal, e.g., 0.42 for 42%) or None
        """
        # Don't calculate common size for "สัดส่วนต่อรายได้" rows
        if "สัดส่วนต่อรายได้" in label:
            return None
        
        # CRITICAL: Rows 4 & 5 (GLGROUP ONLY) - Common Size ONLY in Grand Total column
        # For product keys (BU-specific columns), return None
        # IMPORTANT: Only apply this rule for GLGROUP reports!
        is_glgroup = (self.config.report_type.value == "GLGROUP")
        
        if is_glgroup:
            is_tax_row_glgroup = ("4.ภาษีเงินได้นิติบุคคล" in label)
            is_net_profit_row_glgroup = ("5.กำไร(ขาดทุน) สุทธิ" in label and "(" in label)
            
            if (is_tax_row_glgroup or is_net_profit_row_glgroup) and col.bu is not None:
                # This is a product key column (not Grand Total) - don't calculate common size
                return None
        
        # Get รายได้รวม (total revenue) - try both COSTTYPE and GLGROUP labels
        total_revenue_labels = [
            "รายได้รวม",      # COSTTYPE and GLGROUP (preferred)
            "1 รวมรายได้",    # GLGROUP alternative
        ]
        
        total_revenue_data = None
        for rev_label in total_revenue_labels:
            if rev_label in all_row_data:
                total_revenue_data = all_row_data[rev_label]
                break
        
        if not total_revenue_data:
            # If no total revenue data found yet, return None
            # This will happen for rows before "รายได้รวม" row
            return None
        
        # Get current row value based on column type
        if col.bu is None:
            # Grand total common size
            current_value = row_data.get('GRAND_TOTAL', 0) if row_data else 0
            total_revenue = total_revenue_data.get('GRAND_TOTAL', 0)
        else:
            # BU-specific common size
            current_value = row_data.get(f'BU_TOTAL_{col.bu}', 0) if row_data else 0
            total_revenue = total_revenue_data.get(f'BU_TOTAL_{col.bu}', 0)
        
        # Handle None values (convert to 0)
        if current_value is None:
            current_value = 0
        if total_revenue is None:
            total_revenue = 0
        
        # Calculate percentage
        if abs(total_revenue) < 1e-9:  # Avoid division by zero
            return None
        
        # Return percentage (will be formatted as % by Excel)
        result = current_value / total_revenue
        
        # Return None for zero values (will display as blank)
        if abs(result) < 1e-9:
            return None
        
        return result
