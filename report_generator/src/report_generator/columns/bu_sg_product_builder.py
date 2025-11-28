"""
BU + SG + Product Column Builder
Build columns with BU Total, SG Total, and Product-level detail

This is the CURRENT working implementation from main_generator.py
Column structure: รายละเอียด | รวมทั้งสิ้น | [รวม BU | รวม SG | Product1 | Product2 ...] ...
"""
from .base_column_builder import BaseColumnBuilder, ColumnDef
from typing import List, Dict, Tuple
import pandas as pd
from src.data_loader import DataProcessor
import logging

logger = logging.getLogger(__name__)


class BUSGProductBuilder(BaseColumnBuilder):
    """
    Build columns with full detail: BU + SG + Products
    
    This implements the CURRENT working logic from main_generator.py
    Creates multi-level column headers:
    - Level 1: BU names
    - Level 2: Service Group names
    - Level 3: Product keys
    - Level 4: Product names
    """
    
    def __init__(self, config):
        """Initialize builder with config"""
        super().__init__(config)
        self.data_processor = DataProcessor()
    
    def build_columns(self, data: pd.DataFrame) -> List[ColumnDef]:
        """
        Build complete column structure
        
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
        
        # Get BU list
        bu_list = self.data_processor.get_unique_business_units(data)
        logger.info(f"Building columns for BUs: {bu_list}")
        
        # Build service group dict
        service_group_dict = {}
        for bu in bu_list:
            service_group_dict[bu] = self.data_processor.get_unique_service_groups(data, bu)
        
        # Build product dict
        product_dict = self._build_product_dict(data, bu_list, service_group_dict)
        
        # 3. For each BU
        for bu in bu_list:
            bu_columns = self._build_bu_columns(data, bu, service_group_dict, product_dict)
            columns.extend(bu_columns)
        
        logger.info(f"Built {len(columns)} columns total")
        return columns
    
    def _build_product_dict(
        self,
        data: pd.DataFrame,
        bu_list: List[str],
        service_group_dict: Dict[str, List[str]]
    ) -> Dict[str, Dict[str, List[Tuple[str, str]]]]:
        """
        Build product dictionary: {BU: {SG: [(product_key, product_name), ...]}}
        
        Args:
            data: Input dataframe
            bu_list: List of BU names
            service_group_dict: Dict of {BU: [SG list]}
        
        Returns:
            Nested dict of products
        """
        product_dict = {}
        for bu in bu_list:
            product_dict[bu] = {}
            for sg in service_group_dict[bu]:
                products = data[
                    (data['BU'] == bu) & 
                    (data['SERVICE_GROUP'] == sg)
                ][['PRODUCT_KEY', 'PRODUCT_NAME']].sort_values(
                    by='PRODUCT_KEY'
                ).drop_duplicates()
                
                product_dict[bu][sg] = list(
                    products.itertuples(index=False, name=None)
                )
        
        return product_dict
    
    def _build_bu_columns(
        self,
        data: pd.DataFrame,
        bu: str,
        service_group_dict: Dict[str, List[str]],
        product_dict: Dict[str, Dict[str, List[Tuple[str, str]]]]
    ) -> List[ColumnDef]:
        """
        Build all columns for a single BU
        
        Args:
            data: Input dataframe
            bu: Business unit name
            service_group_dict: Service group dictionary
            product_dict: Product dictionary
        
        Returns:
            List of ColumnDef for this BU
        """
        bu_columns = []
        
        # 1. BU total column
        bu_columns.append(self._create_bu_total_column(bu))
        
        # 2. Service groups for this BU
        for sg in service_group_dict.get(bu, []):
            sg_columns = self._build_sg_columns(bu, sg, product_dict)
            bu_columns.extend(sg_columns)
        
        return bu_columns
    
    def _build_sg_columns(
        self,
        bu: str,
        sg: str,
        product_dict: Dict[str, Dict[str, List[Tuple[str, str]]]]
    ) -> List[ColumnDef]:
        """
        Build columns for a single service group
        
        Args:
            bu: Business unit name
            sg: Service group name
            product_dict: Product dictionary
        
        Returns:
            List of ColumnDef for this SG
        """
        sg_columns = []
        
        # 1. SG total column (รวม SG)
        sg_columns.append(self._create_sg_total_column(bu, sg))
        
        # 2. Products in this SG
        products = product_dict.get(bu, {}).get(sg, [])
        
        for product_key, product_name in products:
            sg_columns.append(
                self._create_product_column(bu, sg, product_key, product_name)
            )
        
        return sg_columns
    
    def get_column_mapping(self, columns: List[ColumnDef]) -> Dict[int, Tuple]:
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
