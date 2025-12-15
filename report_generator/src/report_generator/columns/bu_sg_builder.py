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
        import sys
        from pathlib import Path

        # Add config path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
        from config.satellite_config import (
            ENABLE_SATELLITE_SPLIT,
            get_satellite_service_group_names
        )

        bu_columns = []

        # 1. BU total column
        bu_columns.append(self._create_bu_total_column(bu))

        # 2. Get service groups for this BU
        service_groups = service_group_dict.get(bu, [])

        # 3. Group SATELLITE service groups (if enabled)
        satellite_groups = []
        if ENABLE_SATELLITE_SPLIT:
            satellite_sg_names = get_satellite_service_group_names()
            satellite_groups = [sg for sg in service_groups if sg in satellite_sg_names]

        satellite_inserted = False

        # 4. Build columns
        for sg in service_groups:
            # Skip SATELLITE detail groups (will add later)
            if sg in satellite_groups:
                continue

            # Create column for this SG
            col = ColumnDef(
                name=sg,
                col_type='sg',
                bu=bu,
                service_group=sg,
                product_key=None,
                product_name=None,
                width=18,
                color=self.config.bu_colors.get(bu, 'FFFFFF')
            )
            bu_columns.append(col)

            # Insert SATELLITE summary and details after 4.4.x group
            if not satellite_inserted and satellite_groups and sg.startswith('4.4'):
                # Add summary column
                bu_columns.append(self._create_satellite_summary_column(bu))

                # Add detail columns (4.5.1, 4.5.2)
                for sat_sg in sorted(satellite_groups):
                    sat_col = ColumnDef(
                        name=sat_sg,
                        col_type='sg',
                        bu=bu,
                        service_group=sat_sg,
                        product_key=None,
                        product_name=None,
                        width=18,
                        color=self.config.bu_colors.get(bu, 'FFFFFF')
                    )
                    bu_columns.append(sat_col)

                satellite_inserted = True

        return bu_columns

    def _create_satellite_summary_column(self, bu: str) -> ColumnDef:
        """
        Create virtual summary column for SATELLITE

        Args:
            bu: Business unit name

        Returns:
            ColumnDef for SATELLITE summary
        """
        import sys
        from pathlib import Path

        # Add config path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
        from config.satellite_config import SATELLITE_SUMMARY_NAME, SATELLITE_SUMMARY_ID

        return ColumnDef(
            name=SATELLITE_SUMMARY_NAME,
            col_type='satellite_summary',
            bu=bu,
            service_group=SATELLITE_SUMMARY_ID,
            product_key=None,
            product_name=None,
            width=18,
            color=self.config.bu_colors.get(bu, 'FFFFFF')
        )
    
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
