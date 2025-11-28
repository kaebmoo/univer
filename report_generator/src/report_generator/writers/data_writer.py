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
            
            # Get row data
            is_ratio_row = (label == "         สัดส่วนต่อรายได้")
            skip_calculation = (label == "คำนวณสัดส่วนต้นทุนบริการต่อรายได้")
            
            if skip_calculation:
                row_data = {}
            elif is_ratio_row:
                # Context-aware ratio calculation
                ratio_type = self._get_ratio_type(previous_label)
                row_data = aggregator._calculate_ratio_by_type(
                    ratio_type,
                    all_row_data,
                    bu_list,
                    service_group_dict
                )
            elif is_calculated_row(label):
                # Calculated row (sum/subtract from other rows)
                row_data = aggregator.calculate_summary_row(
                    label,
                    bu_list,
                    service_group_dict,
                    all_row_data
                )
            else:
                # Regular data row
                row_data = aggregator.get_row_data(
                    label,
                    current_main_group_label,
                    bu_list,
                    service_group_dict
                )
            
            # Store row data
            all_row_data[label] = row_data
            
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

        # CRITICAL: Row 13 - only show in GRAND_TOTAL column
        is_tax_row = (label == "13.ภาษีเงินได้นิติบุคคล")
        
        for idx, col in enumerate(data_columns):
            col_index = start_col + idx + 1  # +1 for label column

            # Skip non-grand-total columns for tax row
            if is_tax_row and col.col_type != 'grand_total':
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
            is_percentage = "สัดส่วน" in label
            
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
        col_type = col.col_type
        
        if col_type == 'grand_total':
            return row_data.get('GRAND_TOTAL', 0)
        
        elif col_type == 'bu_total':
            return row_data.get(f'BU_TOTAL_{col.bu}', 0)
        
        elif col_type == 'sg_total':
            # SG total = sum of all products in this SG
            return row_data.get(f'{col.bu}_{col.service_group}', 0)
        elif col_type == 'sg':
            # For BU+SG builder
            return row_data.get(f'{col.bu}_{col.service_group}', 0)

        elif col_type == 'product':
            # Product-level value
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
                service_revenue = all_row_data.get("รายได้บริการ", {}).get(product_key_str, 0)
                total_cost = all_row_data.get("     1. ต้นทุนบริการรวม", {}).get(product_key_str, 0)
                return total_cost / service_revenue if abs(service_revenue) >= 1e-9 else None
            
            elif ratio_type == "service_cost_no_depreciation_ratio":
                service_revenue = all_row_data.get("รายได้บริการ", {}).get(product_key_str, 0)
                cost_no_dep = all_row_data.get("     2. ต้นทุนบริการ - ค่าเสื่อมราคาฯ", {}).get(product_key_str, 0)
                return cost_no_dep / service_revenue if abs(service_revenue) >= 1e-9 else None
            
            elif ratio_type == "service_cost_no_personnel_depreciation_ratio":
                service_revenue = all_row_data.get("รายได้บริการ", {}).get(product_key_str, 0)
                cost_no_pers_dep = all_row_data.get("     3. ต้นทุนบริการ - ไม่รวมค่าใช้จ่ายบุคลากรและค่าเสื่อมราคาฯ", {}).get(product_key_str, 0)
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
