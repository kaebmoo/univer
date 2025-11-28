"""
BU Only Column Builder
Build columns with BU Total only (no SG, no Products)

Column structure: รายละเอียด | รวมทั้งสิ้น | รวม BU1 | รวม BU2 | ...

This is the SIMPLEST column structure for executive-level reports.
"""
from .base_column_builder import BaseColumnBuilder, ColumnDef
from typing import List
import pandas as pd
from src.data_loader import DataProcessor
import logging

logger = logging.getLogger(__name__)


class BUOnlyBuilder(BaseColumnBuilder):
    """
    Build columns with BU totals only
    
    Creates simple column structure:
    - รายละเอียด (Label)
    - รวมทั้งสิ้น (Grand Total)
    - รวม BU1, รวม BU2, ... (BU Totals)
    
    No Service Groups, No Products - Perfect for executive summaries.
    """
    
    def __init__(self, config):
        """Initialize builder with config"""
        super().__init__(config)
        self.data_processor = DataProcessor()
    
    def build_columns(self, data: pd.DataFrame) -> List[ColumnDef]:
        """
        Build simple BU-only column structure
        
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
        logger.info(f"Building BU-only columns for BUs: {bu_list}")
        
        # 4. For each BU - just add BU total column
        for bu in bu_list:
            columns.append(self._create_bu_total_column(bu))
        
        logger.info(f"Built {len(columns)} columns total (BU-only structure)")
        return columns
    
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
