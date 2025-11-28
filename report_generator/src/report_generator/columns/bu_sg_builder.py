"""
BU + SG Column Builder
Build columns with BU Total and SG Total (no Products)

Column structure: รายละเอียด | รวมทั้งสิ้น | รวม BU | SG1 | SG2 | ...

This is for mid-level reports showing Service Group breakdown without Product details.
"""
from .base_column_builder import BaseColumnBuilder, ColumnDef
from typing import List, Dict
import pandas as pd
from src.data_loader import DataProcessor
import logging

logger = logging.getLogger(__name__)


class BUSGBuilder(BaseColumnBuilder):
    """
    Build columns with BU + SG structure (no Products)
    
    Creates column structure:
    - รายละเอียด (Label)
    - รวมทั้งสิ้น (Grand Total)
    - For each BU:
      - รวม BU (BU Total)
      - SG1, SG2, ... (Service Group columns)
    
    Multi-level headers:
    - Row 1: BU names
    - Row 2-4: SG names (merged)
    """
    
    def __init__(self, config):
        """Initialize builder with config"""
        super().__init__(config)
        self.data_processor = DataProcessor()
    
    def build_columns(self, data: pd.DataFrame) -> List[ColumnDef]:
        """
        Build BU + SG column structure
        
        Args:
            data: Input dataframe
        
        Returns:
            List of ColumnDef objects representing all columns
        """
        columns = []
        
        # 1. Label column (รายละเอียด)
        columns.append(self._create_label_column())
        
        # 2. Grand total column (รวมทั้งสิ้น)
        columns.append(self._create_grand_total_column())
        
        # 3. Get BU list
        bu_list = self.data_processor.get_unique_business_units(data)
        logger.info(f"Building BU+SG columns for BUs: {bu_list}")
        
        # 4. Build service group dict
        service_group_dict = {}
        for bu in bu_list:
            service_group_dict[bu] = self.data_processor.get_unique_service_groups(data, bu)
        
        # 5. For each BU
        for bu in bu_list:
            bu_columns = self._build_bu_columns(bu, service_group_dict)
            columns.extend(bu_columns)
        
        logger.info(f"Built {len(columns)} columns total (BU+SG structure)")
        return columns
    
    def _build_bu_columns(
        self,
        bu: str,
        service_group_dict: Dict[str, List[str]]
    ) -> List[ColumnDef]:
        """
        Build all columns for a single BU
        
        Args:
            bu: Business unit name
            service_group_dict: Service group dictionary
        
        Returns:
            List of ColumnDef for this BU
        """
        bu_columns = []
        
        # 1. BU total column
        bu_columns.append(self._create_bu_total_column(bu))
        
        # 2. Service group columns (treated like SG totals)
        for sg in service_group_dict.get(bu, []):
            # Create column for this SG (no products, so it's essentially an SG total)
            col = ColumnDef(
                name=sg,  # Use SG name directly
                col_type='sg',  # New type for BU+SG builder
                bu=bu,
                service_group=sg,
                product_key=None,
                product_name=None,
                width=18,
                color=self.config.bu_colors.get(bu, 'FFFFFF')
            )
            bu_columns.append(col)
        
        return bu_columns
    
    def get_column_mapping(self, columns: List[ColumnDef]) -> dict:
        """
        Create column mapping for data writing
        
        Args:
            columns: List of ColumnDef objects
        
        Returns:
            Dict mapping column index to (type, bu, sg, product_key, product_name)
        """
        column_mapping = {}
        
        for idx, col in enumerate(columns):
            column_mapping[idx] = (
                col.col_type,
                col.bu,
                col.service_group,
                col.product_key,
                col.product_name
            )
        
        return column_mapping
